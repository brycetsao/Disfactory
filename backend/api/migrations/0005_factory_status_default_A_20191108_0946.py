# Generated by Django 2.2.4 on 2019-11-08 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_allow_image_factory_null_20191108_0933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='factory',
            name='status',
            field=models.CharField(choices=[('D', '已舉報'), ('F', '資料不齊'), ('A', '待審核')], default='A', max_length=1),
        ),
    ]
