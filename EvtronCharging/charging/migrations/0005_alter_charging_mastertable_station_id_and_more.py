# Generated by Django 4.0.3 on 2022-05-05 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charging', '0004_alter_charging_mastertable_station_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charging_mastertable',
            name='Station_ID',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='charging_transactiontable',
            name='Station_ID',
            field=models.CharField(max_length=20, null=True),
        ),
    ]