from django.shortcuts import render


def bienvenida(request):
    return render(request, 'noticias/bienvenida.html')
