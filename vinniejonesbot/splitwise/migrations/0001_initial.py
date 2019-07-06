# Generated by Django 2.2.3 on 2019-07-06 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('telegram', '__first__'),
        ('fns', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('price', models.IntegerField()),
                ('count', models.DecimalField(decimal_places=4, max_digits=8)),
                ('total_price', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_date', models.DateField()),
                ('state', models.CharField(default='active', max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='SplitwiseGroup',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='SplitwiseUser',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('oauth_token', models.CharField(blank=True, max_length=256, null=True)),
                ('oauth_token_secret', models.CharField(blank=True, max_length=256, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(default='start', max_length=128)),
                ('last_query', models.CharField(blank=True, max_length=256, null=True)),
                ('fns', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fns.FnsUser')),
                ('last_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='splitwise.SplitwiseGroup')),
                ('splitwise', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='splitwise.SplitwiseUser')),
                ('telegram', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='telegram.TelegramUser')),
            ],
        ),
        migrations.AddField(
            model_name='splitwisegroup',
            name='users',
            field=models.ManyToManyField(related_name='groups', to='splitwise.User'),
        ),
        migrations.CreateModel(
            name='ShoppingListUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approve', models.BooleanField(default=False)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='telegram.Message')),
                ('shopping_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='splitwise.ShoppingList')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='splitwise.User')),
            ],
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='payer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='splitwise.User'),
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='users',
            field=models.ManyToManyField(through='splitwise.ShoppingListUser', to='splitwise.User'),
        ),
        migrations.CreateModel(
            name='ItemShare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='splitwise.Item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='splitwise.User')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='shares',
            field=models.ManyToManyField(through='splitwise.ItemShare', to='splitwise.User'),
        ),
        migrations.AddField(
            model_name='item',
            name='shopping_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='splitwise.ShoppingList'),
        ),
    ]
