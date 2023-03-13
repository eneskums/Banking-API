from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.get_full_name()}'


class Customer(models.Model):
    name = models.CharField(null=True, blank=True, max_length=255, verbose_name='Ad Soyad')

    def __str__(self):
        return f'{self.name}'


class Account(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='Bakiye')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer.name}'


class Transfer(models.Model):
    sender_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sender_account')
    receiver_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='receiver_account')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.amount} - {self.sender_account} to {self.receiver_account}'
