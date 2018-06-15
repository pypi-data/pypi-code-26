from django import template
from ..models import NavMenu

register = template.Library()


@register.inclusion_tag('nav_menus/tags/menu.html', takes_context=True)
def get_nav_menu(context, menu_name, calling_page=None):
    nav_menu = NavMenu.objects.get_or_create(name=menu_name)[0]
    return {
        'calling_page': calling_page,
        'menu_items': nav_menu.menu,
        'menu_name': nav_menu.name,
        'request': context['request'],
    }


@register.simple_tag
def get_nav_menu_json(menu_name):
    nav_menu = NavMenu.objects.get_or_create(name=menu_name)[0]
    return nav_menu.to_json()
