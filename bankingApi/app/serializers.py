from rest_framework import serializers

from .models import Employee, Customer, Account, Transfer, Log


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'name', 'email', 'password')


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.name')

    class Meta:
        model = Account
        fields = '__all__'
        depth = 3


class TransferSerializer(serializers.ModelSerializer):
    source_account_customer_name = serializers.ReadOnlyField(source='source_account.customer.name')
    destination_account_customer_name = serializers.ReadOnlyField(source='destination_account.customer.name')

    class Meta:
        model = Transfer
        fields = '__all__'
        depth = 3


class LogSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='employee.user.username', read_only=True)

    class Meta:
        model = Log
        fields = ['user', 'timestamp', 'from_account', 'to_account', 'amount']
