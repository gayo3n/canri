from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import User
from django import forms
from django.core.exceptions import ValidationError

# 現在のユーザーモデルを取得
User = get_user_model()

class AccountAddForm(forms.Form):
    user_id = forms.CharField(
        required=True,
        max_length=10,
        min_length=8,
        widget=forms.TextInput(attrs={'placeholder': ''})
    )
    password = forms.CharField(
        required=True,
        max_length=10,
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': '******'})
    )
    name = forms.CharField(
        required=True,
        min_length=3,
        max_length=16,
        widget=forms.TextInput(attrs={'placeholder': ''})
    )

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        if not user_id.isdigit():
            raise ValidationError('ユーザーIDは数字のみでなければなりません。')
        if User.objects.filter(user_id=user_id).exists():
            raise ValidationError('すでに使用されているIDです')
        return user_id

    def clean_password(self):
        password = self.cleaned_data['password']
        # パスワードの追加バリデーションはここに記述可能
        return password

    def clean_name(self):
        name = self.cleaned_data['name']
        # 名前の追加バリデーションはここに記述可能
        return name



class UserForm(forms.ModelForm):
        # 最大入力数10文字指定
    name = forms.CharField(max_length=10) # 名前の文字数10文字
    user_id = forms.CharField(max_length=10) # アカウントIDの文字数10文字
    password = forms.CharField(max_length=10, widget=forms.PasswordInput) # パスワードの文字数10文字

    class Meta:
        model = User
        fields = ['user_id', 'password', 'name', 'administrator_flag']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class LoginForm(AuthenticationForm):
    pass