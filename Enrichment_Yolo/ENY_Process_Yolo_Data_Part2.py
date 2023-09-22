#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 18:48:09 2023

@author: cwitham

To anaylse the yolo output and count the number (and area) of monkeys interacting with the enrichment
Manually added region of interest for the enrichment (csv file)

Analyse each detected monkey, see if mask of monkey (object id 18) overlaps with region of interest. For some of the groups wheere
the enrichemnt is on the near pole it is possible that the monkeys may overlap the ROI whilst sitting on the front platform
and not interacting wiht the enrichment. Need to exclude segments that overalp with both the ROI and the front
platform bounding box (object id 10)

"""

import pandas as pd
import pickle
import numpy as np

#calculate area of polygon
def PolyArea(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

#update before using
metadata_file='path_to_metadata_csv_file'
yolo_output_dir='path_to_yolact_pickle_files'

tokeep=[18,10,3,23]
metadata=pd.read_csv(metadata_file)

no_rows,no_cols=metadata.shape

monkey_id=18
frontplatform_id=10


for n in range(no_rows):
    nn=int(metadata.No_Sections.iloc[n])
    if nn>0:
        # load pickle file
        fname=yolo_output_dir+metadata.Group_ID.iloc[n]+'/'+metadata.Video.iloc[n]+'_summary_all.pickle'
        yolo_data=pickle.load(open(fname,'rb'))
        
        roi=[metadata.ROI_X1.iloc[n],metadata.ROI_Y1.iloc[n],metadata.ROI_X2.iloc[n],metadata.ROI_Y2.iloc[n]]
        # convert to 640 x 640 pixels to match yolo output
        roi[0]=roi[0]/1280*640
        roi[1]=roi[1]/720*640
        roi[2]=roi[2]/1280*640
        roi[3]=roi[3]/720*640
        
        a=metadata.Start_Time.iloc[n]
        start_time_sec=int(a[0:2])*3600+int(a[3:5])*60+int(a[6:8])-(7*3600) #start time in seconds relative to 7am
        allframes=[]
        for a in yolo_data['frameno']:
            allframes.append(a)
            
        frames=list(set(allframes))
        
        interactions={'Number':[],'Area':[],'TimeStamp':[]}
        
        for f in frames:
            print(str(n)+':'+str(f))
            inds=[i for i,x in enumerate(allframes) if x==f]
            
            

            no_monks=0
            area_monks=0
            if monkey_id in yolo_data['classes'][inds[0]:inds[-1]+1]:
                # monkeys are present
                monks=[i for i,x in enumerate(yolo_data['classes'][inds[0]:inds[-1]+1]) if x==monkey_id]
                fp=[i for i,x in enumerate(yolo_data['classes'][inds[0]:inds[-1]+1]) if x==frontplatform_id]
                usefp=False
                if len(fp)>0:
                    usefp=True
                    fp_box=yolo_data['boxes'][inds[fp[0]]]
                
                for m in monks:
                    masks=yolo_data['masks'][inds[m]]
                    ispres=0
                    indarea=0
                    isfront=False
                    for mask in masks:
                        mask2=mask.squeeze().tolist()
                        if len(mask2)>2:
                            overlap_roi=[i for i,x in enumerate(mask2) if (x[0]>roi[0])&(x[0]<roi[2])&(x[1]>roi[1])&(x[1]<roi[3])] #find points that overlap with ROI
                            
                            if (len(overlap_roi)>0):
                                ispres=1
                                mask=mask.squeeze().transpose((1,0))
                                indarea+=PolyArea(mask[0],mask[1])     
                            
                            if usefp:
                                overlap_fp=[i for i,x in enumerate(mask2) if (x[0]>fp_box[0])&(x[0]<fp_box[2])&(x[1]>fp_box[1])&(x[1]<fp_box[3])] #find points that overlap with front platform
                     
                                # if overlaps with roi but not with front platform add it to the count and calculate area of mask for monkey
                                if (len(overlap_fp)>0):
                                    isfront=True
                                                         
                    if isfront==False:                
                        area_monks+=indarea
                        no_monks+=ispres

            interactions['Number'].append(no_monks)
            interactions['Area'].append(area_monks)
            interactions['TimeStamp'].append(start_time_sec+f)
        file_out=yolo_output_dir+metadata.Group_ID.iloc[n]+'/'+metadata.Video.iloc[n]+'_interactions.pickle'
        pickle.dump(interactions,open(file_out,'wb'))
        

