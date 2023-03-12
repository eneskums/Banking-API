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
    source_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='source_account')
    destination_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='destination_account')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.transaction_id} - {self.source_account} to {self.destination_account}'


class Log(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    from_account = models.ForeignKey(Account, related_name='logs_sent', on_delete=models.CASCADE)
    to_account = models.ForeignKey(Account, related_name='logs_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
