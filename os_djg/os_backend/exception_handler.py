from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from os_backend.response_format import response_format_data
from os_backend.logger import log

import traceback


class GlobalExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        log.error(str(exception))
        traceback.print_exc()
        return JsonResponse(response_format_data(500, str(exception)), status=200)
