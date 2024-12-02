"""os_djg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

import os_backend.routing
from os_backend import views

urlpatterns = [
    path("test", views.test, name="test"),
    path("ls", views.cmd_ls, name="ls"),
    path("create", views.cmd_create, name="create"),
    path("rmdir", views.cmd_rmdir, name="rmdir"),
    path("delete_file", views.cmd_delete_file, name="delete_file"),
    path("type", views.cmd_type, name="type"),
    path("copy", views.cmd_copy, name="copy"),
    path("mkdir", views.cmd_mkdir, name="mkdir"),
    path("run", views.cmd_run, name="run"),
    path("deldir", views.cmd_deldir, name="deldir"),
    path("move", views.cmd_move, name="move"),
    path("format", views.cmd_format, name="format"),
    path("change_attribute", views.cmd_change_attribute, name="change_attribute"),
    path("change_language", views.cmd_change_language, name="change_language"),

    path("export_result", views.export_csv, name="export_result"),

    # websocket
    path('ws/os_process_ws/', include(os_backend.routing.websocket_urlpatterns)),
]
