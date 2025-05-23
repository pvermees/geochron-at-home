# Generated by Django 4.2.7 on 2024-06-26 12:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ftc', '0022_sample_public'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContainedTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x1_pixels', models.IntegerField()),
                ('y1_pixels', models.IntegerField()),
                ('z1_level', models.FloatField()),
                ('x2_pixels', models.IntegerField()),
                ('y2_pixels', models.IntegerField()),
                ('z2_level', models.FloatField()),
                ('result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ftc.fissiontracknumbering')),
            ],
        ),
    ]
