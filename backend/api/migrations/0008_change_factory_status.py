# Generated by Django 2.2.8 on 2020-01-03 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_report_record_add_nickname_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='factory',
            name='status',
        ),
        migrations.AddField(
            model_name='factory',
            name='before_2016',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='factory',
            name='cet_report_status',
            field=models.CharField(choices=[('A', '未舉報'), ('B', '已舉報')], default='A', max_length=1),
        ),
        migrations.AlterField(
            model_name='factory',
            name='factory_type',
            field=models.CharField(blank=True, choices=[('2-1', '沖床、銑床、車床、鏜孔'), ('2-2', '焊接、鑄造、熱處理'), ('2-3', '金屬表面處理、噴漆'), ('3', '塑膠加工、射出'), ('4', '橡膠加工'), ('5', '非金屬礦物（石材）'), ('6', '食品'), ('7', '皮革'), ('8', '紡織'), ('9', '其他')], max_length=3, null=True),
        ),
    ]
