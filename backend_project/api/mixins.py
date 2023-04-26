from rest_framework import status
from rest_framework.response import Response


class PostDeleteMixin:
    def get_user_action(self, request, pk, model_1, model_2,
                        serial, dict_1, dict_2):
        user = request.user
        object = model_1.objects.get(id=pk)
        if request.method == 'POST':
            if model_2.objects.filter(
                    user=user).filter(
                    recipe=object).exists():
                return Response(data=dict_1,
                                status=status.HTTP_400_BAD_REQUEST)
            model_2.objects.create(user=user, recipe=object)
            serializer = serial(object)
            return Response(serializer.data)
        if model_2.objects.filter(
                user=user).filter(
                recipe=object).exists() is False:
            return Response(data=dict_2,
                            status=status.HTTP_400_BAD_REQUEST)
        model_2.objects.filter(user=user).filter(recipe=object).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
