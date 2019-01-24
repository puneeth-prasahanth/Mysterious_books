# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Books',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=200)),
                ('Auther', models.CharField(max_length=200)),
                ('Discription', models.TextField()),
                ('Publish_date', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
    ]
