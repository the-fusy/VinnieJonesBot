from django.db import models

from telegram.models import TelegramUser, Message
from fns.models import FnsUser


class SplitwiseGroup(models.Models):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    users = models.ManyToManyField('User', related_name='groups')


class SplitwiseUser(models.Model):
    id = models.IntegerField(primary_key=True)
    oauth_token = models.CharField(max_length=256, null=True, blank=True)
    oauth_token_secret = models.CharField(max_length=256, null=True, blank=True)


class User(models.Model):
    splitwise = models.OneToOneField(SplitwiseUser, on_delete=models.SET_NULL, null=True, blank=True)
    telegram = models.OneToOneField(TelegramUser, on_delete=models.SET_NULL, null=True, blank=True)
    fns = models.OneToOneField(FnsUser, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.CharField(max_length=128, default='start')
    last_query = models.CharField(max_length=256, null=True, blank=True)
    last_group = models.ForeignKey(SplitwiseGroup, on_delete=models.SET_NULL, null=True, blank=True)


class ShoppingList(models.Model):
    payer = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_date = models.DateField()
    users = models.ManyToManyField(User, through='ShoppingListUser')


class ShoppingListUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    approve = models.BooleanField(default=False)


class Item(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    price = models.IntegerField()
    count = models.DecimalField(max_digits=8, decimal_places=4)
    total_price = models.IntegerField()
    shares = models.ManyToManyField(User, through='ItemShare')


class ItemShare(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.IntegerField()
