# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 10:33:13 2023

Converts labels from COCO format (json) to YOLO format (one text file per image)
"""

import json
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

# change the paths - this was for the validation dataset
json_file='path_to_json_annotations'
save_dir='path_to_save_dir'
img_path='path_to_images'

fn = save_dir+'labels/'# folder name


# do training set first
data=json.load(open(json_file,'r'))



# Create image dict
images = {'%g' % x['id']: x for x in data['images']}
# Create image-annotations dict
imgToAnns = defaultdict(list)
for ann in data['annotations']:
    imgToAnns[ann['image_id']].append(ann)

# Write labels file
for img_id, anns in tqdm(imgToAnns.items(), desc=f'Annotations {json_file}'):
    img = images['%g' % img_id]
    image=cv2.imread(img_path+img['file_name'])
    image=cv2.resize(image,(640,640))
    cv2.imwrite(save_dir+'images/'+img['file_name'],image)
    h, w, f = img['height'], img['width'], img['file_name']

    bboxes = []
    segments = []
    keypoints = []
    for ann in anns:
        # The COCO box format is [top left x, top left y, width, height]
        box = np.array(ann['bbox'], dtype=np.float64)
        box[:2] += box[2:] / 2  # xy top-left corner to center
        box[[0, 2]] /= w  # normalize x
        box[[1, 3]] /= h  # normalize y
        if box[2] <= 0 or box[3] <= 0:  # if w <= 0 and h <= 0
            continue
    
        clas = 0  # class
        bx = [clas]
        bx.append(box.tolist())
        
        bboxes.append(box)
            
        no_c=-1
        s=[clas]
        for coords in ann['segmentation'][0]:
            no_c+=1
            if (no_c%2==0):
                s.append(coords/w)
            else:
                s.append(coords/h)
        
        segments.append(s)
    
    
    # Write to text file
    fpath=Path(fn+f)
    with open(fpath.with_suffix('.txt'), 'a') as file:
        for i in range(len(bboxes)):
            line = segments[i]
            noa=-1
            for x in line:
                noa+=1
                if noa==0:
                    file.write('%d ' % (x))
                else:
                    file.write('%g ' % (x))
            file.write('\n')
