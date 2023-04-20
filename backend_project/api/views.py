from rest_framework import viewsets
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .pagination import CustomPagination
from .permissions import AdminAuthorPermission
from .models import (Tag, Ingredients, Recipes, ShoppingCart,
                     Favorite, RecipesIngredients)
from .serializers import (TagSerializer, IngredientsSerializer,
                          RecipesSerializer,
                          RecipesShortSerializer, CreateUpdateRecipeSerializer)
from .func import create_cart
from django.http import HttpResponse


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
    search_fields = ('^name',)


class RecipesViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    permission_classes = [AdminAuthorPermission, ]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # filterset_class = RecipesFilter
    filterset_fields = ('author',)

    def get_queryset(self):
        user = self.request.user

        queryset = Recipes.objects.all()
        if self.request.query_params.getlist('tags'):
            list = self.request.query_params.getlist('tags')
            queryset = queryset.filter(tags__slug__in=list).distinct()
        if self.request.query_params.get('is_favorited') == '1':
            queryset = queryset.filter(liked_users__user=user)
        if self.request.query_params.get('is_in_shopping_cart') == '1':
            queryset = queryset.filter(added_to_cart__user=user)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipesSerializer
        elif self.action == 'create' or self.action == 'partial_update':
            return CreateUpdateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        user = request.user
        pk = self.kwargs.get('pk')
        recipe = Recipes.objects.get(id=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                    user=user).filter(recipe=recipe).exists():
                return Response(data={
                                'error':
                                'Данный рецепт уже добавлен в корзину'},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipesShortSerializer(recipe)
            return Response(serializer.data)
        elif request.method == 'DELETE':
            if ShoppingCart.objects.filter(user=user).filter(
                    recipe=recipe).exists() is False:
                return Response(data={
                                'error':
                                'Данный рецепт отсутствует в корзине'},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.filter(
                user=user).filter(
                recipe=recipe).delete()

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           'filename=shopping_cart.txt')
        user = request.user
        recipes = RecipesIngredients.objects.filter(
            recipe__added_to_cart__user=user).select_related()
        result = create_cart(recipes)
        for key, value in result:
            response.write(f'{key}-{value}\n')
        return response

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        user = request.user
        pk = self.kwargs.get('pk')
        recipe = Recipes.objects.get(id=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(user=user).filter(
                    recipe=recipe).exists():
                return Response(
                    data={'error':
                          'Данный рецепт уже добавлен в избранные'},
                    status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipesShortSerializer(recipe)
            return Response(serializer.data)
        elif request.method == 'DELETE':
            if Favorite.objects.filter(user=user).filter(
                    recipe=recipe).exists() is False:
                return Response(data={'error':
                                      'Данный рецепт не был в избранных'},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.filter(user=user).filter(recipe=recipe).delete()
