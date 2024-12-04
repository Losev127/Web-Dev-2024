from django.shortcuts import render

def index_page(request):
    return render(request, 'index.html')

def create_adv(request):
    return render(request, 'create_adv.html')
