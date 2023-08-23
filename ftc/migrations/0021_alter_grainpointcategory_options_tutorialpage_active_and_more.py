# Generated by Django 4.1.7 on 2023-08-21 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ftc', '0020_alter_tutorialpage_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grainpointcategory',
            options={'verbose_name': 'Grain Point Category', 'verbose_name_plural': 'Grain Point Categories'},
        ),
        migrations.AddField(
            model_name='tutorialpage',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='tutorialpage',
            name='sequence_number',
            field=models.IntegerField(default=50),
        ),
    ]