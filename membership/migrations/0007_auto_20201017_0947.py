# Generated by Django 3.1 on 2020-10-17 06:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0006_auto_20201015_2336'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='subscription',
            new_name='subscription_id',
        ),
    ]