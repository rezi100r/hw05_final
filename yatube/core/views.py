from django.shortcuts import render


def page_not_found(request, exception):
    """Функция хендлера 404"""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    """Функция хендлера 403 Check CSRF"""
    return render(request, 'core/403csrf.html')


def server_error(request):
    """Функция хендлера 500"""
    return render(request, 'core/500.html', status=500)


def permission_denied_view(request, exception):
    """Функция хендлера 403"""
    return render(request, 'core/403.html', {'path': request.path}, status=403)
