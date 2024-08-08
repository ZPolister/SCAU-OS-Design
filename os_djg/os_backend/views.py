import json

from django.http import JsonResponse
from os_backend.response_format import response_format_data
from django.views.decorators.csrf import csrf_exempt

from os_backend.logic.disk_manager.disk import DiskService
from os_backend.global_language import text


def test(request):
    return JsonResponse({'test': 'test'})


def cmd_ls(request):
    """
        列举所有文件信息
    """
    result = DiskService.list_directory(request.GET.get("path"))
    return JsonResponse(response_format_data(data=result))


@csrf_exempt
def cmd_create(request):
    """
        创建文件
    """
    request_body = json.loads(request.body)
    result = DiskService.create_file(request_body.get('path'), 'e',
                                     str(request_body.get('content')).encode('utf-8'))
    return JsonResponse(response_format_data(msg=result))


def cmd_rmdir(request):
    """
    删除空文件夹
    Args:
        request: DELETE
    """
    result = DiskService.rmdir(request.GET.get("path"))
    return JsonResponse(response_format_data(msg=result))


def cmd_type(request):
    """
    获取文本内容
    Args:
        request: GET
    """
    flag, result = DiskService.type_file(request.GET.get("path"))
    return JsonResponse(response_format_data(msg=result if not flag else text.get_text('success'),
                                             data=result if flag else None))


def cmd_delete_file(request):
    """
    删除文件
    Args:
        request: DELETE
    """
    flag, result = DiskService.delete_file(request.GET.get("path"))
    return JsonResponse(response_format_data(msg=result))


@csrf_exempt
def cmd_copy(request):
    """
    复制文件
    Args:
        request: POST
    """
    request_body = json.loads(request.body)
    result = DiskService.copy_file(request_body.get('src'), request_body.get('dst'))
    return JsonResponse(response_format_data(msg=result))


@csrf_exempt
def cmd_mkdir(request):
    """
    创建文件夹
    Args:
        request: POST
    """
    request_body = json.loads(request.body)
    result = DiskService.mkdir(request_body.get('path'))
    return JsonResponse(response_format_data(msg=result))


@csrf_exempt
def cmd_run(request):
    """
    运行可执行文件
    Args:
        request: POST
    """
    request_body = json.loads(request.body)
    flag, result = DiskService.run_executable(request_body.get('path'))
    return JsonResponse(response_format_data(msg=result))


def cmd_deldir(request):
    """
    删除文件夹（包括其内容）
    Args:
        request: DELETE
    """
    result = DiskService.delete_directory(request.GET.get("path"))
    return JsonResponse(response_format_data(msg=result))


@csrf_exempt
def cmd_move(request):
    """
    移动文件或目录
    Args:
        request: POST
    """
    request_body = json.loads(request.body)
    result = DiskService.move(request_body.get('src'), request_body.get('dst'))
    return JsonResponse(response_format_data(msg=result))
