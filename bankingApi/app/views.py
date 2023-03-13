from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Customer, Account, Transfer
from .permissions import IsEmployee
from .serializers import AccountSerializer, TransferSerializer, CustomerSerializer


@api_view(['POST'])
@permission_classes([IsEmployee])
def create_customer(request):
    customer_name = request.data.get('name')

    customer = Customer.objects.create(name=customer_name)
    serializer = CustomerSerializer(customer)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsEmployee])
def create_account(request):
    customer_id = request.data.get('customer_id')
    initial_balance = request.data.get('initial_balance')

    try:
        customer = Customer.objects.get(pk=customer_id)
        account = Account.objects.create(customer=customer, balance=initial_balance)
        serializer = AccountSerializer(account)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer with id {} does not exist'.format(customer_id)},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsEmployee])
def transfer(request):
    sender_account_id = request.data.get('sender_account_id')
    receiver_account_id = request.data.get('receiver_account_id')
    transfer_amount = Decimal(request.data.get('transfer_amount'))

    try:
        with transaction.atomic():
            sender_account = Account.objects.get(pk=sender_account_id)
            receiver_account = Account.objects.get(pk=receiver_account_id)

            if sender_account_id == receiver_account_id:
                return Response({'error': 'Sender and receiver account cannot be the same'},
                                status=status.HTTP_400_BAD_REQUEST)

            if transfer_amount <= 0:
                return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

            if sender_account.balance < transfer_amount:
                return Response({'error': 'Insufficient balance in sender account'}, status=status.HTTP_400_BAD_REQUEST)

            transfer = Transfer.objects.create(sender_account=sender_account, receiver_account=receiver_account,
                                               amount=transfer_amount)

            sender_account.balance -= transfer_amount
            sender_account.save()

            receiver_account.balance += transfer_amount
            receiver_account.save()

            transfer_serializer = TransferSerializer(transfer)

            return Response(transfer_serializer.data, status=status.HTTP_201_CREATED)
    except Account.DoesNotExist:
        return Response({'error': 'Account with given id does not exist'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsEmployee])
def account_balance(request, account_id):
    try:
        account = Account.objects.get(pk=account_id)
        return Response({'balance': account.balance})
    except Account.DoesNotExist:
        return Response({'error': 'Account with given id does not exist'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsEmployee])
def transfer_history(request, account_id):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    try:
        account = Account.objects.get(pk=account_id)
        query = Q(sender_account=account) | Q(receiver_account=account)
        if start_date:
            query &= Q(timestamp__gte=start_date)
        if end_date:
            query &= Q(timestamp__lte=end_date)
        transfers = Transfer.objects.filter(query)
        serializer = TransferSerializer(transfers, many=True)
        return Response(serializer.data)
    except Account.DoesNotExist:
        return Response({'error': 'Account with given id does not exist'}, status=status.HTTP_400_BAD_REQUEST)
