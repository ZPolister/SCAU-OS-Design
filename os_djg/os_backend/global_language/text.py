"""
Global Language
"""
text = {
    'en': {
        'disk.success': 'Success',

        # 文件操作信息
        'disk.directory_not_found': 'Directory not found',
        'disk.file_already_exists': 'File already exists',
        'disk.file_created': 'File created',
        'disk.file_not_found': 'File not found',
        'disk.not_enough_space': 'Not enough space',
        'disk.could_not_copy_directory': 'Could not copy directory',

        'disk.parent_directory_not_found': 'Parent directory not found',
        'disk.directory_already_exists': 'Directory already exists',
        'disk.directory_not_empty': 'Directory not empty',

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
        'disk.success': '成功',

        # 文件操作信息
        'disk.directory_not_found': '目录未找到',
        'disk.file_already_exists': '文件已存在',
        'disk.file_created': '文件已创建',
        'disk.file_not_found': '文件未找到',
        'disk.not_enough_space': '空间不足',
        'disk.could_not_copy_directory': '无法复制目录',

        'disk.parent_directory_not_found': '未找到父目录',
        'disk.directory_already_exists': '目录已存在',
        'disk.directory_not_empty': '目录非空',

        # 移动操作
        'disk.illegal_move': '非法移动',
        'disk.not_found_src': '源文件未找到',
        'disk.not_found_dst': '目标未找到',
        'disk.already_exists': '文件（目录）已存在',
        'disk.move_failed': '移动失败',

        # 格式化
        'disk.illegal_attribute_value': '非法属性值',
        'disk.not_found_entry': '条目未找到',
    },

    'jp': {
        'disk.success': '成功',

        # ファイル操作情報
        'disk.directory_not_found': 'ディレクトリが見つかりません',
        'disk.file_already_exists': 'ファイルはすでに存在します',
        'disk.file_created': 'ファイルが作成されました',
        'disk.file_not_found': 'ファイルが見つかりません',
        'disk.not_enough_space': 'スペースが足りません',
        'disk.could_not_copy_directory': 'ディレクトリをコピーできませんでした',

        'disk.parent_directory_not_found': '親ディレクトリが見つかりません',
        'disk.directory_already_exists': 'ディレクトリはすでに存在します',
        'disk.directory_not_empty': 'ディレクトリが空ではありません',

        # 移動操作
        'disk.illegal_move': '不正な移動',
        'disk.not_found_src': 'ソースが見つかりません',
        'disk.not_found_dst': '宛先が見つかりません',
        'disk.already_exists': 'ファイル（ディレクトリ）はすでに存在します',
        'disk.move_failed': '移動に失敗しました',

        # フォーマット
        'disk.illegal_attribute_value': '不正な属性値',
        'disk.not_found_entry': 'エントリが見つかりません',
    },

}

default_language = 'en'
_language = 'jp'


def get_text(key: str):
    return text[_language][key] if text[_language][key] else text[default_language][key]


def set_language(lang: str):
    global _language
    _language = lang
