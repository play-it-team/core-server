#  Copyright (c) 2019 - 2020. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

# Generated by Django 3.0 on 2020-04-19 20:14

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Continent',
            fields=[
                ('code', models.CharField(db_index=True, max_length=2, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=64)),
            ],
            options={
                'verbose_name': 'Continent',
                'verbose_name_plural': 'Continents',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.CharField(db_index=True, max_length=64, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=64)),
                ('code', models.CharField(db_index=True, max_length=2, unique=True)),
                ('code3', models.CharField(db_index=True, max_length=3, unique=True)),
                ('tld', models.CharField(max_length=5)),
                ('continent',
                 models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='countries',
                                   to='area.Continent')),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.CharField(db_index=True, max_length=64, primary_key=True, serialize=False)),
                ('code', models.CharField(db_index=True, max_length=64)),
                ('name', models.CharField(db_index=True, max_length=64)),
                ('asciiName', models.CharField(db_index=True, max_length=64)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='regions',
                                              to='area.Country')),
            ],
            options={
                'verbose_name': 'Region',
                'verbose_name_plural': 'Regions',
                'ordering': ['name'],
                'unique_together': {('country', 'name')},
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.CharField(db_index=True, max_length=64, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('asciiName', models.CharField(db_index=True, max_length=200)),
                ('location',
                 django.contrib.gis.db.models.fields.PointField(blank=True, db_index=True, null=True, srid=4326)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities',
                                              to='area.Country')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                             related_name='cities', to='area.Region')),
            ],
            options={
                'verbose_name': 'City',
                'verbose_name_plural': 'Cities',
                'ordering': ['name'],
                'unique_together': {('country', 'region', 'id', 'name')},
            },
        ),
    ]