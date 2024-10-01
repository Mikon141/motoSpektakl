from django.contrib import admin
from .models import Post, ForumComment, ForumThread, ForumVote

admin.site.register(Post)
admin.site.register(ForumComment)
admin.site.register(ForumThread)  # Zmiana z Thread na ForumThread
admin.site.register(ForumVote)    # Zmiana z Vote na ForumVote