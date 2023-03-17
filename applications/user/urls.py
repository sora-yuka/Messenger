from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from applications.user import views

urlpatterns = [
    path('register/email/', views.UserCreateWithEmailView.as_view()),
    path('activate/<uuid:activation_code>/', views.ActivationApiView.as_view()),
    path("forgot_password/", views.ForgotPasswordAPIView.as_view()),
    path("recovery/<uuid:activation_code>/", views.ForgotPasswordConfirmApiView.as_view()),
    path('change_password/', views.ChangePasswordApiView.as_view()),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]