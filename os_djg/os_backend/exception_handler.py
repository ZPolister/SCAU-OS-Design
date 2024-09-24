from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from os_backend.response_format import response_format_data
import logging

logger = logging.getLogger(__name__)

class GlobalExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        logger.exception("服务器错误")
        return JsonResponse(response_format_data(500, str(exception)), status=200)
