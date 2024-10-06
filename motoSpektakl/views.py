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
from .models import Post, ForumComment, BlogComment
from .forms import PostForm, CommentForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, ForumComment, ForumThread, ForumVote
from .forms import RegisterForm, EditProfileForm, EditPasswordForm, UserChangeForm, CustomUserChangeForm
from .models import PostVote, ForumVote
from .models import ForumThread
from .forms import ThreadForm  # Nowy formularz, który stworzymy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import logging

# Logger do logowania błędów
logger = logging.getLogger(__name__)

# Widok dla strony głównej (index)
def index(request):
    return render(request, 'index.html')

# Widok strony konta użytkownika
def account(request):
    return render(request, 'account.html')

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

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import EditProfileForm
from django.contrib.auth.forms import UserChangeForm

# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import EditProfileForm, UserChangeForm

@login_required
def edit_profile(request):
    user_instance = request.user
    profile_instance, created = UserProfile.objects.get_or_create(user=user_instance)

    if request.method == 'POST':
        # Użyj `CustomUserChangeForm` zamiast domyślnego `UserChangeForm`
        user_form = CustomUserChangeForm(request.POST, instance=user_instance)
        profile_form = EditProfileForm(request.POST, request.FILES, instance=profile_instance)

        if user_form.is_valid() and profile_form.is_valid():
            # Sprawdzenie, czy checkbox "Usuń zdjęcie" jest zaznaczony
            if 'profile_picture-clear' in request.POST:
                profile_instance.profile_picture.delete()  # Usuń zdjęcie z serwera
                profile_instance.profile_picture = None  # Ustaw pole na None
            
            # Debugowanie formularzy
            print("Dane formularza użytkownika: ", user_form.cleaned_data)
            print("Dane formularza profilu: ", profile_form.cleaned_data)

            # Zapisanie zmian w profilach użytkownika i UserProfile
            user_form.save()
            profile_form.save()
            
            # Debugowanie zapisanego profilu
            print("Profil po zapisaniu: ", profile_instance.description, profile_instance.vehicle)

            messages.success(request, 'Twój profil został zaktualizowany.')
            return redirect('edit_profile')
        else:
            print("Błędy formularza użytkownika: ", user_form.errors)
            print("Błędy formularza profilu: ", profile_form.errors)
            messages.error(request, 'Wystąpiły błędy w formularzu. Sprawdź swoje dane.')
    else:
        # Użyj `CustomUserChangeForm` zamiast `UserChangeForm`
        user_form = CustomUserChangeForm(instance=user_instance)
        profile_form = EditProfileForm(instance=profile_instance)

    return render(request, 'edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})

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

# Widok bloga
def blog(request):
    category = request.GET.get('category')  # Pobranie wybranej kategorii z URL
    sort_order = request.GET.get('sort_order')  # Pobranie wybranego porządku sortowania z URL
    search_query = request.GET.get('search', '')  # Pobranie zapytania wyszukiwania z parametru GET

    posts = Post.objects.all()

    # Filtrowanie według kategorii, jeśli podano
    if category:
        posts = posts.filter(category=category)

    # Filtrowanie według wyszukiwanego hasła w tytule lub nazwie użytkownika
    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(author__username__icontains=search_query))

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
        'search_query': search_query,
    }

    return render(request, 'blog.html', context)

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
from .models import Post, ForumComment, BlogComment, UserProfile
from .forms import PostForm, CommentForm
import logging

# Logger do logowania błędów
logger = logging.getLogger(__name__)

def blog_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()

    # Pobranie profilu autora posta
    try:
        user_profile = post.author.userprofile
        print(f"User Profile found: {user_profile}")  # Sprawdzenie, czy profil został pobrany
        print(f"Description: {user_profile.description}")  # Wyświetlenie wartości pola `description`
        print(f"Vehicle: {user_profile.vehicle}")  # Wyświetlenie wartości pola `vehicle`
    except UserProfile.DoesNotExist:
        user_profile = None
        print("User profile not found.")  # Jeśli profil nie istnieje

    # Debugowanie przekazywanych wartości
    profile_picture_url = user_profile.profile_picture.url if user_profile and user_profile.profile_picture else None
    description = user_profile.description if user_profile else 'Brak opisu'
    vehicle = user_profile.vehicle if user_profile else 'Brak informacji o pojeździe'
    
    print(f"Profile Picture URL: {profile_picture_url}")
    print(f"Description: {description}")
    print(f"Vehicle: {vehicle}")

    # Inicjalizacja formularza komentarza
    form = CommentForm()

    # Obsługa dodawania nowego komentarza
    if request.method == 'POST':
        print("Dane POST: ", request.POST)
        form = CommentForm(request.POST)
        if form.is_valid():
            print("Formularz jest poprawny.")
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Komentarz został dodany.')
            return redirect('blog_detail', post_id=post_id)
        else:
            print("Formularz jest niepoprawny: ", form.errors)
            messages.error(request, 'Błąd przy dodawaniu komentarza.')

    # Przekazanie dodatkowych informacji do kontekstu
    context = {
        'post': post,
        'comments': comments,
        'form': form,  # Przekazanie formularza do kontekstu
        'profile_picture': profile_picture_url,
        'description': description,
        'vehicle': vehicle,
    }

    return render(request, 'blog_detail.html', context)

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
    existing_vote = PostVote.objects.filter(post=post, user=request.user).first()

    if existing_vote:
        # Jeśli użytkownik już zagłosował, zmień typ głosu tylko jeśli jest inny
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
        # Dodaj nowy głos
        PostVote.objects.create(post=post, user=request.user, vote_type=vote_type)
        if vote_type == 'like':
            post.add_like()
        else:
            post.add_dislike()

    return redirect('blog_detail', post_id=post.id)


