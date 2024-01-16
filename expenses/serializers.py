# In serializers.py

from rest_framework import serializers
from .models import User, Transaction, Balance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class BalanceSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()

    class Meta:
        model = Balance
        fields = '__all__'

    def get_from_user(self, obj):
        return obj.from_user.name

    def get_to_user(self, obj):
        return obj.to_user.name

    def get_result(self, obj):
        return f"{obj.to_user} owes {obj.from_user}: Rs {obj.amount}"

class CalBalanceSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()

    class Meta:
        model = Balance
        fields = '__all__'

    def get_from_user(self, obj):
        return obj['from_user'].name

    def get_to_user(self, obj):
        return obj['to_user'].name

    def get_result(self, obj):
        return f"{obj['to_user']} owes {obj['from_user']}: Rs {obj['amount']}"
