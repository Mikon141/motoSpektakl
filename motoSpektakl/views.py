from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def account(request):
    return render(request, 'account.html')

def blog(request):
    return render(request, 'blog.html')

def forum(request):
    return render(request, 'forum.html')