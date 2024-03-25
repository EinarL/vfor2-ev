# Generated by Django 5.0.3 on 2024-03-17 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evApp', '0004_image_listing_delete_post_image_listing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='image',
        ),
        migrations.AddField(
            model_name='image',
            name='imageURL',
            field=models.CharField(default='https://res.cloudinary.com/dyjeuxswl/image/upload/v1710692602/6061-eBikeCommuter-MatteBlack_1_qq9yie.jpg', max_length=1024),
            preserve_default=False,
        ),
    ]
