from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from applications.user import views

urlpatterns = [
    path('register/email/', views.UserCreateWithEmailView.as_view(), name='user-create-with-email'),
    path('activate/<uuid:activation_code>/', views.ActivationApiView.as_view(), name='activation-api'),
    path("forgot_password/", views.ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path("recovery/<uuid:activation_code>/", views.ForgotPasswordConfirmApiView.as_view(),
         name='forgot-password-confirm'),
    path('change_password/', views.ChangePasswordApiView.as_view(), name='change-password'),

    path('login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
