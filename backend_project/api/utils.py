from rest_framework import serializers
import base64
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomMixin:
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
        elif request.method == 'DELETE':
            if model_2.objects.filter(
                    user=user).filter(
                    recipe=object).exists() is False:
                return Response(data=dict_2,
                                status=status.HTTP_400_BAD_REQUEST)
            model_2.objects.filter(user=user).filter(recipe=object).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
