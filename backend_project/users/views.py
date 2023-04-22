
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User
from .pagination import UserPagination
from .serializers import (UserCreateSerializer, UserPasswordSerializer,
                          UserSerializer)
from api.models import Follow
from api.serializers import UserFollowSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = UserPagination
    # permission_classes = [IsAuthenticatedOrReadOnly, ]

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
        print(request.user)
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
    def subscribe(self, request, pk):
        user = request.user
        author = User.objects.get(id=pk)
        if request.method == 'POST':
            if user == author:
                return Response(data={'error':
                                      'Нельзя подписываться на себя'})
            elif Follow.objects.filter(user=user, author=author).exists():
                return Response(data={'error':
                                      'Вы уже подписанны на данного автора'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, author=author)
            serializer = UserFollowSerializer(author, context={'request':
                                                               request})
            return Response(serializer.data)
        elif request.method == 'DELETE':
            if (Follow.objects.filter(user=user, author=author).
               exists()) is False:
                return Response(data={'error':
                                      'Вы не были подписанны на автора'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_200_OK)