# Widok dla panelu administracyjnego (admin_panel)
@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)  # Tylko admin i moderator mogą mieć dostęp
def admin_panel(request):
    posts = Post.objects.all()
    comments = ForumComment.objects.all()
    return render(request, 'admin_panel.html', {'posts': posts, 'comments': comments})

# Widok edytowania komentarza
@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id)
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
    comment = get_object_or_404(ForumComment, id=comment_id)
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
    comments = ForumComment.objects.all()  # Pobierz wszystkie komentarze
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


@login_required
def edit_thread(request, thread_id):
    thread = get_object_or_404(ForumThread, id=thread_id)
    # Sprawdzenie, czy użytkownik jest autorem wątku
    if request.user != thread.author:
        messages.error(request, "Nie masz uprawnień do edycji tego wątku.")
        return redirect('forum_detail', thread_id=thread_id)

    if request.method == 'POST':
        form = ThreadForm(request.POST, instance=thread)
        if form.is_valid():
            form.save()
            messages.success(request, "Wątek został pomyślnie zaktualizowany.")
            return redirect('forum_detail', thread_id=thread.id)
    else:
        form = ThreadForm(instance=thread)

    return render(request, 'edit_thread.html', {'form': form, 'thread': thread})

@login_required
def delete_thread(request, thread_id):
    thread = get_object_or_404(ForumThread, id=thread_id)
    # Sprawdzenie, czy użytkownik jest autorem wątku lub administratorem
    if request.user != thread.author and not request.user.is_staff:
        messages.error(request, "Nie masz uprawnień do usunięcia tego wątku.")
        return redirect('forum_detail', thread_id=thread_id)

    if request.method == 'POST':
        thread.delete()
        messages.success(request, "Wątek został usunięty.")
        return redirect('forum')

    return render(request, 'delete_thread.html', {'thread': thread})

# Widok forum dla wszystkich użytkowników
def forum(request):
    search_query = request.GET.get('search', '')  # Pobranie zapytania wyszukiwania z parametru GET
    sort_order = request.GET.get('sort', 'newest')  # Pobranie opcji sortowania z parametru GET

    threads = ForumThread.objects.all()

    # Filtrowanie według zapytania wyszukiwania
    if search_query:
        threads = threads.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

    # Sortowanie według wybranej opcji
    if sort_order == 'oldest':
        threads = threads.order_by('created_at')  # Sortowanie od najstarszych
    else:
        threads = threads.order_by('-created_at')  # Sortowanie od najnowszych (domyślnie)

    # Implementacja paginacji (5 wątków na stronę)
    paginator = Paginator(threads, 5)
    page = request.GET.get('page')
    try:
        threads = paginator.page(page)
    except PageNotAnInteger:
        threads = paginator.page(1)
    except EmptyPage:
        threads = paginator.page(paginator.num_pages)

    context = {
        'threads': threads,
        'search_query': search_query,
        'sort_order': sort_order,
    }

    return render(request, 'forum.html', context)

def forum_detail(request, thread_id):
    thread = get_object_or_404(ForumThread, id=thread_id)
    comments = thread.comments.all()
    
    # Sprawdzenie, czy użytkownik jest autorem wątku lub administratorem
    can_edit_or_delete = request.user == thread.author or request.user.is_staff

    # Przekazanie dodatkowych informacji dotyczących profilu autora komentarza
    for comment in comments:
        comment.author_profile = comment.author.userprofile  # Ładowanie UserProfile dla autora komentarza
    
    context = {
        'thread': thread,
        'comments': comments,
        'can_edit_or_delete': can_edit_or_delete
    }
    return render(request, 'forum_detail.html', context)

