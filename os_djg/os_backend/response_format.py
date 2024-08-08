"""
 返回封装
"""
from os_backend.global_language import text

res_template = {
    'code': 200,
    'msg': text.get_text('success'),
    'data': None
}


def response_format_data(code=200, msg=text.get_text('success'), data=None):
    res = res_template.copy()
    res['code'] = code
    res['msg'] = msg
    res['data'] = data
    return res
