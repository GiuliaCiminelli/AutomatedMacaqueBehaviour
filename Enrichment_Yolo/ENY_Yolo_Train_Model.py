#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 13:12:25 2023

Train Yolo model

"""

from ultralytics import YOLO
 
# update before running code
model_yaml_file='path_to_yaml_file'
model_name='Monkey'


# Load the base model.
model = YOLO('yolov8n-pose.pt')
 
# Training.
results = model.train(
   data=model_yaml_file,
   imgsz=640,
   epochs=2000,
   batch=-1,
   name=model_name)


