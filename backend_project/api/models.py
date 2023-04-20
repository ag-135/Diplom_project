from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=250)
    hexcolor = models.CharField(max_length=250)
    slug = models.SlugField()

    def __str__(self):
        return self.slug


class Ingredients(models.Model):
    name = models.CharField(max_length=250)
    measurement_unit = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes')
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to='recipes/images/',
                              null=True,
                              blank=True,
                              default=None)
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredients, through='RecipesIngredients')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.FloatField()

    def __str__(self):
        return self.name


class RecipesIngredients(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    amount = models.IntegerField()


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers')

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes')
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='liked_users')

    def __str__(self):
        return f'{self.user.name} понравился рецепт {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts')
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='added_to_cart')
