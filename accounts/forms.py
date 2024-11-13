from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import User
from django import forms
from django.core.exceptions import ValidationError

User = get_user_model()

class AccountAddForm(forms.Form):
    userid = forms.CharField(
        required=True,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                'placeholder':''
            }
        )
    )
    password = forms.CharField(
        required=True,
        max_length=255,
        min_length=6,
        widget=forms.PasswordInput(
            attrs={
                'placeholder':'******',
            }
        )
    )
    username = forms.CharField(
        required=True,
        min_length=3,
        max_length=16,
        widget=forms.TextInput(
            attrs={
                'placeholder':''
            }
        )
    )

    def clea_userid(self):
        userid =self.cleaned_data['user_id']
        if User.objects.filter(userid=userid):
            raise ValidationError('すでに使用されているIDです')
        return userid
    
    def clean_password(self):
        password = self.cleaned_data['password']
        return password
    
    def clean_username(self):
        username = self.cleaned_data['name']
        return username




class UserForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            #htmlの表示を変更可能にします
            self.fields['user_id'].widget.attrs['class'] = 'form-control'
            self.fields['password'].widget.attrs['class'] = 'form-control'
            self.fields['name'].widget.attrs['class'] = 'form-control' 

class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('user_id', 'password', 'name')

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['required'] = '' #全フィールドを入力必須

                print(field.label)
                if field.label == '姓':
                    field.widget.attrs['autofocus'] = '' #入力可能状態にする
                    field.widget.attrs['placeholder'] = '大原'
                elif field.label == '名':
                    field.widget.attrs['placeholder'] = '太郎'
                elif field.label == 'メールアドレス':
                    field.widget.attrs['placeholder'] = '***＠gmail.com'