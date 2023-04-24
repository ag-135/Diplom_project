from rest_framework import viewsets
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .pagination import CustomPagination
from .permissions import AdminAuthorPermission
from recipe.models import (Tag, Ingredients, Recipes, ShoppingCart,
                           Favorite, RecipesIngredients)
from .serializers import (TagSerializer, IngredientsSerializer,
                          RecipesSerializer,
                          RecipesShortSerializer, CreateUpdateRecipeSerializer)
from .func import create_cart
from .mixins import PostDeleteMixin
from django.http import FileResponse


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


class RecipesViewSet(PostDeleteMixin, viewsets.ModelViewSet):
    pagination_class = CustomPagination
    permission_classes = [AdminAuthorPermission, ]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
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
        if self.action in ['list', 'retrieve']:
            return RecipesSerializer
        elif self.action in ['create', 'partial_update']:
            return CreateUpdateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk, model_1=Recipes,
                      model_2=ShoppingCart,
                      serial=RecipesShortSerializer):
        dict_1 = {'error': 'Данный рецепт уже добавлен в корзину'}
        dict_2 = {'error': 'Данный рецепт отсутствует в корзине'}
        return self.get_user_action(request, pk, model_1,
                                    model_2, serial, dict_1,
                                    dict_2)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        file = open('cart.txt', 'w')
        user = request.user
        recipes = RecipesIngredients.objects.filter(
            recipe__added_to_cart__user=user).select_related()
        result = create_cart(recipes)
        for key, value in result:
            line = (f'{key}-{value}\n')
            file.write(line)
        file.close()
        response = FileResponse(open('cart.txt', 'rb'),
                                as_attachment=True)
        return response

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk, model_1=Recipes,
                 model_2=Favorite,
                 serial=RecipesShortSerializer):
        dict_1 = {'error': 'Данный рецепт уже добавлен в избранные'}
        dict_2 = {'error': 'Данный рецепт не был в избранных'}
        return self.get_user_action(request, pk, model_1,
                                    model_2, serial, dict_1,
                                    dict_2)
