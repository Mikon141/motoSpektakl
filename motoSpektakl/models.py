from django.db import models
from django.contrib.auth.models import User

# Blog Models

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('nowości', 'Nowości motoryzacyjne'),
        ('recenzje', 'Recenzje pojazdów'),
        ('poradniki', 'Poradniki techniczne'),
        ('historie', 'Moje prywatne historie'),
    ]

    title = models.CharField(max_length=200)  # Tytuł postu
    content = models.TextField()  # Treść postu
    image = models.ImageField(upload_to='images/', null=True, blank=True)  # Zdjęcie postu
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Autor postu
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='nowości')  # Kategoria postu
    created_at = models.DateTimeField(auto_now_add=True)  # Data utworzenia
    updated_at = models.DateTimeField(auto_now=True)  # Data ostatniej aktualizacji
    
    # Pola dla liczników "fajne" i "nie fajne"
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    # Metody do aktualizacji głosów
    def add_like(self):
        self.likes += 1
        self.save()

    def add_dislike(self):
        self.dislikes += 1
        self.save()

    def remove_like(self):
        if self.likes > 0:
            self.likes -= 1
            self.save()

    def remove_dislike(self):
        if self.dislikes > 0:
            self.dislikes -= 1
            self.save()

class PostComment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'motoSpektakl_postcomment'

    def __str__(self):
        return f"Komentarz {self.author.username} na {self.post.title}"

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


# Forum Models


# Forum Models

# Model reprezentujący wątek na forum
class ForumThread(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Model reprezentujący komentarze w wątku
class ForumComment(models.Model):
    thread = models.ForeignKey(ForumThread, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.thread}"

class ForumPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class ForumVote(models.Model):
    VOTE_TYPES = (
        ('like', 'Like'),
        ('dislike', 'Dislike')
    )
    vote_type = models.CharField(choices=VOTE_TYPES, max_length=10)
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')  # Każdy użytkownik może tylko raz zagłosować na dany post

    def __str__(self):
        return f"{self.user.username} - {self.vote_type} - {self.post.title}"

# Model reprezentujący wątek na forum
class ForumThread(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Model reprezentujący komentarze w wątku
class ForumComment(models.Model):
    thread = models.ForeignKey(ForumThread, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.thread}"
    
# Przykładowa modyfikacja modelu UserProfile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default_profile.jpg', null=True, blank=True)

    def __str__(self):
        return self.user.username