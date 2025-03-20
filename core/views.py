from django.shortcuts import render

def base(request):
    return render(request, 'index.html')

# Create your views here.
