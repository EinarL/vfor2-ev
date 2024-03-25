from django.db import models
from django.contrib.auth.models import User



class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.CharField(max_length=1024)
    price = models.IntegerField(default=0)


class Image(models.Model):
    listing = models.ForeignKey(Listing, related_name='images', on_delete=models.CASCADE)
    imageURL = models.CharField(max_length=1024)


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=1024)
    upvotes = models.IntegerField(default=0)

class Reply(models.Model): # reply to a comment
    comment = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=1024)

# keeps track of which user has upvoted which comment
class Upvote(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)