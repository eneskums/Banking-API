from django.urls import path

from .views import create_customer, create_account, transfer, account_balance, transfer_history

urlpatterns = [
    path('create-customer', create_customer, name='create_customer'),
    path('create-account', create_account, name='create_account'),
    path('transfer-amount', transfer, name='transfer'),
    path('account-balance/<int:account_id>', account_balance, name='account_balance'),
    path('transfer-history/<int:account_id>', transfer_history, name='transfer_history'),
]
