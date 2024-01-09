from django import template
from exceptions import CensorTypeException


register = template.Library()


#кортеж плохих слов
BAD_WORDS = ('Редиска', 'петух')


# Фильтр - цензурщик
@register.filter()
def censor(value):
    try:
        # проверка типа передаваемой переменной
        if type(value) is not str:
            raise CensorTypeException

        # Если всё ок с типом - продолжаем
        # проходим по кортежу плохих слов и заменяем их в тексте, если найдём (предварительно отформатировав)
        for word in BAD_WORDS:
            # заменяем слова в маленьком регистре
            value = value.replace(word.lower(), word.lower()[0] + '*' * (len(word) - 1))
            # заменяем слова с большой буквы
            value = value.replace(word.capitalize(), word.capitalize()[0] + '*' * (len(word) - 1))
        return value
    except CensorTypeException:
        print(f'Неверный тип переменной для цензурирования. Передаваемый тип: {type(value)}')
