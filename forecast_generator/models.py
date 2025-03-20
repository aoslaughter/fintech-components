from django.db import models
from .model_support.choice_sets import markets, technologies

# Create your models here.

# Portfolio: parent object for projects
class Portfolio(models.Model):
    description = models.CharField(max_length=250, null=True, default=None)
    inception_date = models.DateField()
    exit_date = models.DateField()
    max_investment_amount = models.DecimalField(
        default=0.0, max_digits=20, decimal_places=3)
    capacity_total = models.DecimalField(null=True, max_digits=7, decimal_places=3)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def capacity_calculation(self):
        return

# Project: capture key project characteristics
class Project(models.Model):
    capacity = models.DecimalField(max_digits=10, decimal_places=3)
    technology = models.CharField(max_length=20, choices=technologies)
    market = models.CharField(
        max_length=10, choices=markets, null=True, default=None
        )
    developer_fee = models.DecimalField(
        default=0.03, max_digits=7, decimal_places=2
        )
    ntp = models.DateField()
    cod = models.DateField()
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="%(class)s_set"
        )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

# Financial I/O: capture input parameters for forecast generation
# captures output results related to this set of inputs
class FinancialIO(models.Model):
    interest_rate = models.DecimalField(max_digits=5, decimal_places=3)
    risk_adjustor = models.DecimalField(
        null=True, default=None, max_digits=5, decimal_places=1
        )
    discount_rate = models.DecimalField(
        default=15.0/100, max_digits=5, decimal_places=1
        )
    draw_number = models.IntegerField(default=5)
    draw_utilization = models.DecimalField(
        default=1.0, max_digits=5, decimal_places=1
        )
    inception_date = models.DateField()
    exit_date = models.DateField()
    irr = models.DecimalField(
        null=True, default=None, max_digits=7, decimal_places=3
        )
    npv = models.DecimalField(
        null=True, default=None, max_digits=20, decimal_places=3
        )
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="%(class)s_set"
        )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)