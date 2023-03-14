from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from .serializers import UserCreateWithEmailSerializer, UserCreateWithPhoneNumberSerializer
from .tasks import send_email_verification_code, send_sms_verification_code

User = get_user_model()


class UserCreateWithEmailView(generics.CreateAPIView):
    serializer_class = UserCreateWithEmailSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        send_email_verification_code(user.email, user.activation_code)
        return Response({
            "msg": "Вы успешно зарегистрировались, к вам на почту отправили письмо с активацией вашего профиля"
        }, status=status.HTTP_201_CREATED)


class UserCreateWithPhoneNumberView(generics.CreateAPIView):
    serializer_class = UserCreateWithPhoneNumberSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        send_sms_verification_code(user.phone_number, user.activation_code)

        return Response({
            "msg": "Вы успешно зарегистрировались, на ваш телефон отправлено сообщение с кодом подтверждения"
        }, status=status.HTTP_201_CREATED)


class ActivationApiView(generics.ListAPIView):
    def get(self, request, activation_code):
        try:
            user = User.objects.get(activation_code=activation_code)
            user.is_active = True
            user.activation_code = ''
            user.save(update_fields=['is_active', 'activation_code'])
            return Response({'msg': 'ваш аккаунт успешно активирован'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'msg': 'некоректный код активации'})

