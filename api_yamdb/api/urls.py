from django.urls import include, path
from rest_framework import routers

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet, get_jwt_token,
                    signup)

router = routers.DefaultRouter()
router.register(r"titles/(?P<title_id>\d+)/reviews",
                ReviewViewSet, basename="reviews")
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)
router.register("categories", CategoryViewSet, basename="categories")
router.register("genres", GenreViewSet, basename="genres")
router.register("titles", TitleViewSet, basename="titles")
router.register("users", UserViewSet)

auth_urls_v1 = [
    path('token/', get_jwt_token, name='token'),
    path('signup/', signup, name='signup')
]
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(auth_urls_v1)),
]
