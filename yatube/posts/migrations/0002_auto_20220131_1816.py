# Generated by Django 2.2.6 on 2022-01-31 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(help_text='Укажите описание группы.', verbose_name='Описание группы'),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(blank=True, help_text='Укажите адрес для страницы группы. Используйте только латиницу, цифры, дефисы и знаки подчёркивания', max_length=60, unique=True, verbose_name='Адрес для страницы группы'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(help_text='Дайте название группе', max_length=200, verbose_name='Название'),
        ),
    ]
