# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-09-18 22:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0003_auto_20180918_1631'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='online',
        ),
    ]
