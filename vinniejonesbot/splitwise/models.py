from enum import Enum

from django.db import models

from telegram.models import TelegramUser
from telegram.types import Message

from fns.models import FnsUser


class SplitwiseGroup(models.Model):
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
    state = models.CharField(max_length=128, default='main')
    last_query = models.CharField(max_length=256, null=True, blank=True)
    last_group = models.ForeignKey(SplitwiseGroup, on_delete=models.SET_NULL, null=True, blank=True)

    class UserManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().select_related('splitwise', 'telegram', 'fns')

    objects = UserManager()


class ShoppingList(models.Model):
    payer = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='+', null=True, blank=True)
    payment_date = models.DateField()
    users = models.ManyToManyField(User, through='ShoppingListUser')

    def set_payer(self, user: User):
        self.payer = user
        self.save()

    def send_list(self, user: User) -> Message:
        return user.telegram.send_message(text=list(self.item_set.all().values_list('name')))

    def add_user(self, user: User):
        ShoppingListUser.objects.create(
            user=user,
            shopping_list=self,
            message_id=self.send_list(user).id,
        )


class ShoppingListUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    message_id = models.IntegerField()
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
