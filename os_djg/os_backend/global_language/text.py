"""
Global Language
"""
text = {
    'en': {
        'disk.success': 'Success',

        # 文件操作信息
        'disk.dir_not_found': 'Directory not found',
        'disk.file_already_exists': 'File already exists',
        'disk.file_created': 'File created',
        'disk.file_not_found': 'File not found',
        'disk.not_enough_space': 'Not enough space',
        'disk.could_not_copy_directory': 'Could not copy directory',

        'disk.parent_directory_not_found': 'Parent directory not found',
        'disk.directory_already_exists': 'Directory already exists',

        # move
        'disk.illegal_move': 'Illegal move',
        'disk.not_found_src': 'Source not found',
        'disk.not_found_dst': 'Destination not found',
        'disk.already_exists': 'File(Directory) already exists',
        'disk.move_failed': 'Move failed',

        # format
        'disk.illegal_attribute_value': 'Illegal attribute value',
        'disk.not_found_entry': 'Entry not found',

    },

    'zh': {

    }
}

default_language = 'en'
_language = 'en'


def get_text(key: str):
    return text[_language][key] if text[_language][key] else text[default_language][key]


def set_language(lang: str):
    global _language
    _language = lang
