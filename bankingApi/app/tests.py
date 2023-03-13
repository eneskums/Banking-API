from datetime import datetime, timedelta

from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from decimal import Decimal

from .models import Customer, Account, Transfer
from .serializers import TransferSerializer


class BankingAPITests(APITestCase):
    def setUp(self):
        self.employee_group = Group.objects.create(name='employee')
        self.employee_user = User.objects.create_user(username='employeeuser', password='123456')
        self.employee_user.groups.add(self.employee_group)
        self.customer = Customer.objects.create(name='Sarah Johnson')
        self.customer2 = Customer.objects.create(name='Michael Garcia')
        self.customer3 = Customer.objects.create(name='Emily Rodriguez')

        self.client = APIClient()

    def test_create_account(self):
        self.client.force_authenticate(user=self.employee_user)
        url = reverse('create_account')
        data = {
            'customer_id': self.customer.id,
            'initial_balance': 500
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer'], self.customer.id)
        self.assertEqual(response.data['balance'], '500.00')

    def test_create_account_with_invalid_customer(self):
        self.client.force_authenticate(user=self.employee_user)
        url = reverse('create_account')
        data = {
            'customer_id': 9999,
            'initial_balance': 500
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Customer with id 9999 does not exist')

    def test_transfer(self):
        self.client.force_authenticate(user=self.employee_user)
        sender_account = Account.objects.create(customer=self.customer, balance=10000)
        receiver_account = Account.objects.create(customer=self.customer, balance=0)

        url = reverse('transfer')
        data = {
            'sender_account_id': sender_account.id,
            'receiver_account_id': receiver_account.id,
            'transfer_amount': 5000
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['sender_account'], sender_account.id)
        self.assertEqual(response.data['receiver_account'], receiver_account.id)
        self.assertEqual(response.data['amount'], Decimal('5000.00'))

        sender_account.refresh_from_db()
        receiver_account.refresh_from_db()
        self.assertEqual(sender_account.balance, Decimal('5000.00'))
        self.assertEqual(receiver_account.balance, Decimal('5000.00'))

    def test_transfer_with_one_account(self):
        self.client.force_authenticate(user=self.employee_user)
        account = Account.objects.create(customer=self.customer, balance=1000)

        url = reverse('transfer')
        data = {
            'sender_account_id': account.id,
            'receiver_account_id': account.id,
            'transfer_amount': 1500
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Sender and receiver account cannot be the same')

        account.refresh_from_db()
        self.assertEqual(account.balance, Decimal('1000.00'))

    def test_transfer_with_invalid_amount(self):
        self.client.force_authenticate(user=self.employee_user)
        sender_account = Account.objects.create(customer=self.customer, balance=1000)
        receiver_account = Account.objects.create(customer=self.customer, balance=0)

        url = reverse('transfer')
        data = {
            'sender_account_id': sender_account.id,
            'receiver_account_id': receiver_account.id,
            'transfer_amount': 0
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid amount')

        sender_account.refresh_from_db()
        receiver_account.refresh_from_db()
        self.assertEqual(sender_account.balance, Decimal('1000.00'))
        self.assertEqual(receiver_account.balance, Decimal('0.00'))

    def test_transfer_insufficient_balance(self):
        self.client.force_authenticate(user=self.employee_user)
        sender_account = Account.objects.create(customer=self.customer, balance=1000)
        receiver_account = Account.objects.create(customer=self.customer, balance=0)

        url = reverse('transfer')
        data = {
            'sender_account_id': sender_account.id,
            'receiver_account_id': receiver_account.id,
            'transfer_amount': 1500
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Insufficient balance in sender account')

        sender_account.refresh_from_db()
        receiver_account.refresh_from_db()
        self.assertEqual(sender_account.balance, Decimal('1000.00'))
        self.assertEqual(receiver_account.balance, Decimal('0.00'))

    def test_get_balance(self):
        self.client.force_authenticate(user=self.employee_user)
        account = Account.objects.create(customer=self.customer, balance=12000)

        url = reverse('account_balance', kwargs={'account_id': account.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], Decimal('12000.00'))

    def test_get_balance_with_invalid_account(self):
        self.client.force_authenticate(user=self.employee_user)

        url = reverse('account_balance', kwargs={'account_id': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Account with given id does not exist')

    def test_get_transfer_history(self):
        self.client.force_authenticate(user=self.employee_user)
        sender_account = Account.objects.create(customer=self.customer, balance=1000)
        receiver_account = Account.objects.create(customer=self.customer2, balance=1000)

        Transfer.objects.create(sender_account=sender_account, receiver_account=receiver_account,
                                amount=Decimal('100.00'))
        Transfer.objects.create(sender_account=sender_account, receiver_account=receiver_account,
                                amount=Decimal('200.00'))
        Transfer.objects.create(sender_account=receiver_account, receiver_account=sender_account,
                                amount=Decimal('50.00'))

        url = reverse('transfer_history', kwargs={'account_id': sender_account.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        self.assertEqual(response.data[0]['sender_account'], sender_account.id)
        self.assertEqual(response.data[0]['receiver_account'], receiver_account.id)
        self.assertEqual(response.data[0]['amount'], Decimal('100.00'))

        self.assertEqual(response.data[1]['sender_account'], sender_account.id)
        self.assertEqual(response.data[1]['receiver_account'], receiver_account.id)
        self.assertEqual(response.data[1]['amount'], Decimal('200.00'))

        self.assertEqual(response.data[2]['sender_account'], receiver_account.id)
        self.assertEqual(response.data[2]['receiver_account'], sender_account.id)
        self.assertEqual(response.data[2]['amount'], Decimal('50.00'))

    def test_get_transfer_history_with_invalid_account(self):
        self.client.force_authenticate(user=self.employee_user)

        url = reverse('transfer_history', kwargs={'account_id': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Account with given id does not exist')

    def test_get_transfer_history_filter_by_date(self):
        self.client.force_authenticate(user=self.employee_user)
        start_date = datetime.now().date() - timedelta(days=1)
        end_date = datetime.now().date() + timedelta(days=1)

        sender_account = Account.objects.create(customer=self.customer, balance=1000)
        receiver_account = Account.objects.create(customer=self.customer2, balance=1000)

        Transfer.objects.create(sender_account=sender_account, receiver_account=receiver_account,
                                amount=Decimal('100.00'))
        Transfer.objects.create(sender_account=sender_account, receiver_account=receiver_account,
                                amount=Decimal('200.00'))
        Transfer.objects.create(sender_account=receiver_account, receiver_account=sender_account,
                                amount=Decimal('50.00'))

        url = reverse('transfer_history',
                      kwargs={'account_id': sender_account.id}) + '?start_date={}&end_date={}'.format(start_date,
                                                                                                      end_date)
        response = self.client.get(url)

        transfers = Transfer.objects.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
        serializer = TransferSerializer(transfers, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_transfer_history_filter_by_invalid_date(self):
        self.client.force_authenticate(user=self.employee_user)
        sender_account = Account.objects.create(customer=self.customer, balance=1000)
        receiver_account = Account.objects.create(customer=self.customer2, balance=1000)

        Transfer.objects.create(sender_account=sender_account, receiver_account=receiver_account,
                                amount=Decimal('100.00'))
        Transfer.objects.create(sender_account=sender_account, receiver_account=receiver_account,
                                amount=Decimal('200.00'))
        Transfer.objects.create(sender_account=receiver_account, receiver_account=sender_account,
                                amount=Decimal('50.00'))
        url = reverse('transfer_history',
                      kwargs={'account_id': sender_account.id}) + '?start_date=2021-01-01&end_date=2020-12-31'

        response = self.client.get(url)

        self.assertEqual(response.data, [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
