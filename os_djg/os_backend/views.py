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
        列举绝对路径下所有文件信息
        Args:
            request: GET
                query:
                    path: 绝对路径

        Examples:
            ls /a -- 列举出"/a"中所有文件信息
    """
    result = DiskService.list_directory(request.GET.get("path"))
    return JsonResponse(response_format_data(data=result))


@csrf_exempt
def cmd_create(request):
    """
        创建文件
        Args:
            request: POST
                body:
                    path: 创建的路径与文件名
                    content: 创建的文件内容

        Examples:
            create  {
                        "path": "/a/1.e",
                        "content": "x++, end"
                    }
            -- 在"/a"下创建内容为 "x++, end"的 "1.e" 文件
    """
    request_body = json.loads(request.body)
    result = DiskService.create_file(request_body.get('path'), 'e',
                                     str(request_body.get('content')).encode('utf-8'))
    return JsonResponse(response_format_data(msg=result))


def cmd_rmdir(request):
    """
    删除空文件夹（只能删除空的文件夹）
    Args:
        request: GET
             query:
                path: 需要删除空文件夹的绝对路径

        Examples:
            rmdir /a -- 删除"/a"中文件夹（如果“/a”存在且为空文件夹）
    """
    result = DiskService.rmdir(request.GET.get("path"))
    return JsonResponse(response_format_data(msg=result))


def cmd_type(request):
    """
    获取指定文件文本内容
    Args:
        request: GET
            query:
                path: 绝对路径

    Examples:
        type /a.e -- 获取"/a.e"文本内容
    """
    flag, result = DiskService.type_file(request.GET.get("path"))
    return JsonResponse(response_format_data(msg=result if not flag else text.get_text('success'),
                                             data=result if flag else None))


def cmd_delete_file(request):
    """
    删除文件（只能删除文件）
    Args:
        request: GET
             query:
                 path: 需要删除的文件的绝对路径

        Examples:
            delete /1/a.e -- 删除"/1/"下"a.e"文件
    """
    flag, result = DiskService.delete_file(request.GET.get("path"))
    return JsonResponse(response_format_data(msg=result))


@csrf_exempt
def cmd_copy(request):
    """
    复制文件
    Args:
        request: POST
                body:
                    src: 源文件路径及其文件名
                    dst: 目标路径（要复制到哪）
    Examples:
        copy    {
                    "src": "/a/1.e",
                    "dst": "/b/d/"
                }
            -- 将"/a"的 "1.e" 文件复制到 "/b/d" 下
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
            body:
                path: 创建文件夹的绝对路径与文件夹名

    Examples:
        mkdir   {
                    "path": "/a/c",
                }
            -- 在"/a"下创建名称为 "c" 的文件夹
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
            body:
                path: 需要执行的文件绝对路径

    Examples:
        run   {
                "path": "/a/c/1.e",
              }
        -- 运行"/a/c"下名称为 "1.e" 的文件
    """
    request_body = json.loads(request.body)
    flag, result = DiskService.run_executable(request_body.get('path'))
    return JsonResponse(response_format_data(msg=result))


def cmd_deldir(request):
    """
    删除文件夹（包括其内容，与rmdir的区别是可以删除非空文件夹，将其下所有文件夹与文件全部删除）
    Args:
        request: GET
             query:
                 path: 需要删除的文件夹的绝对路径

        Examples:
            deldir /1 -- 删除"/1"文件夹（包含内容）
    """
    result = DiskService.delete_directory(request.GET.get("path"))
    return JsonResponse(response_format_data(msg=result))


@csrf_exempt
def cmd_move(request):
    """
    移动文件或目录(可以是文件，也可以是文件夹)
    Args:
        request: POST
                body:
                    src: 源文件（夹）路径及其文件（夹）名
                    dst: 目标路径（要移动到哪）
    Examples:
        move    {
                    "src": "/a/1.e",
                    "dst": "/b/d/"
                }
                 -- 将"/a"的 "1.e" 文件移动到 "/b/d" 下

                {
                    "src": "/a",
                    "dst": "/b/d/"
                }
                 -- 将目录"/a"移动到 "/b/d" 下
    """
    request_body = json.loads(request.body)
    result = DiskService.move(request_body.get('src'), request_body.get('dst'))
    return JsonResponse(response_format_data(msg=result))


def cmd_format(request):
    """
    格式化操作，将所有文件以及文件夹全部删除
    Args:
        request: GET

        Examples:
            没有参数，直接请求即可
    """
    DiskService.format()
    return JsonResponse(response_format_data())


@csrf_exempt
def cmd_change_attribute(request):
    """
    修改文件（目录）属性
    属性值大小为1字节
    Args:
        request: POST
                body:
                    path: 需要修改文件（目录）的绝对路径
                    attribute: 要修改的属性值
    Examples:
        change_attribute    {
                                "path": "/a/1.e",
                                "attribute": "2"
                            }
                 -- 将"/a"的 "1.e" 文件属性修改为"2"
    """
    request_body = json.loads(request.body)
    result = DiskService.change_attribute(request_body.get('path'), request_body.get('attribute'))
    return JsonResponse(response_format_data(msg=result))


@csrf_exempt
def cmd_change_language(request):
    """
    修改信息语言
    目前只有zh/en/jp，参数必须是这三种
    Args:
        request: POST
                body:
                    language: 要修改的语言
    Examples:
        change_language     {
                                language: "zh"
                            }
                 -- 将提示信息语言修改为中文
    """
    lang = json.loads(request.body).get('language')
    if lang in ['zh', 'en', "jp"]:
        text.set_language(lang)
        return JsonResponse(response_format_data())
    else:
        return JsonResponse(response_format_data(401, text.get_text('error')))
