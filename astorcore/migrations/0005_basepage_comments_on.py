# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-16 20:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('astorcore', '0004_comment_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='basepage',
            name='comments_on',
            field=models.BooleanField(default=True),
        ),
    ]