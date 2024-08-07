# Generated by Django 4.1.2 on 2022-10-31 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ftc', '0005_remove_region_shift_x_remove_region_shift_y_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grain',
            name='scale_x',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grain',
            name='scale_y',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grain',
            name='shift_x',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='grain',
            name='shift_y',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='grain',
            name='stage_x',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grain',
            name='stage_y',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='image',
            unique_together={('grain', 'index', 'ft_type')},
        ),
    ]
