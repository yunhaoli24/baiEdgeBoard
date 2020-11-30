#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# license removed for brevity
import socket
import cv2
import numpy as np


def server():
    host = '0.0.0.0'
    port = 8848
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("等待连接.....")
    s.bind((host, port))
    s.listen(1)

    video_name = "result"
    while True:
        conn, addr = s.accept()
        print("接收来自" + addr[0] + "的连接")
        while True:
            try:
                data = conn.recv(1228800)
                image = np.asarray(bytearray(data), dtype="uint8")
                frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
                if frame is not None:
                    cv2.namedWindow(video_name, cv2.WINDOW_NORMAL)
                    cv2.imshow(video_name, frame)
                    cv2.waitKey(1)
            except Exception as e:
                print(e)
                break

        s.close()


if __name__ == '__main__':
    server()
