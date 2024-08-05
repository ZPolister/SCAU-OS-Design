"""
Global Language
"""
text = {
    'en': {
        'disk.dir_not_found': 'Directory not found',
        'disk.file_not_found': 'File not found',
        'disk.not_enough_space': 'Not enough space',

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
