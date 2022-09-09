from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Comments, Genre, Review, Title, User
from reviews.validations import validate_username


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitlesReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating',)
        model = Title
        read_only_fields = fields


class TitlesWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category')
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        request = self.context['request']
        if request.method != 'POST':
            return data
        title = get_object_or_404(
            Title,
            pk=self.context['view'].kwargs.get('title_id')
        )
        if Review.objects.filter(
            title=title,
            author=request.user
        ).exists():
            raise ValidationError('Вы не можете добавить более'
                                  'одного отзыва на произведение')
        return data

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comments


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }

    def validate_username(self, value):
        return validate_username(value)


class UserEditSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        validators=[validate_username],
        max_length=settings.MAX_LENGTH_USERNAME,
        required=True,
    )
    email = serializers.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL,
        required=True,
    )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        validators=[validate_username],
        max_length=settings.MAX_LENGTH_USERNAME,
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=settings.MAX_LENGTH_CONFIRMATION_CODE,
        required=True,
    )
