from django.urls import path
from applications.user import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('registers/email/', views.UserCreateWithEmailView.as_view()),
    path('registers/phone_number/', views.UserCreateWithPhoneNumberView.as_view()),
    path('activate/<uuid:activation_code>/', views.ActivationApiView.as_view()),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]