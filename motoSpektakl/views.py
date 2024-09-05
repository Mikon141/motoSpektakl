from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.contrib import messages
from smtplib import SMTPException
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import logging

# Logger do logowania błędów
logger = logging.getLogger(__name__)

# Strony główne
def index(request):
    return render(request, 'index.html')

def account(request):
    return render(request, 'account.html')

def blog(request):
    return render(request, 'blog.html')

def forum(request):
    return render(request, 'forum.html')

# Rejestracja użytkownika
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Konto nieaktywne, dopóki nie zostanie aktywowane
            user.save()

            # Wygenerowanie tokenu aktywacyjnego
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            activation_link = f"{request.scheme}://{current_site.domain}/activate/{uid}/{token}/"

            # Wysłanie e-maila aktywacyjnego
            mail_subject = 'Aktywuj swoje konto'
            message = render_to_string('activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })

            try:
                send_mail(
                    mail_subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Rejestracja pomyślna! Sprawdź swój e-mail, aby aktywować konto.')
                return render(request, "register.html", {"form": form})
            except SMTPException as e:
                logger.error(f"Błąd wysyłania e-maila: {e}")
                messages.error(request, 'Wystąpił problem podczas wysyłania e-maila aktywacyjnego.')
        else:
            print(form.errors)  # Wyświetl błędy w konsoli
            messages.error(request, 'Formularz zawiera błędy. Proszę sprawdzić dane.')
            return render(request, "register.html", {"form": form})
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

# Aktywacja konta po kliknięciu w link aktywacyjny
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None:
        if user.is_active:
            messages.info(request, 'Twoje konto jest już aktywne. Możesz się zalogować.')
            return redirect('login')
        elif default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Twoje konto zostało aktywowane. Możesz się teraz zalogować.')
            return redirect('login')
        else:
            messages.error(request, 'Link aktywacyjny jest nieprawidłowy lub wygasł.')
            return redirect('register')
    else:
        messages.error(request, 'Link aktywacyjny jest nieprawidłowy.')
        return redirect('register')