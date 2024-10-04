from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Post, BlogComment, ForumThread, ForumComment  # Usuń PostComment

# Formularz rejestracji
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


from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.forms import FileInput
from .models import UserProfile

class EditProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        required=False,
        label="Zdjęcie profilowe",
        widget=FileInput(attrs={
            'class': 'form-control-file',
            'initial_text': 'Aktualne zdjęcie:',
            'input_text': 'Zmień',
            'clear_checkbox_label': 'Usuń zdjęcie',
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        label="Opis użytkownika"
    )
    vehicle = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Pojazd użytkownika"
    )

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'description', 'vehicle']
        labels = {
            'profile_picture': 'Zdjęcie profilowe',
            'description': 'Opis użytkownika',
            'vehicle': 'Pojazd użytkownika',
        }

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['vehicle'].widget.attrs.update({'class': 'form-control'})


from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # Upewnij się, że tylko te pola będą edytowalne
        labels = {
            'username': 'Nazwa użytkownika',
            'email': 'Adres e-mail',
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        # Ukrycie pola `date_joined`, aby nie było brane pod uwagę w formularzu
        self.fields['date_joined'].widget = forms.HiddenInput()
        self.fields['date_joined'].required = False

        from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # Tylko te pola chcemy edytować
        exclude = ['date_joined', 'last_login']  # Wyklucz niepotrzebne pola


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


# Formularz do resetowania hasła
class ResetPasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})


# Formularz do postów na blogu
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'rows': 5})


# Formularz do komentarzy w postach na blogu
class CommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment  # Używaj BlogComment zamiast PostComment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'rows': 3})


# Formularz do wątków na forum
class ThreadForm(forms.ModelForm):
    class Meta:
        model = ForumThread
        fields = ['title', 'content']

    def __init__(self, *args, **kwargs):
        super(ThreadForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'rows': 5})


# Formularz do komentarzy w wątkach forum
class ForumCommentForm(forms.ModelForm):
    class Meta:
        model = ForumComment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(ForumCommentForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'rows': 3})