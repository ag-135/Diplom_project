from django.contrib import admin

from .models import Ingredients, Recipes, RecipesIngredients, Tag


class RecipesIngridientsInline(admin.TabularInline):
    model = RecipesIngredients
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    inlines = (RecipesIngridientsInline,)


class IngredientsAdmin(admin.ModelAdmin):
    inlines = (RecipesIngridientsInline,)


admin.site.register(Tag)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipes, RecipeAdmin)
admin.site.register(RecipesIngredients)
