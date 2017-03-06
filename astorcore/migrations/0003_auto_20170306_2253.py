# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-06 22:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('astorcore', '0002_auto_20170306_2244'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagevisit',
            name='request_method',
            field=models.CharField(default=1, max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pagevisit',
            name='user_agent',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
