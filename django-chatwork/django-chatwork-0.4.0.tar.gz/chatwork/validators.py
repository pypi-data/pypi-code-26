import re

from django.core import validators
from django.utils.deconstruct import deconstructible


@deconstructible
class CommaSeparatedListValidator(validators.RegexValidator):
    regex = r'^\w+(?:,\w+)*$'
    message = ',（カンマ）で区切られている必要があります。'
    flags = 0


@deconstructible
class KanaValidator(validators.RegexValidator):
    regex = r'^[{}-{}]+$'.format(chr(0x3040), chr(0x309F))
    message = 'ひらがなで入力してください。'
    flags = 0


@deconstructible
class KeyValidator(validators.RegexValidator):
    regex = r'^[-\w_]+$'
    message = '使用できない文字列が含まれています。半角アルファベットと ' \
              '_（アンダースコア）、-（ハイフン）が使用できます。'
    flags = re.ASCII


@deconstructible
class UidValidator(validators.RegexValidator):
    regex = r'^[a-z]\d{4}[01]\d{5}[a-z]$'
    message = '不正なUIDです。'
    flags = re.ASCII


@deconstructible
class PhoneNumberValidator(validators.RegexValidator):
    """ 電話番号のバリデーション """
    regex = r'^[0-9]+-[0-9]+-[0-9]+$'
    message = 'xxx-xxxx-xxxxのようにハイフン付きで入力してください。'
