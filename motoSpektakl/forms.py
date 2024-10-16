from django import forms
from django.forms import FileInput
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm,
    SetPasswordForm,
)
from django.contrib.auth.models import User
from .models import (
    Post,
    BlogComment,
    ForumThread,
    ForumComment,
    UserProfile,
)
import bleach

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

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Nazwa użytkownika',
            'email': 'Adres e-mail',
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        self.fields['date_joined'].widget = forms.HiddenInput()
        self.fields['date_joined'].required = False

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        exclude = ['date_joined', 'last_login']

class EditPasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        super(EditPasswordForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

class ResetPasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image']

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'rows': 5})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})

class CommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'rows': 3})

    def clean_content(self):
        content = self.cleaned_data.get('content')
        content_cleaned = bleach.clean(content, strip=True)
        if len(content_cleaned.strip()) < 5:
            raise forms.ValidationError("Komentarz jest zbyt krótki. Wprowadź pełniejszą treść.")
        if "badword" in content_cleaned.lower():
            raise forms.ValidationError("Komentarz zawiera niedozwolone słowa. Proszę usunąć takie słowa i spróbować ponownie.")
        return content_cleaned

class ThreadForm(forms.ModelForm):
    class Meta:
        model = ForumThread
        fields = ['title', 'content']

    def __init__(self, *args, **kwargs):
        super(ThreadForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'rows': 5})

class ForumCommentForm(forms.ModelForm):
    class Meta:
        model = ForumComment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(ForumCommentForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'rows': 3})

    def clean_content(self):
        content = self.cleaned_data.get('content')
        content_cleaned = bleach.clean(content, strip=True)
        if len(content_cleaned.strip()) < 5:
            raise forms.ValidationError("Komentarz jest zbyt krótki. Wprowadź pełniejszą treść.")
        if "badword" in content_cleaned.lower():
            raise forms.ValidationError("Komentarz zawiera niedozwolone słowa. Proszę usunąć takie słowa i spróbować ponownie.")
        return content_cleaned