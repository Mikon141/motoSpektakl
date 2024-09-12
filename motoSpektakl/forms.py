from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
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
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.is_active = False  # Użytkownik będzie nieaktywny do momentu aktywacji
        if commit:
            user.save()
        return user


# Formularz do edycji profilu
class EditProfileForm(UserChangeForm):
    profile_picture = forms.ImageField(required=False, label="Zdjęcie profilowe")
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Opis użytkownika")
    vehicle = forms.CharField(max_length=100, required=False, label="Pojazd użytkownika")

    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture', 'description', 'vehicle']
        labels = {
            'username': 'Login',
            'email': 'Adres e-mail',
            'profile_picture': 'Zdjęcie profilowe',
            'description': 'Opis użytkownika',
            'vehicle': 'Pojazd użytkownika',
        }

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['vehicle'].widget.attrs.update({'class': 'form-control'})


# Formularz do zmiany hasła
class EditPasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        super(EditPasswordForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})