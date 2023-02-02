from django.db import models


# class Pass(models.Model):
#     PASS_TYPES = (
#         ('A', 'Accomodation'),
#         ('E', 'Events Participation'),
#         ('F', 'Flagship Events'),
#         ('N', 'Normal Passes')
#     )

#     name = models.CharField(max_length=50, default="pass")
#     amount = models.IntegerField()
#     type = models.CharField(max_length=1, choices=PASS_TYPES, default='N')

#     class Meta:
#         verbose_name_plural = "Passes"

#     def __str__(self) -> str:
#         return self.name


class Order(models.Model):
    id = models.CharField(max_length=30, unique=True, primary_key=True)
    user = models.ForeignKey("registration.UserProfile", on_delete=models.DO_NOTHING)
    checksum = models.CharField(max_length=200, default="")
    pay_for = models.CharField(max_length=100, default="")
    amount = models.CharField(max_length=10, default="1.00")
    currency = models.CharField(max_length=3, default="INR")
    request_timestamp = models.CharField(max_length=20, default="")
    signature = models.CharField(max_length=200, default="")
    response_timestamp = models.CharField(max_length=20, default="")
    result_code = models.CharField(max_length=4, default="0000")
    result_msg = models.CharField(max_length=200, default="")
    transaction_token = models.CharField(max_length=100, default="")

    class Meta:
        verbose_name_plural = "Orders"

    def __str__(self):
        return self.id


class Transaction(models.Model):
    txn_id = models.CharField(max_length=100, unique=True, primary_key=True, default="")
    bank_txn_id = models.CharField(max_length=100, default="")
    user = models.ForeignKey("registration.UserProfile", on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=20, default="failed")
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    amount = models.CharField(max_length=10, default="1.00")
    gateway_name = models.CharField(max_length=20, default="")
    payment_mode = models.CharField(max_length=20, default="UPI")
    resp_code = models.CharField(max_length=5, default="")
    resp_msg = models.CharField(max_length=200, default="")
    timestamp = models.CharField(max_length=20, default="")

    class Meta:
        verbose_name_plural = "Transactions"

    def __str__(self) -> str:
        return self.txn_id
