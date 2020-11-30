#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import json

from src.model import pm_model
from src.video import video_process
from src.uitl import print_results, draw_results, parse_args, load_image

if __name__ == '__main__':

    args = parse_args()

    # 加载模型和配置文件
    with open('/home/root/workspace/helmet/config.json') as json_file:
        configs = json.load(json_file)
    helmet_model = pm_model(configs)

    args.game_mode = True
    if args.game_mode:
        # 比赛模式从摄像头获取视频
        print('比赛模式，从摄像头获取视频')
        video_process(configs['camera'], helmet_model, args.socket_video, configs['video_width'], configs['video_height'], configs['buffer_size'])
    else:
        # 图片模式，检测完一张图片后就退出程序
        image = load_image(configs['image'])
        boxes = helmet_model.predict(image)
        print_results(boxes, helmet_model.label_names)
        draw_results(image, boxes, helmet_model.colors, helmet_model.label_names, True)
        sys.exit(1)


