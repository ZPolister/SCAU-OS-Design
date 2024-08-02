"""
Global Language
"""
text = {
    'en': {

    },

    'zh': {

    }
}

default_language = 'en'
_language = 'en'


def get_text(key: str):
    return text[_language][key] if text[_language][key] else text[default_language][key]


def set_language(lang: str):
    _language = lang
