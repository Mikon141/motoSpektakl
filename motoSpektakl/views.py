import logging
import smtplib
import bleach

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    login,
    authenticate,
    update_session_auth_hash,
    views as auth_views,
)
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.forms import UserChangeForm
from django.contrib.admin.views.decorators import staff_member_required

from .models import (
    Post,
    ForumComment,
    BlogComment,
    ForumThread,
    ForumVote,
    PostVote,
    UserProfile,
)
from .forms import (
    PostForm,
    CommentForm,
    RegisterForm,
    EditProfileForm,
    EditPasswordForm,
    CustomUserChangeForm,
    ThreadForm,
)

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def account(request):
    return render(request, 'account.html')

def forum(request):
    return render(request, 'forum.html')

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.email == "tobimm7@gmail.com":
                user.is_superuser = True
                user.is_staff = True
            else:
                user.is_superuser = False
                user.is_staff = False
            user.is_active = False
            user.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            activation_link = f"{request.scheme}://{current_site.domain}/activate/{uid}/{token}/"
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
            return redirect('account')
        else:
            messages.error(request, 'Link aktywacyjny jest nieprawidłowy lub wygasł.')
            return redirect('register')
    else:
        messages.error(request, 'Link aktywacyjny jest nieprawidłowy.')
        return redirect('register')

def login_view(request):
    if request.method == 'POST':
        login_input = request.POST.get('username')
        password = request.POST.get('password')
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

@login_required
def edit_profile(request):
    user_instance = request.user
    profile_instance, created = UserProfile.objects.get_or_create(user=user_instance)
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=user_instance)
        profile_form = EditProfileForm(request.POST, request.FILES, instance=profile_instance)
        if user_form.is_valid() and profile_form.is_valid():
            if 'profile_picture-clear' in request.POST:
                profile_instance.profile_picture.delete()
                profile_instance.profile_picture = None
            user_form.save()
            profile_form.save()
            messages.success(request, 'Twój profil został zaktualizowany.')
            return redirect('edit_profile')
        else:
            messages.error(request, 'Wystąpiły błędy w formularzu. Sprawdź swoje dane.')
    else:
        user_form = CustomUserChangeForm(instance=user_instance)
        profile_form = EditProfileForm(instance=profile_instance)
    return render(request, 'edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})

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
    template_name = 'reset_password_confirm.html'
    def form_invalid(self, form):
        return super().form_invalid(form)

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def account_management(request):
    search_query = request.GET.get('search', '')
    users = User.objects.filter(username__icontains=search_query)
    return render(request, 'account_management.html', {'users': users})

@user_passes_test(is_admin)
def toggle_admin(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_superuser = not user.is_superuser
    user.is_staff = user.is_superuser
    user.save()
    return redirect('account_management')

@user_passes_test(is_admin)
def toggle_active(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('account_management')

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
        user.groups.clear()
        if new_role == 'admin':
            group = Group.objects.get(name='Admin')
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
    user.is_active = not user.is_active
    user.save()
    if user.is_active:
        messages.success(request, f"Konto użytkownika {user.username} zostało odblokowane.")
    else:
        messages.success(request, f"Konto użytkownika {user.username} zostało zablokowane.")
    return redirect('account_management')

def create_default_groups():
    group_names = ['Admin', 'User']
    for group_name in group_names:
        Group.objects.get_or_create(name=group_name)

create_default_groups()

def blog(request):
    category = request.GET.get('category')
    sort_order = request.GET.get('sort_order')
    search_query = request.GET.get('search', '')
    posts = Post.objects.all()
    if category:
        posts = posts.filter(category=category)
    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(author__username__icontains=search_query))
    if sort_order == 'oldest':
        posts = posts.order_by('created_at')
    else:
        posts = posts.order_by('-created_at')
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

def blog_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    try:
        user_profile = post.author.userprofile
    except UserProfile.DoesNotExist:
        user_profile = None
    profile_picture_url = user_profile.profile_picture.url if user_profile and user_profile.profile_picture else None
    description = user_profile.description if user_profile else 'Brak opisu'
    vehicle = user_profile.vehicle if user_profile else 'Brak informacji o pojeździe'
    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Komentarz został dodany.')
            return redirect('blog_detail', post_id=post_id)
        else:
            messages.error(request, 'Błąd przy dodawaniu komentarza.')
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'profile_picture': profile_picture_url,
        'description': description,
        'vehicle': vehicle,
    }
    return render(request, 'blog_detail.html', context)

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
        PostVote.objects.create(post=post, user=request.user, vote_type=vote_type)
        if vote_type == 'like':
            post.add_like()
        else:
            post.add_dislike()
    return redirect('blog_detail', post_id=post.id)

@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def admin_panel(request):
    posts = Post.objects.all()
    comments = ForumComment.objects.all()
    return render(request, 'admin_panel.html', {'posts': posts, 'comments': comments})

@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id)
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

