# Generated by Django 5.0.6 on 2024-06-25 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Object_Detection', '0004_alter_idsproductdetails_category_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/')),
            ],
        ),
    ]
