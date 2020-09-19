#!/bin/sh
# 开机自启脚本 sudo nohup sh run.sh &
# 等待系统初始化成功
sleep 10
rm -rf /home/root/workspace/helmet/nohup.out
sudo /usr/bin/python /home/root/workspace/helmet/helmet_main_process.py