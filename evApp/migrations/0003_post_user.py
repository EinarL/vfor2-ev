# Generated by Django 5.0.3 on 2024-03-17 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evApp', '0002_post_upvotes'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.CharField(default='defa', max_length=32),
            preserve_default=False,
        ),
    ]
