from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, JwtTokenAPIView, GenreViewSet,
                    TitlesViewSet, RegistrationAPIView, ReviewViewSet,
                    CommentsViewSet, UserViewSet)


app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(
    r'categories',
    CategoryViewSet,
    basename='categories'
)
router_v1.register(
    r'genres',
    GenreViewSet,
    basename='genres'
)
router_v1.register(
    r'titles',
    TitlesViewSet,
    basename='titles'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)
router_v1.register(
    r'users',
    UserViewSet,
    basename='users'
)

authorization_urls = [
    path('auth/signup/', RegistrationAPIView.as_view(), name='register'),
    path('auth/token/', JwtTokenAPIView.as_view(), name='token'),
]


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/', include(authorization_urls)),
]
