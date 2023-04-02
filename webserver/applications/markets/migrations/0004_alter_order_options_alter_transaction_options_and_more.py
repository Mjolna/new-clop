# Generated by Django 4.1.7 on 2023-04-02 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0003_alter_order_options_transaction'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['created_on']},
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['-created_on']},
        ),
        migrations.RenameField(
            model_name='order',
            old_name='created_at',
            new_name='created_on',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='created',
            new_name='created_on',
        ),
    ]
