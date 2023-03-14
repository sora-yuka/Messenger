from django.contrib.auth import get_user_model
from rest_framework import serializers
from . import tasks


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


class UserCreateWithPhoneNumberSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirm = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'password_confirm']

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    # @staticmethod
    # def validate_phone_number(phone_number):
    #     if not phone_number.startswith('+996'):
    #         raise serializers.ValidationError('Ваш номер должен начинаться на +996')
    #     if len(phone_number) != 13:
    #         raise serializers.ValidationError('Некоректный номер телефона')
    #     if not phone_number[1:].isdigit():
    #         raise serializers.ValidationError('Некоректный номер телефона')
    #     return phone_number

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.create_activation_code()
        user.save()
        tasks.send_sms_verification_code.delay(code=user.activation_code, receiver=user.phone_number)
        return user



