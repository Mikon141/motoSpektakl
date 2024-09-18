from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=250)  # Tytuł postu
    content = models.TextField()  # Treść postu
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Autor postu
    created_at = models.DateTimeField(auto_now_add=True)  # Data utworzenia
    updated_at = models.DateTimeField(auto_now=True)  # Data ostatniej aktualizacji

    def __str__(self):
        return self.title