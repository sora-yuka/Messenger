from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from . import tasks
from django.shortcuts import get_object_or_404
from time import sleep

User = get_user_model()


class UserCreateWithEmailSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm']

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError("Passwords don't match")

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.create_activation_code()
        user.save()
        tasks.send_email_verification_code.delay(user.email, user.activation_code)
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        user = get_object_or_404(User, email=email)
        user.create_activation_code()
        user.save()
        tasks.send_password_recovery.delay(user.email, user.activation_code)
        sleep(3)
        user.activation_code = ""
        self.user = user
        return email


class ForgotPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=6, write_only=True, required=True)
    password_confirm = serializers.CharField(min_length=6, write_only=True, required=True)

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError("Пароли не совпадают.")

        user = get_object_or_404(User, email=attrs.get("email"))
        self.user = user
        return attrs

    def set_new_password(self):
        user = self.user
        user.password = make_password(self.validated_data.get("password"))
        user.save()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, min_length=6, write_only=True)
    new_password = serializers.CharField(required=True, min_length=6, write_only=True)
    new_password_repeat = serializers.CharField(required=True, min_length=6, write_only=True)

    def validate_old_password(self, old_password):
        user = self.context.get('request').user
        if not user.check_password(old_password):
            raise serializers.ValidationError('Старый пароль введен неверно')
        return old_password

    def validate(self, attrs):
        p1 = attrs['new_password']
        p2 = attrs['new_password_repeat']
        if p1 != p2:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def create(self, validated_data):
        user = self.context.get('request').user
        user.set_password(validated_data['new_password'])
        user.save(update_fields=['password'])
        return user



# class UserCreateWithPhoneNumberSerializer(serializers.ModelSerializer):
#     phone_number = serializers.CharField(required=True)
#     password = serializers.CharField(min_length=6, write_only=True)
#     password_confirm = serializers.CharField(min_length=6, write_only=True)
#
#     class Meta:
#         model = User
#         fields = ['phone_number', 'password', 'password_confirm']

    # def validate(self, attrs):
    #     password = attrs.get('password')
    #     password_confirm = attrs.pop('password_confirm')
    #
    #     if password != password_confirm:
    #         raise serializers.ValidationError("Passwords don't match")
    #     return attrs
    #
    # # @staticmethod
    # # def validate_phone_number(phone_number):
    # #     if not phone_number.startswith('+996'):
    # #         raise serializers.ValidationError('Ваш номер должен начинаться на +996')
    # #     if len(phone_number) != 13:
    # #         raise serializers.ValidationError('Некоректный номер телефона')
    # #     if not phone_number[1:].isdigit():
    # #         raise serializers.ValidationError('Некоректный номер телефона')
    # #     return phone_number
    #
    # def create(self, validated_data):
    #     user = User.objects.create_user(**validated_data)
    #     user.create_activation_code()
    #     user.save()
    #     tasks.send_sms_verification_code.delay(code=user.activation_code, receiver=user.phone_number)
    #     return user
