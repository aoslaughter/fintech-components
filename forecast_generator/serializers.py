from rest_framework import serializers
from .models import *
from .model_support import technologies, markets

class PortfolioSerializer(serializers.ModelSerializer):
    inception_date = serializers.DateField(format="%Y-%m-%d")
    exit_date = serializers.DateField(format="%Y-%m-%d")
    created = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M")
    modified = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M")

    class Meta:
        model = Portfolio
        fields = ["description", "max_investment_amount", "capacity_total"]

class ProjectSerializer(serializers.ModelSerializer):
    market = serializers.ChoiceField(choices=markets)
    technology = serializers.ChoiceField(choices=technologies)
    ntp = serializers.DateField(format="%Y-%m-%d")
    cod = serializers.DateField(format="%Y-%m-%d")
    created = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M")
    modified = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M")


    class Meta:
        model = Project
        fields = ["capacity", "developer_fee", "portfolio"]

class FinancialIOSerializer(serializers.ModelSerializer):
    inception_date = serializers.DateField(format="%Y-%m-%d")
    exit_date = serializers.DateField(format="%Y-%m-%d")
    created = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M")
    modified = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M")

    class Meta:
        model = FinancialIO
        fields = ["interest_rate", "risk_adjustor", "discount_rate",
                  "draw_number", "draw_utilization", "irr", "npv", "portfolio"]