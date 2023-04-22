from datetime import datetime
from django.utils import timezone
from social_media.tasks import create_post_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from social_media.models import Profile, Post
from social_media.permisions_social_media import (
    IsProfileOwnerOrReadOnly,
    IsOwnerOrReadOnly,
)
from social_media.serializers import (
    ProfileSerializer,
    PostSerializer,
    ProfileDetailSerializer,
    PostListSerializer,
    PostDetailSerializer,
)
from rest_framework.permissions import IsAuthenticated


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    permission_classes = (IsAuthenticated, IsProfileOwnerOrReadOnly)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProfileDetailSerializer
        return ProfileSerializer


class FollowProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, profile_id):
        user = request.user
        profile = Profile.objects.get(id=profile_id)

        if not user.profile.follows.filter(id=profile_id).exists():
            user.profile.follows.add(profile)
            user.profile.save()
            return Response(status=status.HTTP_200_OK)

        user.profile.follows.remove(profile)
        user.profile.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UnfollowProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, profile_id):
        user = request.user
        profile = Profile.objects.get(id=profile_id)

        if user.profile.follows.filter(id=profile_id).exists():
            user.profile.follows.remove(profile)
            user.profile.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_404_NOT_FOUND)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        queryset = Post.objects.filter(
            author__in=self.request.user.profile.follows.all()
        )
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")

        if title:
            return queryset.filter(title__icontains=title)
        if author:
            return queryset.filter(author__username__icontains=author)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)

    def create(self, request, *args, **kwargs):
        scheduled_time = request.data.get("scheduled_time")
        if scheduled_time:
            # Convert the scheduled time to datetime object
            scheduled_time = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S")
            # Convert the scheduled time to timezone aware datetime object
            scheduled_time = timezone.make_aware(scheduled_time)
            # Schedule the task to create the post at the scheduled time
            create_post_task.apply_async(
                args=[request.user.profile.id, request.data], eta=scheduled_time
            )
            # Return success response
            return Response(
                {"message": "Post will be created at the scheduled time."},
                status=status.HTTP_200_OK,
            )

        # If scheduled time is not provided, create the post immediately
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class LikePostView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, post_id):
        user = request.user
        post = Post.objects.get(id=post_id)

        if post.unlikes.filter(id=user.profile.id).exists():
            post.unlikes.remove(user.profile)
            post.save()
            return Response(status=status.HTTP_200_OK)

        post.likes.add(user.profile)
        post.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UnlikePostView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, post_id):
        user = request.user
        post = Post.objects.get(id=post_id)

        if post.likes.filter(id=user.profile.id).exists():
            post.likes.remove(user.profile)
            post.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        post.unlikes.add(user.profile)
        post.save()

        return Response(status=status.HTTP_200_OK)
