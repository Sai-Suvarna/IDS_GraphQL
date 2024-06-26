# Generated by Django 5.0.6 on 2024-06-26 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IDSProductDetails',
            fields=[
                ('productId', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('category', models.TextField()),
                ('item', models.TextField()),
                ('description', models.TextField()),
                ('units', models.CharField(max_length=100)),
                ('thresholdValue', models.IntegerField()),
                ('images', models.JSONField(default=list)),
            ],
        ),
    ]
