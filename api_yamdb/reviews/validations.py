import re
import time

from django.conf import settings
from django.core.exceptions import ValidationError

REGULAR_SYMBOLS = re.compile(settings.REGULAR_USERNAME, re.I)


def validate_username(value):
    if value == 'me':
        raise ValidationError('Использовать имя "me" в'
                              ' качестве username запрещено.')
    valid_symbol = " ".join(REGULAR_SYMBOLS.findall(value))
    invalid_symbol = " ".join([
        symbol for symbol in value if symbol not in valid_symbol
    ])
    if len(invalid_symbol) > 0:
        raise ValidationError(
            f'Имя пользователя содержит недопустимые символы: {invalid_symbol}'
        )
    return value


INCORRECT_YEAR = '{year} год не должен превышать текущий!'


def validate_year(value):
    if value > time.localtime()[0]:
        raise ValidationError(INCORRECT_YEAR.format(year=value))