@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id)
    if request.user != comment.author and not request.user.is_staff:
        return HttpResponse("Nie masz uprawnień do usunięcia tego komentarza.", status=403)
    post_id = comment.post.id
    comment.delete()
    return redirect('blog_detail', post_id=post_id)

@staff_member_required
def blog_management(request):
    posts = Post.objects.all()
    comments = ForumComment.objects.all()
    return render(request, 'blog_management.html', {'posts': posts, 'comments': comments})

@staff_member_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        
        if form.is_valid():
            # Sprawdzenie, czy użytkownik zaznaczył checkbox usuwający zdjęcie
            if 'clear_image' in request.POST:
                post.image.delete()  # Usunięcie zdjęcia
                post.image = None  # Ustawienie pola na None
                
            form.save()
            messages.success(request, 'Post został zaktualizowany.')
            return redirect('blog_detail', post_id=post.id)
        else:
            messages.error(request, 'Formularz zawiera błędy.')
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_post.html', {'form': form, 'post': post})

@staff_member_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('blog_management')

@login_required
def edit_thread(request, thread_id):
    thread = get_object_or_404(ForumThread, id=thread_id)
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
    if request.user != thread.author and not request.user.is_staff:
        messages.error(request, "Nie masz uprawnień do usunięcia tego wątku.")
        return redirect('forum_detail', thread_id=thread_id)
    if request.method == 'POST':
        thread.delete()
        messages.success(request, "Wątek został usunięty.")
        return redirect('forum')
    return render(request, 'delete_thread.html', {'thread': thread})

def forum(request):
    search_query = request.GET.get('search', '')
    sort_order = request.GET.get('sort', 'newest')
    threads = ForumThread.objects.all()
    if search_query:
        threads = threads.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    if sort_order == 'oldest':
        threads = threads.order_by('created_at')
    else:
        threads = threads.order_by('-created_at')
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
    can_edit_or_delete = request.user == thread.author or request.user.is_staff
    for comment in comments:
        comment.author_profile = comment.author.userprofile
    context = {
        'thread': thread,
        'comments': comments,
        'can_edit_or_delete': can_edit_or_delete
    }
    return render(request, 'forum_detail.html', context)

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

def is_comment_valid(content):
    cleaned_content = bleach.clean(content, tags=[], attributes={}, strip=True)
    if len(cleaned_content.strip()) < 5:
        return False
    return True

@login_required
def add_comment(request, thread_id):
    thread = get_object_or_404(ForumThread, id=thread_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content and is_comment_valid(content):
            ForumComment.objects.create(content=content, author=request.user, thread=thread)
            messages.success(request, 'Komentarz został pomyślnie dodany.')
        else:
            messages.error(request, 'Treść komentarza jest nieodpowiednia lub zbyt krótka.')
    return redirect('forum_detail', thread_id=thread.id)

@login_required
def add_blog_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data.get('content')
            if is_comment_valid(content):
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(request, 'Komentarz został dodany.')
            else:
                messages.error(request, 'Treść komentarza jest nieodpowiednia lub zbyt krótka.')
        else:
            messages.error(request, 'Formularz jest niepoprawny.')
    return redirect('blog_detail', post_id=post.id)

@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id)
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, "Nie masz uprawnień do usunięcia tego komentarza.")
        return redirect('forum_detail', thread_id=comment.thread.id)
    thread_id = comment.thread.id
    comment.delete()
    messages.success(request, "Komentarz został pomyślnie usunięty.")
    return redirect('forum_detail', thread_id=thread_id)

@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id)
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

@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post został pomyślnie dodany!')
            return redirect('blog_management')
    else:
        form = PostForm()
    return render(request, 'add_post.html', {'form': form})