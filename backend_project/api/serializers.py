from rest_framework import serializers
import base64
from django.core.files.base import ContentFile
from users.models import User
from users.serializers import UserSerializer
from .models import Tag, Ingredients, Recipes, RecipesIngredients


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'hexcolor', 'slug')


class RecipesShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class RecipesIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipesIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateRecipesIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(many=False,
                                            queryset=Ingredients.objects.all()
                                            )

    class Meta:
        model = RecipesIngredients
        fields = ('id', 'amount')


class RecipesSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'image',
            'author',
            'is_favorite',
            'is_in_shopping_cart',
            'ingredients',
            'name',
            'text',
            'cooking_time')

    def get_ingredients(self, obj):
        ingredients = RecipesIngredients.objects.filter(recipe=obj).all()
        return RecipesIngredientsSerializer(ingredients, many=True).data

    def get_is_favorite(self, obj):
        print(self.context)
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorite_recipes.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_carts.filter(recipe=obj).exists()


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateRecipesIngredientsSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipes
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        print(validated_data)
        recipe = Recipes.objects.create(**validated_data)
        for ingredient in ingredients:
            ingredient_obj = ingredient['id']
            amount = ingredient['amount']
            RecipesIngredients.objects.create(
                ingredient=ingredient_obj, recipe=recipe, amount=amount
            )
        for tag in tags:
            recipe.tags.add(tag)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        print(instance)
        instance = super().update(instance, validated_data)
        print(instance)
        instance.tags.clear()
        instance.tags.clear()
        for ingredient in ingredients:
            ingredient_obj = ingredient['id']
            amount = ingredient['amount']
            RecipesIngredients.objects.create(
                ingredient=ingredient_obj, recipe=instance, amount=amount
            )
        for tag in tags:
            instance.tags.add(tag)
        return instance

    def to_representation(self, instance):
        instance = RecipesSerializer(
            instance, context={
                'request': self.context.get('request')})
        return instance.data


class UserFollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    # recipes = RecipesShortSerializer(read_only=True, many=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.following.filter(author=obj).exists()

    def get_recipes_count(self, obj):
        result = obj.recipes.count()
        return result

    def get_recipes(self, obj):
        user = self.context.get('request').user
        limit = int(self.context.get('recipes_limit'))
        recipes = Recipes.objects.filter(author__followers__user=user)[:limit]
        serializer = RecipesShortSerializer(recipes, many=True)
        return serializer.data
