#!/usr/bin/python
# -*- coding: UTF-8 -*-
import cv2
import select
import v4l2capture
import time
import threading
import numpy as np
import os
import sys
import socket

from src.helmet_serial import SerialThread
from src.uitl import print_results, draw_results, cast_origin

__all__ = ['video_process']


class VideoThread(threading.Thread):

    def __init__(self, video_device, video_w, video_h, buffer_size, name):
        threading.Thread.__init__(self)
        self.name = name
        self.is_loop = True
        self.video_w = video_w
        self.video_h = video_h
        self.video = self.video_cap(video_device, video_w, video_h, buffer_size)
        self.frame = self.read_frame()
        print('初始化视频线程成功！')

    def run(self):
        while self.is_loop:
            self.frame = self.read_frame()

    def stop(self):
        """
        结束线程
        """
        print("退出视频线程！")
        self.is_loop = False

    def video_cap(self, video_device, video_w, video_h, buffer_size):
        """
        启动摄像头拉流
        :param video_device: 设备号
        :param video_w: 拉流宽
        :param video_h: 拉流长
        :param buffer_size: 缓冲区大小
        :return: 视频流
        """
        video = v4l2capture.Video_device(video_device)
        video.set_format(video_w, video_h)
        video.create_buffers(buffer_size)
        video.queue_all_buffers()
        video.start()
        return video

    def read_frame(self):
        """
        读取当前视频帧
        :return: 当前帧图像
        """
        try:
            select.select((self.video,), (), ())
            image_data = self.video.read_and_queue()
            array = np.array(np.frombuffer(image_data, dtype=np.uint8))
            frame = array.reshape(self.video_h, self.video_w, 3)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception, e:
            frame = None
        return frame


def video_process(video_path, helmet_model, socket_video_flag, video_width, video_height, buffer_size=1):
    """
    处理视频
    :param video_path: 摄像头路径
    :param helmet_model: 模型
    :param socket_video_flag: 是否启用socket传输视频流
    :param video_width: 拉流宽
    :param video_height: 拉流长
    :param buffer_size: 缓冲区大小
    """
    video_thread = VideoThread(video_path, video_width, video_height, buffer_size, '视频线程')
    video_thread.start()
    serial_thread = SerialThread('串口线程')
    serial_thread.start()

    is_connected = False

    if socket_video_flag:
        try:
            print("连接socket发送图片！")
            host = '192.168.1.111'
            port = 8848
            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.settimeout(1)
            socket_client.connect((host, port))
            print("连接socket成功！")
            is_connected = True
        except Exception, e:
            print("连接socket失败！")
            is_connected = False

    while True:
        try:
            frame_read = video_thread.frame

            if frame_read is None:
                print('获取视频失败！')
                # 退出程序
                socket_client.close()
                video_thread.stop()
                serial_thread.stop()
                sys.exit(1)

            # [类别编号, 置信度, 中点坐标, 左上坐标, 右下坐标]
            boxes = helmet_model.predict(frame_read)
            cast_origin(boxes, helmet_model.image_width, helmet_model.image_height, frame_read.shape)

            print_results(boxes, helmet_model.label_names)
            draw_results(frame_read, boxes, helmet_model.colors, helmet_model.label_names, False)
            serial_thread.set_data(boxes)

            if is_connected:
                try:
                    buffer = cv2.imencode('.jpg', frame_read)[1]
                    socket_client.sendall(np.array(buffer).tostring())
                except Exception, e:
                    print("socket断开连接！")
                    socket_client.close()
                    is_connected = False


        except KeyboardInterrupt:
            # 退出程序
            socket_client.close()
            video_thread.stop()
            serial_thread.stop()
            sys.exit(1)
