# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 15:14:36 2023

@author: c.witham

intermediate stage of yolo output processing - extracts only the objects 
needed for this particular analysis and combines into a single file for each day
"""

import pandas as pd
import pickle

#update before using
metadata_file='path_to_metadata_csv_file'
yolo_output_dir='path_to_yolact_pickle_files'

tokeep=[18,10,3,23]
data=pd.read_csv(metadata_file)

no_rows,no_cols=data.shape


for n in range(no_rows):
    print(n)
    nn=int(data.No_Sections.iloc[n])
    if nn>0:
        no_frames=-1
        newdata={'boxes':[],'masks':[],'scores':[],'classes':[],'frameno':[]}
        for m in range(nn):
            file_name=yolo_output_dir+data.Group_ID.iloc[n]+'/'+data.Video.iloc[n]+'_'+str(m+1)+'_summary.pickle'
            yolo_data=pickle.load(open(file_name,'rb'))
            for i,output in enumerate(yolo_data['boxes']):
                no_frames+=1
                for j,out in enumerate(output):
                    x1,y1,x2,y2,score,clas=out
                    clas=int(clas)
                    if clas in tokeep:
                        newdata['boxes'].append([x1,y1,x2,y2])
                        newdata['masks'].append(yolo_data['masks'][i][j])
                        newdata['scores'].append(score)
                        newdata['classes'].append(clas)
                        newdata['frameno'].append(no_frames)
        out_fname=yolo_output_dir+data.Group_ID.iloc[n]+'/'+data.Video.iloc[n]+'_summary_all.pickle'
        pickle.dump(newdata,open(out_fname,'wb'))
            
            