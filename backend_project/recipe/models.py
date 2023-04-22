from django.db import models
from colorfield.fields import ColorField
from users.models import User


class Tag(models.Model):

    COLOR_PALETTE = [
        ("#FFFFFF", "white", ),
        ("#000000", "black", ),
    ]

    name = models.CharField(max_length=250, verbose_name="tag's name")
    color = ColorField(samples=COLOR_PALETTE, verbose_name="tag's color")
    slug = models.SlugField(verbose_name="tag's slug")

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.slug


class Ingredients(models.Model):
    name = models.CharField(max_length=250,
                            verbose_name="ingredient's name")
    measurement_unit = models.CharField(max_length=50,
                                        verbose_name="measurement unit")

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="author's name")
    name = models.CharField(max_length=250,
                            verbose_name="recipe's name")
    image = models.ImageField(upload_to='recipes/images/',
                              null=True,
                              blank=True,
                              default=None,
                              verbose_name="recipe's image")
    text = models.TextField(verbose_name="recipe's description'")
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipesIngredients',
        verbose_name="recipe's ingredients")
    tags = models.ManyToManyField(Tag, verbose_name="recipe's tags")
    cooking_time = models.IntegerField(verbose_name="cooking time")

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class RecipesIngredients(models.Model):
    recipe = models.ForeignKey(Recipes,
                               on_delete=models.CASCADE,
                               verbose_name="recipe")
    ingredient = models.ForeignKey(Ingredients,
                                   on_delete=models.CASCADE,
                                   verbose_name="ingredient")
    amount = models.IntegerField(verbose_name="amount of ingredient")

    class Meta:
        verbose_name = "Recipe's ingredient"
        verbose_name_plural = "Recipe's ingredients"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="user")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name="author")

    class Meta:
        verbose_name = "follower's pair"
        verbose_name_plural = "follower's pairs"

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='user')
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='liked_users',
        verbose_name='recipe')

    class Meta:
        verbose_name = "favorite pair"
        verbose_name_plural = "favorite pairs"

    def __str__(self):
        return f'{self.user.name} понравился рецепт {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='whose cart')
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='added_to_cart',
        verbose_name='recipe in cart')

    class Meta:
        verbose_name = 'shopping cart'
        verbose_name_plural = 'shopping carts'
