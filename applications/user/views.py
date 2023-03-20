from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import views
from datetime import datetime, timezone
from . import tasks, serializers
from .serializers import ForgotPasswordSerializer, ForgotPasswordConfirmSerializer, UserCreateWithEmailSerializer
User = get_user_model()


class UserCreateWithEmailView(views.APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserCreateWithEmailSerializer)
    def post(self, request):
        serializer = UserCreateWithEmailSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tasks.send_email_verification_code(user.email, user.activation_code)
            return Response({
                "msg": "Вы успешно зарегистрировались, к вам на почту отправили письмо с активацией вашего профиля"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordAPIView(views.APIView):
    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"msg": "Мы выслали ссылку для сброса пароля."})


class ForgotPasswordConfirmApiView(views.APIView):
    @swagger_auto_schema(request_body=ForgotPasswordConfirmSerializer)
    def post(self, request, activation_code):
        user = User.objects.get(activation_code=activation_code)
        if (datetime.now(timezone.utc) - user.created_at).total_seconds() > 86400:
            return Response(
                {"msg": "Ссылка для сброса пароля недействительна."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ForgotPasswordConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.set_new_password()
        return Response(
            {"msg": "Пароль успешно обновлен."},
            status=status.HTTP_200_OK
        )



class ActivationApiView(views.APIView):
    def get(self, request, activation_code):
        try:
            user = User.objects.get(activation_code=activation_code)
            user.is_active = True
            user.activation_code = ''
            user.save(update_fields=['is_active', 'activation_code'])
            return Response({'msg': 'ваш аккаунт успешно активирован'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'msg': 'некоректный код активации'})


class ChangePasswordApiView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.ChangePasswordSerializer
    permission_classes = [IsAuthenticated]



