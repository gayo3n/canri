from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import CustomUser


User = get_user_model()

class UserForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            #htmlの表示を変更可能にします
            self.fields['userid'].widget.attrs['class'] = 'form-control'
            self.fields['password'].widget.attrs['class'] = 'form-control'
            self.fields['username'].widget.attrs['class'] = 'form-control'


 

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('userid', 'password', 'username')

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['required'] = ''
                
                print(field.label)
                if field.label == '姓':
                    field.widget.attrs['autofocus'] = ''
                    field.widget.attrs['placeholder'] = '大原'
                elif field.label == '名':
                    field.widget.attrs['placeholder'] = '太郎'
                elif field.label == 'メールアドレス':
                    field.widget.attrs['placeholder'] = '***＠gmail.com'