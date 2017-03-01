# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-28 23:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('astorcore', '0008_externalhtmlpage_uploadpage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadpage',
            name='basepage_ptr',
        ),
        migrations.DeleteModel(
            name='ExternalHTMLPage',
        ),
        migrations.CreateModel(
            name='ExternalHTMLPage',
            fields=[
                ('basepage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='astorcore.BasePage')),
                ('abstract', models.TextField(blank=True, default='')),
                ('file', models.FileField(upload_to='.')),
            ],
            options={
                'abstract': False,
            },
            bases=('astorcore.basepage',),
        ),
        migrations.DeleteModel(
            name='UploadPage',
        ),
    ]