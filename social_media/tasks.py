from social_media.models import Post, Profile

from celery import shared_task


@shared_task
def create_post_task(profile_id, post_data):
    profile = Profile.objects.get(id=profile_id)
    post_data["author"] = profile.id
    Post.objects.create(**post_data)
