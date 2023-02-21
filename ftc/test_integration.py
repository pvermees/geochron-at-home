from django.test import Client, TestCase, tag
from django.urls import reverse

import csv
import io
import json
from random import uniform

def gen_latlng():
  return [
    uniform(0.1, 0.9),
    uniform(0.1, 0.9)
  ]

def gen_latlngs(n):
  r = []
  for i in range(n):
    r.append(gen_latlng())
  return r


class CountingCase(TestCase):
  def count_grain(self, sample, grain, count):
    self.client.post(
      reverse('updateTFNResult'),
      { 'counting_res': {
        'sample_id': sample,
        'grain_num': grain,
        'ft_type': 'S',
        'track_num': count,
        'marker_latlngs': gen_latlngs(count)
      }},
      content_type='application/json'
    )

  def logout(self):
    self.client.post(reverse('logout'))

  def complete_tutorial(self):
    self.client.get(reverse('tutorial'))
    self.client.post(reverse('tutorial_result'))

  def perform_guest_count(self, grain_counts):
    self.client.get(reverse('guest_counting'))
    self.complete_tutorial()
    for ((sample, grain), count) in grain_counts.items():
      self.count_grain(sample, grain, count)
    self.logout()

  def login(self, user, password):
    login_page = reverse('account_login')
    self.client.get(login_page)
    r = self.client.post(login_page, {
      'login': user,
      'password': password
    })
    return r

  def get_total_track_count(self):
    r = self.client.post(
      reverse('getTableData'),
      { 'client_response': [
        1, 2
      ] },
      content_type='application/json'
    )
    assert(r.status_code == 200)
    j = json.loads(r.content)
    total = 0
    for [project, sample, index, ft_type, track_count, user, datetime, area] in j['aaData']:
      total += track_count
    return total


@tag('integration')
class TestGuestCounts(CountingCase):
  fixtures = [
    'users.json', 'projects.json', 'samples.json',
    'grains.json', 'images.json'
  ]

  def test_guest_counts_are_unlimited(self):
    s1count = 5
    s2count = 6
    guest_count = 5
    for i in range(guest_count):
      self.perform_guest_count({ (1, 1): s1count, (2, 1): s2count })
    self.login('admin', 'admin_password')
    total = self.get_total_track_count()
    # should get the results from sample 1 which is owned by admin
    assert(total == guest_count * s1count)
    self.logout()
    self.login('super', 'super_password')
    total = self.get_total_track_count()
    # should get the results from all samples
    assert(total == guest_count * (s1count + s2count))


@tag('integration')
class TestCountJsonDownload(CountingCase):
  fixtures = [
    'users.json', 'projects.json', 'samples.json',
    'grains.json', 'grains2.json', 'images.json',
    'results.json', 'results2.json'
  ]

  def get_json_results(self, samples=None):
    if samples is None:
      r = self.client.get(reverse('getJsonResults'))
    else:
      r = self.client.get(
        reverse('getJsonResults'),
        { 'samples[]': samples }
      )
    gs = json.loads(r.content)
    r = {}
    for g in gs:
      grain_id = g['grain']
      assert(grain_id not in r)
      r[grain_id] = g
    return r

  def sorted_results_for_grain(self, grain):
    return sorted([
      result['result'] for result in grain['results']
    ])

  def test_superuser_downloads_all_grains(self):
    self.login('super', 'super_password')
    grains = self.get_json_results()
    assert(sorted(grains.keys()) == [1, 2, 3, 4])
    assert(self.sorted_results_for_grain(grains[1]) == [3, 3])
    assert(self.sorted_results_for_grain(grains[2]) == [2, 2, 3, 3])
    assert(self.sorted_results_for_grain(grains[3]) == [2])
    assert(self.sorted_results_for_grain(grains[4]) == [2])

  def test_admin_downloads_only_her_grains(self):
    self.login('admin', 'admin_password')
    grains = self.get_json_results()
    assert(sorted(grains.keys()) == [1, 3, 4])
    assert(self.sorted_results_for_grain(grains[1]) == [3, 3])
    assert(self.sorted_results_for_grain(grains[3]) == [2])
    assert(self.sorted_results_for_grain(grains[4]) == [2])

  def test_many_samples(self):
    self.login('super', 'super_password')
    grains = self.get_json_results(['1', '2'])
    assert(sorted(grains.keys()) == [1, 2, 3, 4])
    assert(self.sorted_results_for_grain(grains[1]) == [3, 3])
    assert(self.sorted_results_for_grain(grains[2]) == [2, 2, 3, 3])
    assert(self.sorted_results_for_grain(grains[3]) == [2])
    assert(self.sorted_results_for_grain(grains[4]) == [2])

  def test_superuser_downloads_any_grains(self):
    self.login('super', 'super_password')
    grains = self.get_json_results(['2'])
    assert(sorted(grains.keys()) == [2])
    assert(self.sorted_results_for_grain(grains[2]) == [2, 2, 3, 3])

  def test_admin_cannot_download_others_results(self):
    self.login('admin', 'admin_password')
    grains = self.get_json_results(['2'])
    assert(sorted(grains.keys()) == [])

@tag('integration')
class TestCountCsvDownload(CountingCase):
  fixtures = [
    'users.json', 'projects.json', 'samples.json',
    'grains.json', 'grains2.json', 'images.json',
    'results.json', 'results2.json'
  ]

  def get_csv_results(self, samples=None):
    if samples is None:
      r = self.client.get(reverse('getCsvResults'))
    else:
      r = self.client.get(
        reverse('getCsvResults'),
        { 'samples[]': samples }
      )
    dicts = csv.DictReader(io.StringIO(r.content.decode('utf-8')))
    res = {}
    for row in dicts:
      psi = (row['project_name'], row['sample_name'], row['index'])
      c = int(row['count'])
      if psi in res:
        res[psi].append(c)
      else:
        res[psi] = [c]
    return res

  def test_superuser_downloads_csv_all_grains(self):
    self.login('super', 'super_password')
    grains = self.get_csv_results()
    assert(sorted(grains.keys()) == [
      ("proj1", "adm_samp", '1'),
      ("proj1", "adm_samp", '2'),
      ("proj1", "adm_samp", '3'),
      ("proj2", "counter_samp", '1')
    ])
    assert(sorted(grains[("proj1", "adm_samp", '1')]) == [3, 3])
    assert(sorted(grains[("proj1", "adm_samp", '2')]) == [2])
    assert(sorted(grains[("proj1", "adm_samp", '3')]) == [2])
    assert(sorted(grains[("proj2", "counter_samp", '1')]) == [2, 2, 3, 3])