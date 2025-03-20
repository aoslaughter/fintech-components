from users.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'is_staff', 'created', 'modified']
