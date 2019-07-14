import logging

from enum import Enum

from django.db import models
from django.db.models import F

from telegram.models import TelegramUser
from telegram.types import Message

from telegram import bot

from fns.models import FnsUser


logger = logging.getLogger(__name__)


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

    def _get_item_buttons(self, user):
        return [
            item.get_button_row_for_user(user)
            for item in self.item_set.all().prefetch_related('shares')
        ]

    def send_list(self, user: User) -> Message:
        return user.telegram.send_message(
            text='Покупка',
            reply_markup={
                'inline_keyboard': self._get_item_buttons(user) + [[{
                    'text': 'Апрувнуть',
                    'callback_data': 'approve',
                }]]
            }
        )

    def add_user(self, user: User):
        ShoppingListUser.objects.create(
            user=user,
            shopping_list=self,
            message_id=self.send_list(user).id,
        )

    def update_lists(self):
        for list_user in ShoppingListUser.objects.filter(shopping_list=self).select_related('user'):
            list_user.user.telegram.edit_message(
                message_id=list_user.message_id,
                text='Покупка',
                reply_markup={
                    'inline_keyboard': self._get_item_buttons(list_user.user) + [[{
                        'text': 'Апрувнуть' if not list_user.approve else 'Дизапрувнуть',
                        'callback_data': 'approve' if not list_user.approve else 'disapprove',
                    }]]
                }
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
    count = models.DecimalField(max_digits=4, decimal_places=2)
    total_price = models.IntegerField()
    shares = models.ManyToManyField(User, through='ItemShare')

    def get_button_row_for_user(self, user: User):
        shares = ItemShare.objects.filter(user=user, item=self, count__gte=0)

        result = [{
            'text': f'{self.name}: {self.count} * {self.price / 100}',
            'callback_data': f'{self.id}_1',
        }]

        if shares:
            result.append({
                'text': f'- ({shares[0].count})',
                'callback_data': f'{self.id}_-1',
            })

        return result

    def change_count(self, user, new_value):
        if not ItemShare.objects.filter(user=user, item=self).exists():
            ItemShare.objects.create(user=user, item=self, count=0)
        ItemShare.objects.filter(user=user, item=self).update(count=F('count') + new_value)
        self.shopping_list.update_lists()


class ItemShare(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.IntegerField()
