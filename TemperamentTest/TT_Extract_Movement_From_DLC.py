# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 08:07:27 2023


Extracts movement information by phase from deeplabcut markers
"""
import pathlib
import pandas as pd
import numpy as np
import os

# file paths - update before using
CSVfile=path_to_CSV_phase_information_file
DLC_output_dir=path_to_DLC_Output
Save_output_dir=path_to_dir_save_files

# list of deeplabcut csv files
dd=list(pathlib.Path(DLC_output_dir).glob('*.csv'))

# read in phase information
phase_times=pd.read_csv(CSVfile)

phase_times['Movement']=0
phase_times['Freeze']=0
phase_times['OutOfSight']=0

#cycle through deeplabcut csv files
for data_file in dd:
    print(data_file)
    data = pd.read_csv(data_file, header=[0,1,2])
    
    fpath,fname=os.path.split(data_file)
    animal_id=fname[0:3]
    
    bodyparts=[]
    cols=data.columns.values
    
    for n in range(1,len(cols),3):
        scorer,bp,co=cols[n]
        bodyparts.append(bp)

    no_bp=len(bodyparts)
    
    face_coords = [0,1,2,3,4,5,8,9,12,13] # index of face coordinates
    body_coords = [6,7,10,11,14,15,16,17,18,19,20,21,22,23] #index of body coordinates
    
    # extract face and body coordinates and scores
    face_allx=data.iloc[:,[n*3+1 for n in face_coords]].to_numpy()
    face_ally=data.iloc[:,[n*3+2 for n in face_coords]].to_numpy()
    face_conf=data.iloc[:,[n*3+3 for n in face_coords]].to_numpy()

    body_allx=data.iloc[:,[n*3+1 for n in body_coords]].to_numpy()
    body_ally=data.iloc[:,[n*3+2 for n in body_coords]].to_numpy()
    body_conf=data.iloc[:,[n*3+3 for n in body_coords]].to_numpy()
    
    # set coordinates with scores below threshold to NaN
    face_allx[np.where(face_conf<0.8)]=np.nan
    face_ally[np.where(face_conf<0.8)]=np.nan
    
    body_allx[np.where(body_conf<0.8)]=np.nan
    body_ally[np.where(body_conf<0.8)]=np.nan
    
    # get average face and body coordinates
    
    face_x=np.nanmean(face_allx,axis=1)
    face_y=np.nanmean(face_ally,axis=1)
    
    body_x=np.nanmean(body_allx,axis=1)
    body_y=np.nanmean(body_ally,axis=1)
    

    # calculate difference in x,y coordinates between frames
    diff_face=np.sqrt(np.square(np.diff(face_x))+np.square(np.diff(face_y)))
    diff_body=np.sqrt(np.square(np.diff(body_x))+np.square(np.diff(body_y)))
    
    excl=np.logical_and(np.isnan(diff_face),np.isnan(diff_body))
    ismoving=np.logical_or(diff_face>4,diff_body>4)
    ismoving[excl]=False
    
    # Baseline (Familiar Food) Phase
    
    phases={'FF','NF','NO1','NO2','end_novel'}
    
    for phase in phases:
        i=phase_times['Obs_ID'].eq(animal_id)&phase_times['Phase'].eq(phase)
        i=i.index[i==True]
        if len(i)>0:
            frame_start=phase_times.loc[i,'Frame_Start'].tolist()[0]
            frame_rate=phase_times.loc[i,'FrameRate'].tolist()[0]
            if phase=='FF':
                tim=5
            else:
                tim=2
                
            inds=range(frame_start,frame_start+(frame_rate*tim*60))
            if phase=='end_novel':
                if inds[-1]>len(ismoving):
                    inds=range(frame_start,len(ismoving))
            
            phase_times.loc[i,'Movement']=np.sum(ismoving[inds])/frame_rate
            phase_times.loc[i,'OutOfSight']=np.sum(excl[inds])/frame_rate
            phase_times.loc[i,'Freeze']=(np.sum(ismoving[inds]==False)-np.sum(excl[inds]))/frame_rate
        else:
            phase_times.loc[i,'Movement']=np.nan
            phase_times.loc[i,'OutOfSight']=np.nan
            phase_times.loc[i,'Freeze']=np.nan
    
phase_times.to_csv(Save_output_dir)
