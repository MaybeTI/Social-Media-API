import os
import uuid

from django.utils.text import slugify
from django.db import models
from social_media_config import settings
from django.db.models.signals import post_save


def profile_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.user.email)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/profile/", filename)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        blank=True, null=True, upload_to=profile_image_file_path
    )
    follows = models.ManyToManyField(
        "self", related_name="followed_by", symmetrical=False, blank=True
    )

    def __str__(self):
        return f"{self.user.email} Profile"


def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile.objects.create(user=instance)
        user_profile.save()
        user_profile.follows.add(instance.profile)
        user_profile.save()


post_save.connect(create_profile, sender=settings.AUTH_USER_MODEL)


def post_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/post/", filename)


class Post(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="uploads/post/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(Profile, related_name="liked_by", blank=True)
    unlikes = models.ManyToManyField(Profile, related_name="unliked_by", blank=True)
