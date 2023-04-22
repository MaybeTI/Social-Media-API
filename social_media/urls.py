from django.urls import path, include
from rest_framework import routers
from social_media.views import (
    FollowProfileView,
    ProfileViewSet,
    UnfollowProfileView,
    PostViewSet,
    LikePostView,
    UnlikePostView,
)


router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet, basename="profiles")
router.register("posts", PostViewSet, basename="posts")


urlpatterns = [
    path(
        "profiles/<int:profile_id>/follow/", FollowProfileView.as_view(), name="follow"
    ),
    path(
        "profiles/<int:profile_id>/unfollow/",
        UnfollowProfileView.as_view(),
        name="unfollow",
    ),
    path("posts/<int:post_id>/like/", LikePostView.as_view(), name="like"),
    path("posts/<int:post_id>/unlike/", UnlikePostView.as_view(), name="unlike"),
    path("", include(router.urls)),
]

app_name = "social_media"
