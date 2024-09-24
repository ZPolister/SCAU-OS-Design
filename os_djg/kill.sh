#!/bin/bash

# 获取所有 manage.py runserver 的进程号
PIDS=$(pgrep -f 'manage.py runserver')

# 检查是否找到进程
if [ -n "$PIDS" ]; then
  echo "Found PIDs: $PIDS"
  
  # 循环处理每个 PID
  for pid in $PIDS; do
    # 检查进程是否仍在运行
    if ps -p $pid > /dev/null; then
      echo "Killing process $pid"
      kill -9 $pid  # 杀掉进程
      sleep 0.5     # 等待 0.5 秒
    else
      echo "Process $pid is not running"
    fi
  done
else
  echo "No running manage.py runserver processes found."
fi

