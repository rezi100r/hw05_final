# Generated by Django 2.2.16 on 2022-02-14 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20220214_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Добавьте картинку', upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
