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
        widget=forms.TextInput(
            attrs={
                'placeholder': ''  # プレースホルダーを空に設定
            }
        )
    )
        password = forms.CharField(
        required=True,
        max_length=10,
        min_length=6,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '******',  # プレースホルダーを設定
            }
        )
    )
        name = forms.CharField(
        required=True,
        min_length=3,
        max_length=16,
        widget=forms.TextInput(
            attrs={
                'placeholder': ''  # プレースホルダーを空に設定
            }
        )
    )
        

        def clean_user_id(self):
            user_id = self.cleaned_data['user_id']
            # ユーザーIDが数字のみで構成されているかチェック
            if not user_id.isdigit():
                raise ValidationError('ユーザーIDは数字のみでなければなりません。')
            # ユーザーIDが既に存在するかチェック
            if User.objects.filter(user_id=user_id).exists():
                raise ValidationError('すでに使用されているIDです')
            return user_id

        def clean_password(self):
            password = self.cleaned_data['password']
            # パスワードに対する追加のバリデーションをここに追加可能
            return password

        def clean_name(self):
            name = self.cleaned_data['name']
            # 名前に対する追加のバリデーションをここに追加可能
            return name
        def clean_user_id(self):
            user_id = self.cleaned_data['user_id']
            if not user_id.isdigit():
                raise ValidationError('ユーザーIDは数字のみでなければなりません。')
            if User.objects.filter(user_id=user_id).exists():
                raise ValidationError('すでに使用されているIDです')
            return user_id
        def clean_password(self):
            password = self.cleaned_data['password']
            return password
        def clean_name(self):
            name = self.cleaned_data['name']
            return name



class UserForm(forms.ModelForm):
        # 最大入力数10文字指定
    name = forms.CharField(max_length=10) # 名前の文字数10文字
    user_id = forms.CharField(max_length=10) # アカウントIDの文字数10文字
    password = forms.CharField(max_length=10) # パスワードの文字数10文字

    class Meta:
        model = User
        fields = ['user_id', 'password', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class UserCreationForm(UserCreationForm):    # 最大入力数10文字指定
    name = forms.CharField(max_length=10) # 名前の文字数10文字
    user_id = forms.CharField(max_length=10) # アカウントIDの文字数10文字
    password = forms.CharField(max_length=10) # パスワードの文字数10文字

    class Meta:
        model = User
        fields = ('user_id', 'password', 'name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = '' #全フィールドを入力必須

            print(field.label)
            if field.label == 'ID':
                field.widget.attrs['autofocus'] = '' #入力可能状態にする
                field.widget.attrs['placeholder'] = '12345'
            elif field.label == 'パスワード':
                field.widget.attrs['placeholder'] = 'password'
            elif field.label == '名前':
                field.widget.attrs['placeholder'] = '大原太郎'


class LoginForm(AuthenticationForm):
    pass