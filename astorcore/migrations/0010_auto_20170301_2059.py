# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-01 20:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('astorcore', '0009_auto_20170228_2329'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ExternalHTMLPage',
            new_name='HTMLUploadPage',
        ),
    ]