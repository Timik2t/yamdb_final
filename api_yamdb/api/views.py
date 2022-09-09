import random

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitlesFilter
from .permissions import (
    IsAdmin,
    IsModerator,
    IsOwner,
    IsReadOnly
)
from .serializers import (
    CategorySerializer,
    CommentsSerializer,
    GenreSerializer,
    RegistrationSerializer,
    ReviewSerializer,
    TitlesReadSerializer,
    TitlesWriteSerializer,
    TokenSerializer,
    UserEditSerializer,
    UserSerializer
)
from reviews.models import Category, Genre, Review, Title, User


class DescriptionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAdmin | IsReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class CategoryViewSet(DescriptionViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(DescriptionViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin | IsReadOnly]
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TitlesFilter
    ordering_fields = ('year',)
    ordering = ('-year',)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitlesReadSerializer
        return TitlesWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [(IsOwner & permissions.IsAuthenticated)
                          | IsAdmin | IsModerator | IsReadOnly]
    serializer_class = ReviewSerializer

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentsViewSet(viewsets.ModelViewSet):
    permission_classes = [(IsOwner & permissions.IsAuthenticated)
                          | IsAdmin | IsModerator | IsReadOnly]
    serializer_class = CommentsSerializer

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title__id=self.kwargs['title_id']
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    pagination_class = PageNumberPagination
    lookup_field = 'username'

    @action(
        methods=['get', 'patch', ],
        detail=False,
        url_path='me',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer,
    )
    def users_me_profile(self, request):
        if request.method == 'GET':
            return Response(
                self.get_serializer(request.user).data,
                status=status.HTTP_200_OK
            )
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegistrationAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = ''.join(random.sample(
            settings.REGULAR_CONFIRMATION_CODE,
            settings.MAX_LENGTH_CONFIRMATION_CODE
        ))
        try:
            user, _ = User.objects.get_or_create(**serializer.validated_data)
        except IntegrityError as error:
            for message in error.args:
                if 'username' in message:
                    return Response(
                        {'username': 'Пользователь с таким именем'
                                     ' уже существует.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if 'email' in message:
                    return Response(
                        {'email': 'Пользователь с такой почтой'
                                  ' уже существует.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            subject='Регистрация пользователя',
            message=f'Код подтверждения: {confirmation_code}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.data['email']],
        )
        return Response(request.data, status=status.HTTP_200_OK)


class JwtTokenAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )
        if user.confirmation_code != settings.DEFAULT_CONFIRMATION_CODE:
            if user.confirmation_code == serializer.validated_data[
                'confirmation_code'
            ]:
                access_token = RefreshToken.for_user(user).access_token
                return Response(
                    {'token': str(access_token)},
                    status=status.HTTP_200_OK,
                )
            user.confirmation_code = settings.DEFAULT_CONFIRMATION_CODE
            user.save()
        return Response(
            {'confirmation_code': 'Неверный код подтверждения'
                                  ', получите новый.'},
            status=status.HTTP_400_BAD_REQUEST
        )
