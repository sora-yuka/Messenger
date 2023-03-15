from django.urls import path
from applications.user import views

urlpatterns = [
    path('registers/email/', views.UserCreateWithEmailView.as_view()),
    path('registers/phone_number/', views.UserCreateWithPhoneNumberView.as_view()),
    path('activate/<uuid:activation_code>/', views.ActivationApiView.as_view()),
]