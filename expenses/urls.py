from django.urls import path
from .views import UserListCreateView, TransactionListCreateView, OutstandingBalancesView

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('outstanding-balances/', OutstandingBalancesView.as_view(), name='outstanding-balances'),
    path('outstanding-balances/<int:user_id>/', OutstandingBalancesView.as_view(), name='outstanding-balances'),

]
