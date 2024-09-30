from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.models import User, Group
from django.contrib.auth import views as auth_views
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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q  # Importowanie narzędzia do wyszukiwania
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Vote
from .forms import RegisterForm, EditProfileForm, EditPasswordForm
import logging

# Logger do logowania błędów
logger = logging.getLogger(__name__)

# Widok dla strony głównej (index)
def index(request):
    return render(request, 'index.html')

# Widok strony konta użytkownika
def account(request):
    return render(request, 'account.html')

# Widok bloga
def blog(request):
    return render(request, 'blog.html')

# Widok forum
def forum(request):
    return render(request, 'forum.html')

# Rejestracja użytkownika
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Przypisanie roli admina dla wybranego użytkownika
            if user.email == "tobimm7@gmail.com":
                user.is_superuser = True
                user.is_staff = True
            else:
                user.is_superuser = False
                user.is_staff = False

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
            messages.error(request, 'Formularz zawiera błędy. Proszę sprawdzić dane.')
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
        
        # Sprawdzamy, czy login_input to e-mail czy login
        try:
            validate_email(login_input)
            user = User.objects.get(email=login_input)
            username = user.username
        except (ValidationError, User.DoesNotExist):
            username = login_input
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('account')
        else:
            messages.error(request, 'Login, adres e-mail lub hasło są nieprawidłowe.')

    return render(request, 'account.html')

# Edycja profilu
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Twój profil został zaktualizowany.')
            return redirect('edit_profile')
        else:
            messages.error(request, 'Wystąpiły błędy w formularzu. Sprawdź swoje dane.')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})

# Zmiana hasła
@login_required
def change_password(request):
    if request.method == 'POST':
        form = EditPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Hasło zostało zmienione pomyślnie.')
            return redirect('edit_profile')
        else:
            for field, errors in form.errors.items():
                if 'old_password' in field:
                    messages.error(request, 'Stare hasło jest nieprawidłowe.')
    else:
        form = EditPasswordForm(request.user)

    return render(request, 'change_password.html', {'form': form})

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'reset_password_confirm.html'  # Upewnij się, że używasz swojego szablonu

    def form_invalid(self, form):
        # Wyciąganie błędów z formularza i przenoszenie ich do sekcji messages
        return super().form_invalid(form)

# Sprawdza, czy użytkownik jest administratorem
def is_admin(user):
    return user.is_superuser

# Widok zarządzania użytkownikami, dostępny tylko dla admina
@user_passes_test(is_admin)
def account_management(request):
    search_query = request.GET.get('search', '')
    users = User.objects.filter(username__icontains=search_query)  # Możliwość filtrowania użytkowników
    return render(request, 'account_management.html', {'users': users})

