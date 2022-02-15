from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Переопределенный класс визуализации станицы автора"""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Переопределенный класс визуализации станицы технологии"""

    template_name = 'about/tech.html'