# Widok dodawania nowego wątku (dla zalogowanych użytkowników)
@login_required
def add_thread(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            new_thread = form.save(commit=False)
            new_thread.author = request.user
            new_thread.save()
            messages.success(request, "Nowy wątek został dodany pomyślnie!")
            return redirect('forum_detail', thread_id=new_thread.id)
    else:
        form = ThreadForm()
    return render(request, 'add_thread.html', {'form': form})

# Widok edytowania wątku (dla autorów wątku)
@login_required
def edit_thread(request, thread_id):
    thread = get_object_or_404(ForumThread, id=thread_id)
    if request.user != thread.author:
        messages.error(request, "Nie masz uprawnień do edytowania tego wątku.")
        return redirect('forum_detail', thread_id=thread.id)

    if request.method == 'POST':
        form = ThreadForm(request.POST, instance=thread)
        if form.is_valid():
            form.save()
            messages.success(request, "Wątek został zaktualizowany.")
            return redirect('forum_detail', thread_id=thread.id)
    else:
        form = ThreadForm(instance=thread)
    return render(request, 'edit_thread.html', {'form': form, 'thread': thread})

# Widok usuwania wątku (dla autorów wątku lub adminów)
@login_required
def delete_thread(request, thread_id):
    thread = get_object_or_404(ForumThread, id=thread_id)
    if request.user != thread.author and not request.user.is_staff:
        messages.error(request, "Nie masz uprawnień do usunięcia tego wątku.")
        return redirect('forum_detail', thread_id=thread.id)

    if request.method == 'POST':
        thread.delete()
        messages.success(request, "Wątek został usunięty.")
        return redirect('forum')
    return render(request, 'delete_thread.html', {'thread': thread})

# Widok dodawania nowego komentarza (dla zalogowanych użytkowników)
@login_required
def add_comment(request, thread_id):
    thread = get_object_or_404(ForumThread, id=thread_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            ForumComment.objects.create(content=content, author=request.user, thread=thread)
            return redirect('forum_detail', thread_id=thread.id)
    return redirect('forum_detail', thread_id=thread.id)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id)
    # Sprawdzenie, czy użytkownik jest autorem komentarza lub adminem
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, "Nie masz uprawnień do usunięcia tego komentarza.")
        return redirect('forum_detail', thread_id=comment.thread.id)

    thread_id = comment.thread.id  # Zapisujemy `thread_id`, ponieważ `comment` zostanie usunięty
    comment.delete()
    messages.success(request, "Komentarz został pomyślnie usunięty.")
    return redirect('forum_detail', thread_id=thread_id)

@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id)
    # Sprawdzenie, czy użytkownik jest autorem komentarza lub adminem
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, "Nie masz uprawnień do edytowania tego komentarza.")
        return redirect('forum_detail', thread_id=comment.thread.id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Komentarz został zaktualizowany.")
            return redirect('forum_detail', thread_id=comment.thread.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'edit_comment.html', {'form': form, 'comment': comment})

@login_required
def blog_comment_delete(request, post_id, comment_id):
    comment = get_object_or_404(BlogComment, id=comment_id, post_id=post_id)
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, "Nie masz uprawnień do usunięcia tego komentarza.")
        return redirect('blog_detail', post_id=comment.post.id)

    comment.delete()
    messages.success(request, "Komentarz został pomyślnie usunięty.")
    return redirect('blog_detail', post_id=post_id)

@login_required
def blog_comment_edit(request, post_id, comment_id):
    comment = get_object_or_404(BlogComment, id=comment_id, post_id=post_id)
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, "Nie masz uprawnień do edytowania tego komentarza.")
        return redirect('blog_detail', post_id=comment.post.id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Komentarz został zaktualizowany.")
            return redirect('blog_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'edit_comment.html', {'form': form, 'comment': comment})

# Widok dodawania głosów dla wątków forum - tylko dla zalogowanych użytkowników
@login_required
def vote_on_thread(request, thread_id, vote_type):
    thread = get_object_or_404(ForumThread, id=thread_id)
    existing_vote = ForumVote.objects.filter(thread=thread, user=request.user).first()

    if existing_vote:
        if existing_vote.vote_type != vote_type:
            if vote_type == 'like':
                thread.likes += 1
                if thread.dislikes > 0:
                    thread.dislikes -= 1
            else:
                thread.dislikes += 1
                if thread.likes > 0:
                    thread.likes -= 1
            existing_vote.vote_type = vote_type
            existing_vote.save()
    else:
        ForumVote.objects.create(thread=thread, user=request.user, vote_type=vote_type)
        if vote_type == 'like':
            thread.likes += 1
        else:
            thread.dislikes += 1

    thread.save()
    return redirect('forum_detail', thread_id=thread.id)