# Generated by Django 2.0 on 2018-06-20 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_auto_20180620_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.ImageField(default='', upload_to='courses/%Y/%m', verbose_name='封面图'),
        ),
    ]
