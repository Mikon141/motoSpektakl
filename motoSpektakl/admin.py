from django.contrib import admin
from .models import Post, ForumComment, ForumThread, ForumVote
from .models import UserProfile

admin.site.register(Post)
admin.site.register(ForumComment)
admin.site.register(ForumThread)  # Zmiana z Thread na ForumThread
admin.site.register(ForumVote)    # Zmiana z Vote na ForumVote

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture')  # Dodajemy 'profile_picture' do listy pól wyświetlanych w adminie

admin.site.register(UserProfile, UserProfileAdmin)