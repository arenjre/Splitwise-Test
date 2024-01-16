from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self) -> str:
        return f"{self.name}"

class Transaction(models.Model):
    payer = models.ForeignKey(User, related_name='payer', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    participants = models.ManyToManyField(User, related_name='participants')
    split_shares = models.TextField()

class Balance(models.Model):
    from_user = models.ForeignKey(User, related_name='balance_from', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='balance_to', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"from {self.from_user} to {self.to_user} and amount is {self.amount}"