# Promowanie lub degradowanie użytkownika do/z roli admina
@user_passes_test(is_admin)
def toggle_admin(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_superuser = not user.is_superuser
    user.is_staff = user.is_superuser
    user.save()
    return redirect('account_management')

# Aktywowanie lub dezaktywowanie konta użytkownika
@user_passes_test(is_admin)
def toggle_active(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('account_management')

# Usuwanie użytkownika
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('account_management')

@login_required
@user_passes_test(is_admin)
def update_user_role(request, user_id):
    user = User.objects.get(pk=user_id)
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        
        # Usuwamy użytkownika ze wszystkich grup i dodajemy do nowej
        user.groups.clear()
        if new_role == 'admin':
            group = Group.objects.get(name='Admin')
        elif new_role == 'moderator':
            group = Group.objects.get(name='Moderator')
        else:
            group = Group.objects.get(name='User')
        
        user.groups.add(group)
        user.save()
        
        messages.success(request, f"Rola użytkownika {user.username} została zmieniona na {new_role}.")
        return redirect('account_management')

    return render(request, 'update_user_role.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def toggle_user_activation(request, user_id):
    user = User.objects.get(pk=user_id)
    
    # Odwracamy status aktywności użytkownika
    user.is_active = not user.is_active
    user.save()
    
    if user.is_active:
        messages.success(request, f"Konto użytkownika {user.username} zostało odblokowane.")
    else:
        messages.success(request, f"Konto użytkownika {user.username} zostało zablokowane.")
    
    return redirect('account_management')

# Utworzenie grup, jeśli jeszcze nie istnieją
def create_default_groups():
    group_names = ['Admin', 'Moderator', 'User']
    for group_name in group_names:
        Group.objects.get_or_create(name=group_name)

# Wywołaj tę funkcję w odpowiednim miejscu, np. w widoku głównym
create_default_groups()

def account_management(request):
    search_query = request.GET.get('search', '')
    users = User.objects.filter(username__icontains=search_query)  # Możliwość filtrowania użytkowników
    return render(request, 'account_management.html', {'users': users})

def blog(request):
    category = request.GET.get('category')  # Pobranie wybranej kategorii z URL
    sort_order = request.GET.get('sort_order')  # Pobranie wybranego porządku sortowania z URL

    posts = Post.objects.all()

    # Filtrowanie według kategorii, jeśli podano
    if category:
        posts = posts.filter(category=category)

    # Sortowanie według wybranej opcji
    if sort_order == 'oldest':
        posts = posts.order_by('created_at')  # Sortuj od najstarszych
    else:  # Default lub gdy sort_order == 'newest'
        posts = posts.order_by('-created_at')  # Sortuj od najnowszych

    # Paginacja - 3 posty na stronę
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'category': category,
        'sort_order': sort_order,
    }

    return render(request, 'blog.html', context)

def blog_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()  # Pobieramy wszystkie komentarze dla danego posta
    
    # Obsługa dodawania komentarza
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog_detail', post_id=post.id)
    else:
        form = CommentForm()

    return render(request, 'blog_detail.html', {'post': post, 'comments': comments, 'form': form})

# Tworzenie nowego posta
@login_required
def blog_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog_list')
    else:
        form = PostForm()
    return render(request, 'blog_create.html', {'form': form})

def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.likes += 1
    post.save()
    return redirect('blog_detail', post_id=post.id)

def post_dislike(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.dislikes += 1
    post.save()
    return redirect('blog_detail', post_id=post.id)

@login_required
def add_vote(request, post_id, vote_type):
    post = get_object_or_404(Post, id=post_id)
    existing_vote = Vote.objects.filter(post=post, user=request.user).first()

    # Sprawdzamy, czy użytkownik już zagłosował
    if existing_vote:
        # Jeśli istnieje głos i użytkownik zagłosował na coś innego, aktualizujemy
        if existing_vote.vote_type != vote_type:
            if vote_type == 'like':
                post.add_like()
                post.remove_dislike()
            else:
                post.add_dislike()
                post.remove_like()
            existing_vote.vote_type = vote_type
            existing_vote.save()
    else:
        # Jeśli nie ma istniejącego głosu, dodajemy nowy głos
        Vote.objects.create(post=post, user=request.user, vote_type=vote_type)
        if vote_type == 'like':
            post.add_like()
        else:
            post.add_dislike()

    return redirect('blog_detail', post_id=post_id)

# Widok dla panelu administracyjnego (admin_panel)
@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)  # Tylko admin i moderator mogą mieć dostęp
def admin_panel(request):
    posts = Post.objects.all()
    comments = Comment.objects.all()
    return render(request, 'admin_panel.html', {'posts': posts, 'comments': comments})

# Widok edytowania komentarza
@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    # Sprawdzenie, czy użytkownik jest autorem komentarza lub adminem
    if request.user != comment.author and not request.user.is_staff:
        return HttpResponse("Nie masz uprawnień do edytowania tego komentarza.", status=403)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog_detail', post_id=comment.post.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'edit_comment.html', {'form': form, 'comment': comment})

# Widok usuwania komentarza
@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    # Sprawdzenie, czy użytkownik jest autorem komentarza lub adminem
    if request.user != comment.author and not request.user.is_staff:
        return HttpResponse("Nie masz uprawnień do usunięcia tego komentarza.", status=403)

    post_id = comment.post.id
    comment.delete()
    return redirect('blog_detail', post_id=post_id)

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def blog_management(request):
    posts = Post.objects.all()  # Pobierz wszystkie posty
    comments = Comment.objects.all()  # Pobierz wszystkie komentarze
    return render(request, 'blog_management.html', {'posts': posts, 'comments': comments})


@staff_member_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_post.html', {'form': form, 'post': post})

@staff_member_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('blog_management')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Post
from .forms import PostForm

# Widok edycji postu
@staff_member_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'edit_post.html', {'form': form, 'post': post})

# Widok usuwania postu
@staff_member_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('blog_management')

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from .models import Post

@staff_member_required
def blog_management(request):
    posts = Post.objects.all()
    return render(request, 'blog_management.html', {'posts': posts})

# motoSpektakl/views.py

# Widok główny forum
def forum(request):
    return render(request, 'forum.html')

# Widok szczegółów wątku forum
def forum_detail(request, thread_id):
    # Tu można dodać logikę do pobierania szczegółów wątku z bazy danych
    # Na razie zwrócimy tylko prosty placeholder
    context = {'thread_id': thread_id}
    return render(request, 'forum_detail.html', context)