from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adres e-mail")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nazwa użytkownika',
            'email': 'Adres e-mail',
            'password1': 'Hasło',
            'password2': 'Potwierdź hasło',
        }
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Nazwa użytkownika"
        self.fields['email'].label = "Adres e-mail"
        self.fields['password1'].label = "Hasło"
        self.fields['password2'].label = "Potwierdź hasło"
    
    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.is_active = False  # Użytkownik będzie nieaktywny do momentu aktywacji
        if commit:
            user.save()
        return user