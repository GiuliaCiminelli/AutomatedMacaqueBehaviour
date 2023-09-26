#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 14:38:13 2023


Run model on days of CCTV videos - output is pickle and labelled video files, day broken up into sections to reduce file size
"""

from ultralytics import YOLO
import cv2
import pickle
import os

import numpy as np
from scipy import io

model_dir='path-to-model'
video_dir='path-to-videos'
output_dir='path-for-saving'

# define some constants
CONFIDENCE_THRESHOLD = 0.2
GREEN = (0, 255, 0)
model=YOLO(model_dir+'best.pt')

#groups to analyse
groups={'G01','G03','G04','G06','G07','G09','G13','G15','G16'}

for gp in groups:
    vid_dir=video_dir+gp+'/'
    videos=os.listdir(vid_dir)
    
    out_dir=output_dir+gp+'/'
    
    for video in videos:
        video_input=vid_dir+video
        vidname,ext=os.path.splitext(video)
        
        save_file=out_dir+vidname
        
        #open video and create video writer object for output 
        vid=cv2.VideoCapture(video_input)
        target_fps   = 1
        frame_width  = round(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = round(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_rate=round(vid.get(cv2.CAP_PROP_FPS))
        no_parts=1    
        video_output=out_dir+vidname+'_'+str(no_parts)+'.mp4'
        out = cv2.VideoWriter(video_output, cv2.VideoWriter_fourcc(*'mp4v'), target_fps, (frame_width, frame_height))
        
        
         
        success,frame = vid.read()
        frameno=0

        # set up empty dictionary for output
        coco_out={'boxes':[], 'masks':[],'frames':[]}
        
        while success:
            if frameno%frame_rate==0:
                frame=cv2.resize(frame,(640,640))
                
                # run the YOLO model on the frame
                detections = model(frame,verbose=False)[0]
                
                if type(detections.masks)!=type(None):
                    # extract masks and boxes from model - boxes is a 6 element vector of x1,y1,x2,y2,score and class
                    masks=detections.masks.data.cpu().detach().numpy()
                    boxes=detections.boxes.data.cpu().detach().numpy()
                    
                    
                    coco_out['boxes'].append(boxes)
                    masks_cont=[]
                    #convert mask to contours to save space
                    for mask in masks:
                        mask2=mask.astype(np.uint8)
                        contours, _ = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                        masks_cont.append(contours)
                    coco_out['masks'].append(masks_cont)
                    frame_out=detections.plot(labels=False, boxes=False, probs=False)
                    frame_out=cv2.resize(frame_out,(frame_width,frame_height))
                else:
                    coco_out['boxes'].append([])
                    coco_out['masks'].append([])
                    
                    
                   
                out.write(frame_out)
                print(frameno)
            success,frame=vid.read() # read video frame
            
            coco_out['frames'].append(frameno)
            frameno+=1
            
            # save file for every x files otherwise files get too big
            if (frameno>100) & ((frameno%250000)==0):            
                #io.savemat(save_file+'_'+str(no_parts)+'_boxes.mat', coco_out)
                with open(save_file+'_'+str(no_parts)+'_summary.pickle', 'wb') as f:
                    pickle.dump(coco_out, f)
                    
                out.release()
                video_output=out_dir+vidname+'_'+str(no_parts+1)+'.mp4'
                out = cv2.VideoWriter(video_output, cv2.VideoWriter_fourcc(*'mp4v'), target_fps, (frame_width, frame_height))
                coco_out={'boxes':[], 'masks':[],'frames':[]}
                no_parts+=1
                
        vid.release()
        out.release()
        with open(save_file+'_'+str(no_parts)+'_summary.pickle', 'wb') as f:
            pickle.dump(coco_out, f)
