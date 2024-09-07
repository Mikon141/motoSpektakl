from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
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
            return redirect('login')  # Przekierowanie na stronę logowania
        elif default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Twoje konto zostało aktywowane. Możesz się teraz zalogować.')
            return redirect('account')  # Przekierowanie na stronę konta po aktywacji
        else:
            messages.error(request, 'Link aktywacyjny jest nieprawidłowy lub wygasł.')
            return redirect('register')
    else:
        messages.error(request, 'Link aktywacyjny jest nieprawidłowy.')
        return redirect('register')

# Logowanie za pomocą loginu lub adresu e-mail
def login_view(request):
    if request.method == 'POST':
        login_input = request.POST.get('username')  # Może być loginem lub adresem e-mail
        password = request.POST.get('password')
        
        logger.info(f"Login attempt for: {login_input}")
        
        # Sprawdzamy, czy login_input to e-mail czy login
        try:
            validate_email(login_input)
            # Jeśli to e-mail, znajdź użytkownika po adresie e-mail
            user = User.objects.get(email=login_input)
            username = user.username  # Pobieramy nazwę użytkownika powiązaną z e-mailem
        except ValidationError:
            # Jeśli to nie jest e-mail, zakładamy, że to login
            username = login_input
        except User.DoesNotExist:
            username = None
            logger.error(f"User not found for: {login_input}")
        
        # Autoryzacja użytkownika
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            logger.info(f"User authenticated: {username}")
            login(request, user)
            logger.info(f"User {username} logged in successfully")
            return redirect('account')  # Przekierowanie na stronę konta po zalogowaniu
        else:
            logger.error(f"Authentication failed for: {login_input}")
            return render(request, 'account.html', {'error': 'Nieprawidłowe dane logowania'})
    
    return render(request, 'account.html')