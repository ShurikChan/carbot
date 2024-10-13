# Generated by Django 5.1.2 on 2024-10-12 09:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoodSpare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spare_part', models.TextField()),
                ('image', models.ImageField(upload_to='good-spare/')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car_app.car')),
            ],
        ),
    ]
