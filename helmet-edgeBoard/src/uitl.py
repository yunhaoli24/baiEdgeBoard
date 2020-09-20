#!/usr/bin/python
# -*- coding: UTF-8 -*-
import cv2
import argparse
import numpy as np

__all__ = ['load_image', 'parse_args', 'draw_results', 'print_results', 'cast_origin']


def load_image(path):
    """
    载入图片
    """
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    return image


def parse_args():
    """
    转化args
    """
    parser = argparse.ArgumentParser(description='比赛模式读取摄像头视频；反之跑图片识别。')
    parser.add_argument('-g', '--game_mode',
                        help='比赛模式Flag',
                        action="store_true")
    parser.add_argument('-s', '--socket_video',
                        help='输出视频Flag',
                        action="store_false")
    return parser.parse_args()


def draw_results(image, boxes, colors, class_names, image_mode=False):
    """
    在图片上画出结果框
    :param image: 图片
    :param boxes: boxes数组
    :param colors: 颜色list
    :param class_names: 标签名
    :param image_mode: 是否保存
    """
    for box in boxes:
        predicted_class = class_names[box[0]]
        label = '{} {:.2f}'.format(predicted_class, box[1])
        cv2.putText(image, label, (box[3][0], box[3][1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[box[0]], 1)
        cv2.rectangle(image, box[3], box[4], colors[box[0]], 3)
    if image_mode:
        cv2.imwrite('result.jpg', image)


def cast_origin(boxes, resize_width, resize_height, shape):
    """
    映射为原图大小
    类别编号, 置信度, 中点坐标, 左上坐标, 右下坐标
    :param boxes: boxes
    :param resize_width: 拉伸尺寸之后的宽
    :param resize_height: 拉伸尺寸之后的长
    :param shape: 读入图片长宽
    :return: None
    """
    for box in boxes:
        box[2] = (int(box[2][0] * shape[1] / resize_width), int(box[2][1] * shape[0] / resize_height))
        box[3] = (int(box[3][0] * shape[1] / resize_width), int(box[3][1] * shape[0] / resize_height))
        box[4] = (int(box[4][0] * shape[1] / resize_width), int(box[4][1] * shape[0] / resize_height))


def print_results(boxes, class_names):
    """
    打印结果
    :param boxes: boxes
    :param class_names: 标签名
    :return:
    """
    print('类别\t置信度\t中点坐标\t左上坐标\t右下坐标\t')
    for box in boxes:
        print('{}\t{}\t{}\t{}\t{}'.format(class_names[box[0]], box[1], box[2], box[3], box[4]))
    print('\n')
