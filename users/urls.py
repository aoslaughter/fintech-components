from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter, DefaultRouter
from users.views import UserViewSet
from auth.views import LoginViewSet, RegistrationViewSet, RefreshViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'auth/login', LoginViewSet, basename='auth-login')
router.register(r'auth/register', RegistrationViewSet, basename='auth-register')
router.register(r'auth/refresh', RefreshViewSet, basename='auth-refresh')

router.register(r'', UserViewSet, basename='users')

urlpatterns = [
    *router.urls,
    path("accounts/", include("django.contrib.auth.urls")),
    path("dashboard/", views.dashboard, name='dashboard'),
]
