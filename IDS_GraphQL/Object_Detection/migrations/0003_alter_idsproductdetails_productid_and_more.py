# Generated by Django 5.0.6 on 2024-06-24 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Object_Detection', '0002_idsproductdetails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idsproductdetails',
            name='productId',
            field=models.CharField(max_length=20, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='idsproductdetails',
            name='units',
            field=models.CharField(max_length=100),
        ),
    ]
