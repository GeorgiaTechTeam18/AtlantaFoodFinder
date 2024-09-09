from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request,'UserAuth/index.html')

def register(request):
    return render(request,'UserAuth/register.html')

