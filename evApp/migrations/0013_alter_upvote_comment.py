# Generated by Django 5.0.3 on 2024-03-26 15:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evApp', '0012_alter_upvote_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upvote',
            name='comment',
            field=models.ForeignKey(default=1000, on_delete=django.db.models.deletion.CASCADE, to='evApp.comment'),
            preserve_default=False,
        ),
    ]