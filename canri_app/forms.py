# forms.py
from django import forms


class SearchForm(forms.Form):
    search_query = forms.CharField(label='メンバー名を入力', max_length=100, required=False, widget=forms.TextInput)
