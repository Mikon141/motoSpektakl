from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return self.title