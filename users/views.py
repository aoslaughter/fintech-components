import django_filters
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse
from users.serializers import UserSerializer
from users.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from users.forms import UserRegistrationForm

def dashboard(request):
    return render(request, 'users/dashboard.html')

def register(request):
    if request.method == 'GET':
        return render(
            request, 'users/register.html', {'form': UserRegistrationForm}
        )
    elif request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('dashboard'))

class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [OrderingFilter]
    queryset = User.objects.none()
    ordering_fields = ['modified']

