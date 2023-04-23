from rest_framework import serializers
from .models import Profile, Post


class ProfileSerializer(serializers.ModelSerializer):
    is_followed_by_current_user = serializers.SerializerMethodField(read_only=True)
    follows = serializers.IntegerField(source="follows.count", read_only=True)
    user = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "bio",
            "profile_image",
            "is_followed_by_current_user",
            "follows",
        )

    def get_is_followed_by_current_user(self, obj):
        request = self.context.get("request")
        user = request.user
        return user.profile.follows.filter(id=obj.id).exists()


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title", "content", "image")


class ProfileDetailSerializer(ProfileSerializer):
    posts = PostSerializer(read_only=True, many=True)
    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "bio",
            "profile_image",
            "is_followed_by_current_user",
            "follows",
            "posts",
        )


class ProfileDetailForLikes(ProfileSerializer):
    user_email = serializers.EmailField(source="user.email")

    class Meta:
        model = Profile
        fields = ("user_email",)


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.EmailField(source="author.user.email")
    likes = serializers.IntegerField(source="likes.count")
    unlikes = serializers.IntegerField(source="unlikes.count")

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "content",
            "image",
            "created_at",
            "likes",
            "unlikes",
        )


class PostDetailSerializer(PostSerializer):
    likes = ProfileDetailForLikes(read_only=True, many=True)
    unlikes = ProfileDetailForLikes(read_only=True, many=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "content",
            "image",
            "created_at",
            "likes",
            "unlikes",
        )
