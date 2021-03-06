#  Copyright (c) 2019 - 2020. Abhimanyu Saharan <desk.abhimanyu@gmail.com> and the Play.It contributors

# Generated by Django 3.0 on 2020-04-19 20:14

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.CharField(db_index=True, max_length=200, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=500)),
            ],
            options={
                'verbose_name': 'Artist',
                'verbose_name_plural': 'Artists',
                'ordering': ['name'],
            },
        ),
    ]
