from decimal import Decimal

from rest_framework import serializers

from .models import Employee, Customer, Account, Transfer


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'first_name', 'last_name', 'username', 'password')


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.name')

    class Meta:
        model = Account
        fields = '__all__'


class TransferSerializer(serializers.ModelSerializer):
    source_account_customer_name = serializers.ReadOnlyField(source='source_account.customer.name')
    destination_account_customer_name = serializers.ReadOnlyField(source='destination_account.customer.name')
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Transfer
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['amount'] = round(Decimal(ret['amount']), 2)
        return ret
