from django.contrib import admin
from .models import Post, ForumComment, ForumThread, ForumVote
from .models import UserProfile

admin.site.register(Post)
admin.site.register(ForumComment)
admin.site.register(ForumThread)
admin.site.register(ForumVote)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture')

admin.site.register(UserProfile, UserProfileAdmin)