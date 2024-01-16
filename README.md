## _Expense Sharing_

## Development

### To create transaction (post):

```sh
http://127.0.0.1:8000/api/transactions/?type=EQUAL
```
- For first test case
  type = EQUAL
  payload = {
    "payer": 1,
    "amount": 1000,
    "participants": [2, 3, 4],
    "split_shares": "25 25 25 25"
}
- For second test case
  type = EXACT
  payload = {
    "payer": 1,
    "amount": 1250,
    "participants": [2, 3],
    "split_shares": "370 880"
}
- For third test case
  type = PERCENT
  payload = {
    "payer": 4,
    "amount": 1200,
    "participants": [4,1,2,3],
    "split_shares": "40, 20, 20, 20"
}

None: Transaction type can be "EQUAL", "EXACT", "PERCENT" only.
If you choose EQUAL then split_shares will 25% for each. And if you add different  split_shares it will automatically will change


### To get all user's owes (get):

```sh
http://127.0.0.1:8000/api/outstanding-balances/
```

### To get specific user's owes (get):

```sh
http://127.0.0.1:8000/api/outstanding-balances/1/
```

