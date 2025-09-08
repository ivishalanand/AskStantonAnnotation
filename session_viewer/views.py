from django.shortcuts import render

def index(request):
    return render(request, 'session_viewer/index.html')