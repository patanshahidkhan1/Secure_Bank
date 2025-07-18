from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class CustomerProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    email_address = models.EmailField()
    phone_number = models.CharField(max_length=15)
    account_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    account_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} - Balance: ₹{self.account_balance}"
    
    class Meta:
        verbose_name = "Customer Profile"
        verbose_name_plural = "Customer Profiles"

class BankTransaction(models.Model):
    TRANSACTION_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name = "Bank Transaction"
        verbose_name_plural = "Bank Transactions"
    
    def __str__(self):
        return f"{self.customer.username} - {self.transaction_type} - ₹{self.amount}"