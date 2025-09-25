from django import template

register = template.Library()

'''
Custom Template Filter para ver si el usuario pertenece a un grupo específico.
'''
@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

