
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import User, Transaction, Balance
from .serializers import UserSerializer, TransactionSerializer, BalanceSerializer, CalBalanceSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TransactionListCreateView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        option_exact = True
        request_data = request.data.copy()
        type = request.GET.get('type')
        transaction_type = ["EQUAL", "EXACT", "PERCENT"]
        if type not in transaction_type:
            return Response({"result": 'Transaction type can be "EQUAL", "EXACT", "PERCENT" only.'})

        split_shares = [int(element.replace(',', '')) for element in request.data['split_shares'].split()]

        if type == "EXACT":
            payer_mount = request.data['amount'] - sum(split_shares)

            if payer_mount < 0:
                return Response({"result": "Split amount are not correct!"})
            else:
                payer_mount = [payer_mount]
                # payer_mount.extend(split_shares)
                # split_shares = payer_mount
                type = "PERCENT"
                option_exact = False


        if type == "EQUAL":
            split_shares = [25,25,25,25]
            request_data
            request_data['split_shares'] = "25 25 25 25"
            type = "PERCENT"

        if type == "PERCENT" and sum(split_shares) != 100 and option_exact:
            return Response({"result": "Split percentages are not correct!"})
        

        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)

        # Create the transaction
        transaction = serializer.save()

        # Update user balances based on the transaction
        balances = self.update_user_balances(transaction, type, split_shares)

        # Include the updated balances in the response
        balance_serializer = BalanceSerializer(balances, many=True)
        response_data = serializer.data
        response_data['updated_balances'] = balance_serializer.data

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def update_user_balances(self, transaction, type, split_shares):
        # Update participants' balances
        payer = transaction.payer
        participants = transaction.participants.all()
        amount = transaction.amount
        # percentages_list = [int(element.replace(',', '')) for element in transaction.split_shares.split()]
        percentages_list = split_shares

        # Calculate individual shares
        total_percentage = sum(percentages_list)
        individual_shares = [(amount * percentage) / total_percentage for percentage in percentages_list]

        balances = []
        all_balances = Balance.objects.all()

        def reverse_handler(x):
            if_check = True
            for bal in all_balances:
                if bal.from_user == x and bal.to_user == payer:
                    if_check = bal

            return if_check

        for i, participant in enumerate(participants):
            # check_reverse = reverse_handler(participant)
            check_reverse = True
            participant.balance -= individual_shares[i]
            participant.save()

            if check_reverse == True:
                # Create corresponding balances for payer and participants
                payer_to_participant = Balance.objects.create(
                    from_user=payer,
                    to_user=participant,
                    amount=individual_shares[i]
                )
                participant_to_payer = Balance.objects.create(
                    from_user=participant,
                    to_user=payer,
                    amount=-individual_shares[i]
                )


            balances.extend([payer_to_participant, participant_to_payer])

        return balances

class OutstandingBalancesView(generics.ListAPIView):
    queryset = Balance.objects.filter(amount__gt=0)
    serializer_class = CalBalanceSerializer

    def make_unique(self, data, keys):
        seen = set()
        unique_data = []

        for entry in data:
            entry_key = tuple(entry[key] for key in keys)

            if entry_key not in seen:
                seen.add(entry_key)
                unique_data.append(entry)

        return unique_data


    def list(self, request, *args, **kwargs):
        user_id = None
        try:
            user_id = self.kwargs['user_id']
        except:
            pass

        outstanding_balances = Balance.objects.filter(amount__gt=0)
        # Create a dictionary to store aggregated balances
        aggregated_balances = {}

        for balance in outstanding_balances:
            # Use a tuple as a key to handle both directions (A owes B and B owes A)
            key = (balance.from_user.id, balance.to_user.id)

            # Accumulate amounts for the same pair of users
            if key in aggregated_balances:
                aggregated_balances[key] += balance.amount
            else:
                aggregated_balances[key] = balance.amount

        # Create a list of aggregated balances
        result = []
        processed_pairs = set()

        for (from_user_id, to_user_id), amount in aggregated_balances.items():
            from_user = User.objects.get(id=from_user_id)
            to_user = User.objects.get(id=to_user_id)

            # Check if the reverse owe relationship exists
            reverse_key = (to_user_id, from_user_id)

            if reverse_key not in processed_pairs:
                reverse_amount = aggregated_balances.get(reverse_key, 0)

                # Determine the direction of the owe relationship
                if amount > reverse_amount:
                    result.append({
                        'from_user': from_user,
                        'to_user': to_user,
                        'amount': amount - reverse_amount,
                    })
                else:
                    result.append({
                        'from_user': to_user,
                        'to_user': from_user,
                        'amount': reverse_amount - amount,
                    })

                # Mark the reverse pair as processed
                processed_pairs.add(reverse_key)

        def for_usr(el):
            if el.to_user.id == user_id:
                return True
        
        unique_data = self.make_unique(result, ['from_user', 'to_user'])
        if user_id:
            usr_data = []
            for data in unique_data:
                if data['to_user'].id == user_id:
                    usr_data.append(data)

            unique_data = usr_data

        if unique_data:
            all_unique = []
            for data in unique_data:
                if data['from_user'] != data['to_user']:
                    all_unique.append(data)
            unique_data = all_unique
        serializer = CalBalanceSerializer(unique_data, many=True)

        # import pdb;pdb.set_trace()
        return Response(serializer.data, status=status.HTTP_200_OK)

