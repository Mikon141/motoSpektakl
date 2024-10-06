from django.db import models
from django.contrib.auth.models import User

# Definicje modeli

# Model wątku na forum
class ForumThread(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.PositiveIntegerField(default=0)  # Dodanie pola "likes"
    dislikes = models.PositiveIntegerField(default=0)  # Dodanie pola "dislikes"

    def __str__(self):
        return self.title


# Model komentarza na forum
class ForumComment(models.Model):
    thread = models.ForeignKey(ForumThread, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Komentarz {self.author.username} w wątku {self.thread.title}"


# Model głosów na forum
class ForumVote(models.Model):
    VOTE_CHOICES = [
        ('like', 'Fajne'),
        ('dislike', 'Nie fajne')
    ]
    thread = models.ForeignKey(ForumThread, related_name='votes', on_delete=models.CASCADE, default=1)  # Domyślnie przypisany wątek
    user = models.ForeignKey(User, related_name='forum_votes', on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('thread', 'user')  # Każdy użytkownik może tylko raz zagłosować na dany wątek

    def __str__(self):
        return f"{self.user.username} zagłosował na {self.vote_type} dla {self.thread.title}"


# Model posta na blogu
class Post(models.Model):
    CATEGORY_CHOICES = [
        ('nowości', 'Nowości motoryzacyjne'),
        ('recenzje', 'Recenzje pojazdów'),
        ('poradniki', 'Poradniki techniczne'),
        ('historie', 'Moje prywatne historie'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='nowości')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    # Dodane metody do obsługi głosów
    def add_like(self):
        """Dodaj jeden punkt do liczby polubień."""
        self.likes += 1
        self.save()

    def remove_like(self):
        """Odejmij jeden punkt od liczby polubień, jeśli to możliwe."""
        if self.likes > 0:
            self.likes -= 1
            self.save()

    def add_dislike(self):
        """Dodaj jeden punkt do liczby niepolubień."""
        self.dislikes += 1
        self.save()

    def remove_dislike(self):
        """Odejmij jeden punkt od liczby niepolubień, jeśli to możliwe."""
        if self.dislikes > 0:
            self.dislikes -= 1
            self.save()


# Model komentarza do posta na blogu
class BlogComment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Komentarz {self.author.username} do posta {self.post.title}"


# Model głosów na blogu
class PostVote(models.Model):
    VOTE_CHOICES = [
        ('like', 'Fajne'),
        ('dislike', 'Nie fajne')
    ]
    post = models.ForeignKey(Post, related_name='votes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='votes', on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('post', 'user')  # Każdy użytkownik może tylko raz zagłosować na dany post

    def __str__(self):
        return f"{self.user.username} zagłosował na {self.vote_type} dla {self.post.title}"


# Model profilu użytkownika
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default_profile.jpg', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    vehicle = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username