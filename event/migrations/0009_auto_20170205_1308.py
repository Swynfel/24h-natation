# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-05 13:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0008_user_distance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nage',
            name='backandforth',
            field=models.IntegerField(blank=True, null=True, verbose_name='Aller-Retour'),
        ),
    ]
