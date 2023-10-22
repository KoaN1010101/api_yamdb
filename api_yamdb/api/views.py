from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title, User
from .permissions import (IsAdmin, IsAdminModeratorOwnerOrReadOnly,
                          IsAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, RegistrationSerializer,
                          ReviewSerializer, TitleListSerializer,
                          TitleSerializer, TokenSerializer, UserSerializer)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAdminModeratorOwnerOrReadOnly,
    )

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        serializer.save(title=title, author=self.request.user)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsAdminModeratorOwnerOrReadOnly,
    )

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"),
                                   title__id=self.kwargs.get('title_id'))
        serializer.save(review=review, author=self.request.user)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"),
                                   title__id=self.kwargs.get('title_id'))
        return review.comments.all()


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = "slug"
    lookup_value_regex = "[^/]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class GenreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = GenreSerializer
    lookup_field = "slug"
    lookup_value_regex = "[^/]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return TitleListSerializer
        return TitleSerializer

    def get_queryset(self):
        queryset = Title.objects.annotate(rating=Avg('reviews__score'))
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name=name)
        year = self.request.query_params.get('year')
        if year is not None:
            queryset = queryset.filter(year=year)
        genre = self.request.query_params.get('genre')
        if genre is not None:
            queryset = queryset.filter(genre__slug=genre)
        category = self.request.query_params.get('category')
        if category is not None:
            queryset = queryset.filter(category__slug=category)
        return queryset


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, _ = User.objects.get_or_create(**serializer.validated_data)
    except IntegrityError:
        return Response(
            {'username': 'Пользователь с таким именем или почтой уже есть.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Регистрация на YamDB',
        message=f"Ваш код подтверждения: {confirmation_code}",
        from_email=None,
        recipient_list=[user.email],
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User,
                             username=serializer.validated_data["username"])

    if default_token_generator.check_token(
        user, serializer.validated_data["confirmation_code"]
    ):
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    @action(
        detail=False, methods=['get', 'patch'],
        url_name='me', url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def user_information(self, request):
        if request.method == 'GET':
            return Response(
                UserSerializer(request.user).data,
                status=status.HTTP_200_OK
            )
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )
