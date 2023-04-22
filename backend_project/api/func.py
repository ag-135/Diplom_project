def create_cart(recipes):
    ing = {}
    for obj in recipes:
        key = f'{obj.ingredient.name} ({obj.ingredient.measurement_unit})'
        value = obj.amount
        if key in ing:
            ing[key] = ing[key] + value
        else:
            ing[key] = value
    return ing.items()
