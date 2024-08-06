import json

from django.http import JsonResponse
from os_backend.response_format import response_format_data
from django.views.decorators.csrf import csrf_exempt

import os_backend.logic.disk_manager.disk


def test(request):
    return JsonResponse({'test': 'test'})


def cmd_ls(request):
    """
        列举所有文件信息
    """
    result = os_backend.logic.disk_manager.disk.DiskService.list_directory(request.GET.get("path"))
    return JsonResponse(response_format_data(data=result))


@csrf_exempt
def cmd_create(request):
    """
        创建文件
    """
    request_body = json.loads(request.body)
    result = os_backend.logic.disk_manager.disk.DiskService.create_file(request_body.get('path'), 'e',
                                                                        str(request_body.get('content')).encode('utf-8'))
    return JsonResponse(response_format_data(data=result))
