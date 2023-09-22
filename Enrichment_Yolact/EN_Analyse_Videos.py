# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 10:33:47 2022

@author: c.witham

Apply YOlACT model to CCTV camera footage to detect monkeys, save output (bounding box, mask, scores, classes) to a pickle file
"""

from yolact import Yolact
from yolact.utils.augmentations import  FastBaseTransform
from yolact.layers.output_utils import postprocess
import os

from yolact.data import  set_cfg

import numpy as np
import torch

import pickle
from scipy import io

import cv2

# set config, vid file and weights paths - change before running code!
config_file=Path_to_Yolact_Config_File #yaml file
weights_file=Path_to_Yolact_Weights_File # pth file
viddir=Directory_Videos
output_dir=Directory_for_Saving


# load Yolact model
set_cfg(config_file)

with torch.no_grad():
    torch.set_default_tensor_type('torch.cuda.FloatTensor')
    net = Yolact()
    net.load_weights(weights_file)
    net.eval()
    net=net.cuda()

# analyse videos
vids=os.listdir(viddir) 
for video in vids:
    video_input=viddir+video
    save_file=output_dir+video[:-4]+'_out'
   
    # open video files for reading and writing
    vid=cv2.VideoCapture(video_input)
    target_fps   = round(vid.get(cv2.CAP_PROP_FPS))
    frame_width  = round(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = round(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
       
    success,frame=vid.read() # read video frame
    coco_out={'classes':[],'scores':[],'boxes':[],'masks':[]}
    frameno=0
    while success:        
        frame_out=frame.copy()
        
        # run Yolact model on frame
        with torch.no_grad():
            frame=torch.from_numpy(frame).cuda().float() # convert format for torch
            batch = FastBaseTransform()(frame.unsqueeze(0))
            preds = net(batch)  
        
        # process yolact output to get classes, scores, masks and bounding boxes
        classes, scores, boxes, masks = postprocess(preds, frame_width, frame_height, crop_masks=False, score_threshold=0.1)
        
        #convert output to numpy format 
        coco_out['classes'].append(classes.cpu().detach().numpy())
        coco_out['scores'].append(scores.cpu().detach().numpy())
        coco_out['boxes'].append(boxes.cpu().detach().numpy())
        masks_cont=[]
        
        #convert each mask from mask image to contour (save space)
        for mask in masks:
            mask2=mask.cpu().detach().numpy()
            mask2=mask2.astype(np.uint8)
            contours, _ = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            masks_cont.append(contours)
        coco_out['masks'].append(masks_cont)

        success,frame=vid.read() # read video frame
        frameno+=1
        print(frameno)
    
    vid.release()
    
    # save output as pickle file
    with open(save_file+'.pickle', 'wb') as f:
        pickle.dump(coco_out, f)
