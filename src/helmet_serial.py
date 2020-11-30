# coding=UTF-8
from serial import Serial

import threading

__all__ = ['SerialThread']


# 外面RX  里面TX  接GND
class SerialThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.is_loop = True
        self.singal = threading.Event()

        self.port = "/dev/ttyPS1"
        self.bps = 9600
        self.timeout = 10

        self.result_data = False
        self.state = False
        self.send_data("Init")
        print('初始化串口线程成功!')
        self.singal.set()

    def run(self):
        while self.is_loop:

            self.singal.wait()

            if self.result_data and self.state == False:  # 传入的数据为开门 当前状态为关门时
                print('开门！')
                self.send_data("1ab")
                self.state = True

            if self.result_data == False and self.state == True:  # 传入的数据为关门 当前状态为开门时
                print('关门!')
                self.send_data("0ab")
                self.state = False

            self.singal.clear()

    def set_data(self, boxes):
        """
        设置发送数据，并唤醒线程
        :param boxes: boxes
        """
        # 传入boxes判断是否存在帽子  当box[0]==2时为帽子类
        self.result_data = False
        for box in boxes:
            if box[0] == 2:
                self.result_data = True
        self.singal.set()

    def send_data(self, data):
        """
        调用串口发送数据
        :param data: 待发送的数据
        """
        try:
            uar_serial = Serial(self.port, self.bps, timeout=self.timeout)
            result = uar_serial.write(data)
            uar_serial.close()
            # print(result)

        except Exception as e:
            print("----error-----", e)

    def stop(self):
        """
        结束线程
        """
        self.result_data = False
        self.is_loop = False
        self.singal.set()
        print("退出串口线程！")
