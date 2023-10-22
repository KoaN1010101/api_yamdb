from django.conf import settings
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User
from .validators import username_validator


class ReviewSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(slug_field="username",
                                          read_only=True)

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")

    def validate(self, data):
        title_id = self.context["request"].parser_context["kwargs"]["title_id"]
        user = self.context["request"].user
        if self.context["request"].method == "POST":
            if user.reviews.filter(title_id=title_id).exists():
                raise serializers.ValidationError(
                    "Вы уже оставили отзыв. Нельзя оставлять отзыв дважды."
                )
        return data


class CommentSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(slug_field="username",
                                          read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "slug")
        lookup_field = "slug"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name", "slug")
        lookup_field = "slug"


class TitleListSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField()
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = ("id", "name", "year", "rating",
                  "description", "genre", "category")


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category'
        )


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=[username_validator]
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH
    )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )

    def validate_username(self, value):
        return username_validator(value)
