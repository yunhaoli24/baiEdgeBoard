# coding=UTF-8
from serial import Serial

import threading
import time
import os

__all__ = ['SerialThread']

#外面RX  里面TX  接GND
class SerialThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.is_loop = True
        self.singal = threading.Event()
        
        self.port = "/dev/ttyPS1"
        self.bps = 9600             #波特率9600 1停止 8数据
        self.timeout = 10

        self.result_data = 0
        self.state = False
        self.send_data("Init")
        print('初始化串口线程成功!')
        self.singal.set()


    def run(self):
        while self.is_loop:
            
            self.singal.wait()

            if self.result_data == 2 and self.state ==  False:   #传入的数据为开门 当前状态为关门时
                print('开门！')
                self.send_data("1ab")
                self.state = True

            if self.result_data == 0 and self.state == True:    #传入的数据为关门 当前状态为开门时
                print('关门!')
                self.send_data("0ab")
                self.state = False

            if self.result_data == 1:
                print('请佩戴安全帽!')
                self.send_data("3ab")

            self.singal.clear()

    def set_data(self, boxes):      #传入boxes判断是否存在帽子  box[0]的值 1为人 2为帽子 
        self.result_data = 0
        for box in boxes:
            if box[0] == 1:
                self.result_data = 1
            if box[0] == 2:
                self.result_data = 2
                break
        self.singal.set()

    def send_data(self, data):          #data 为 需要发送的数据(不确定是否能发转义字符)
        try:
            uar_serial = Serial(self.port, self.bps, timeout=self.timeout)
            result = uar_serial.write(data)     #result 为 发送数据的长度
            uar_serial.close()

        except Exception as e:
                print("----error-----", e)

    def stop(self):
        """
        结束线程
        """
        self.result_data = 0
        self.is_loop = False
        self.singal.set()
        print("退出串口线程！")


