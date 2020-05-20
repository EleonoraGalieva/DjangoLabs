from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import *


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = '__all__'
        exclude = ['user', 'verified']
