from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import TagViewSet, IngredientsViewSet, RecipesViewSet
from users.views import UserViewSet


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
