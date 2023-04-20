from django_filters import rest_framework as filters
from .models import Recipes


class RecipesFilter(filters.FilterSet):
    author = filters.NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    tags = filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='in'
    )

    class Meta:
        model = Recipes
        fields = ('author', 'tags')
