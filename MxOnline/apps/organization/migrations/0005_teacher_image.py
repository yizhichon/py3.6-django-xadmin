# Generated by Django 2.0 on 2018-06-14 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_auto_20180613_1417'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='image',
            field=models.ImageField(default='', upload_to='teacher/%Y/%m', verbose_name='头像'),
        ),
    ]