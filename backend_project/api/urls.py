from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet

from .views import IngredientsViewSet, RecipesViewSet, TagViewSet

router = DefaultRouter()

router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'users', UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
