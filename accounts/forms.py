from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth import get_user_model, authenticate
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
    password = forms.CharField(max_length=10) # パスワードの文字数10文字

    class Meta:
        model = User
        fields = ['user_id', 'password', 'name', 'administrator_flag']
        error_messages = {
            'user_id':{
                'unique': 'このアカウントIDは既に使用されています。'
            },
            'name':{
                'unique': 'この名前のユーザーは既に存在しています。'
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def new_username(self):
        name = self.changed_data['name']
        if User.objects.filter(name=name):
            raise ValidationError('この名前のユーザーは既に存在しています。')
        return name
    
    def new_user_id(self):
        user_id = self.changed_data['user_id']
        if User.objects.filter(user_id=user_id):
            raise ValidationError('このユーザーIDは既に使用されています。')
        return user_id

class LoginForm(AuthenticationForm):
    pass


class CustomPasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        required=True,
        max_length=255,
        min_length=6,
        widget=forms.PasswordInput(
        )
    )

    new_password = forms.CharField(
        required=True,
        max_length=255,
        min_length=6,
        widget=forms.PasswordInput(
        )
    )

    confirm_new_password = forms.CharField(
        required=True,
        max_length=255,
        min_length=6,
        widget=forms.PasswordInput(
        )
    )

    def __init__(self, _user_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_name = _user_name

    def clean(self):
        cleaned_data = super(CustomPasswordChangeForm, self).clean()
        print(cleaned_data)
        return cleaned_data
    
    def clean_current_password(self):
        current_password = self.cleaned_data['current_password']
        if self._user_name and current_password:
            auth_result = authenticate(
                username = self._user_name,
                password = current_password
            )
            if not auth_result:
                raise ValidationError('パスワードが間違っています')
        return current_password
    
    def clean_new_password(self):
        new_password = self.cleaned_data['newpassword']
        return new_password
    
    def clean_confirm_new_password(self):
        confirm_new_password = self.cleaned_data['confirm_new_password']
        if confirm_new_password != self.cleaned_data['new_password']:
            raise ValidationError('パスワードが一致しません')
        return confirm_new_password
    

class MySetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs['class'] = '[class名]'
        self.fields['new_password2'].widget.attrs['class'] = '[class名]'
        self.fields['new_password1'].widget.attrs['placeholder'] = '半角英字6文字以上'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'パスワード確認用'
        self.fields['new_password1'].widget.attrs['minlength'] = 6
        self.fields['new_password1'].widget.attrs['maxlength'] = 10
        self.fields['new_password2'].widget.attrs['minlength'] = 6
        self.fields['new_password2'].widget.attrs['maxlength'] = 10

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError('パスワードが一致しません。')
        return cleaned_data
    
    def clean_new_password2(self):
        new_password2 = self.cleaned_data.get('new_password2')
        if self.user.check_password(new_password2):
            raise forms.ValidationError('現在と同じパスワードです')
        return new_password2