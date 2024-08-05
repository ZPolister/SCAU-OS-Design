"""
 返回封装
"""

res_template = {
    'code': 200,
    'msg': 'success',
    'data': None
}


def response_format_data(code=200, msg='success', data=None):
    res = res_template
    res['code'] = code
    res['msg'] = msg
    res['data'] = data
    return res
