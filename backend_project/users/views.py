from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated,
                                        AllowAny)
from .pagination import UserPagination
from .serializers import (UserCreateSerializer, UserPasswordSerializer,
                          UserSerializer)
from recipe.models import Follow
from api.serializers import UserFollowSerializer
from api.utils import CustomMixin


User = get_user_model()


class UserViewSet(CustomMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = UserPagination
    permission_classes = [AllowAny, ]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(methods=['get'],
            detail=False,
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(methods=['get', 'post'], detail=False)
    def set_password(self, request):
        user = User.objects.get(username=request.user.username)
        password = request.data.get("new_password")
        serializer = UserPasswordSerializer(user, data={"password": password})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    @action(methods=['get'],
            detail=False,
            pagination_class=UserPagination,
            permission_classes=[IsAuthenticated, ])
    def subscriptions(self, request):
        query = (User.objects.filter(followers__user=request.user)
                 .select_related().order_by('id'))
        recipes_limit = self.request.query_params.get('recipes_limit')
        pagination = self.paginate_queryset(query)
        serializer = UserFollowSerializer(pagination,
                                          many=True,
                                          context={
                                            'request': request,
                                            'recipes_limit': recipes_limit,
                                            })
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk, model_1=User,
                  model_2=Follow, serial=UserFollowSerializer):
        dict_1 = {'error': 'Нельзя подписываться на себя'}
        dict_2 = {'error': 'Вы уже подписанны на данного автора'}
        return self.get_user_action(self, request, pk, model_1,
                                    model_2, serial,
                                    dict_1, dict_2)
