# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 10:47:53 2023


find if dlc markers are in yolact box
Script to detect in deeplabcut markers for the monkey are inside the object bounding box from Yolact
"""
import pandas as pd
import pickle
import os
import numpy as np

# file paths - update before using
CSVfile=path_to_CSV_file
DLC_output_dir=path_to_DLC_Output
Yolact_output_dir=path_to_Yolact_Output
Save_output_dir=path_to_dir_save_files

# read in phase information spreadsheet
phase_info=pd.read_csv(CSVfile)
phases=['FF','NF','NO1','NO2']
phase_length=[300,120,120,120]
no_rows,no_cols=phase_info.shape
first_approach=[]

dlc_thresh=0.9
dlc_x=[1,4,7,10,13,16,19,22,25,28]

wood_sc=[33,36]

for n in range(no_rows):
    print(n)
    obs_id=phase_info.Obs_ID.iloc[n]
    phs=phase_info.Phase.iloc[n]
    
    if os.path.exists(Yolact_output_dir+obs_id+'_Front_camera_out.pickle'):
        if os.path.exists(DLC_output_dir+obs_id+'_DLC.csv'):
    
            if phs in phases:
                # find phase index, start and end frames for phase
                i=phases.index(phs)
                start_frame=int(phase_info.Time_Start.iloc[n]*phase_info.FrameRate_Front.iloc[n])
                end_frame=int((phase_info.Time_Start.iloc[n]+phase_length[i])*phase_info.FrameRate_Front.iloc[n])
                
                # read in DLC and yolact data
                dlc_markers=pd.read_csv(DLC_output_dir+obs_id+'_Front_Camera_1downsampledDLC_resnet50_TT_FrontJun2shuffle1_100000.csv',header=[0,1,2])
                yolact_box=pickle.load(open(Yolact_output_dir+obs_id+'_Front_camera_out.pickle','rb'))
                headers=dlc_markers.columns
                
                
                # get yolact bounding box
                allboxes=np.zeros((phase_length[i]*phase_info.FrameRate_Front.iloc[n],4))
                for m in range(start_frame,end_frame):
                    if len(yolact_box['boxes'][m])>0:
                        allboxes[m-start_frame][0]=yolact_box['boxes'][m][0][0]
                        allboxes[m-start_frame][1]=yolact_box['boxes'][m][0][1]
                        allboxes[m-start_frame][2]=yolact_box['boxes'][m][0][2]
                        allboxes[m-start_frame][3]=yolact_box['boxes'][m][0][3]
                    else:
                        allboxes[m-start_frame][0]=np.nan
                        allboxes[m-start_frame][1]=np.nan
                        allboxes[m-start_frame][2]=np.nan
                        allboxes[m-start_frame][3]=np.nan
                    
                        
                
                allboxes=allboxes.squeeze()
                bbox=np.nanmedian(allboxes,axis=0) # use median of bounding boxes for all object detections during that phase

                bbox_orig=bbox.copy()
                
                # make the bounding box bigger (use fixed bounding box 200 x 500 for NF and FF, original bbox x 2 for NO1 and NO2
                width=(bbox[2]-bbox[0])
                height=(bbox[3]-bbox[1])
                
                meanx=(bbox[2]+bbox[0])/2
                meany=(bbox[3]+bbox[1])/2
                
                
                # for food items use fixed box 200 wide and 500 high, for other objects double size of detected bounding box
                if i<2:
                    bbox[0]=meanx-100
                    bbox[1]=meany-400
                    bbox[2]=meanx+100
                    bbox[3]=meanx+100
                else:
                    bbox[0]=bbox[0]-(width/2)
                    bbox[1]=bbox[1]-(height/2)
                    bbox[2]=bbox[2]+(width/2)
                    bbox[3]=bbox[3]+(height/2)
                
                results_out={'Frame':[],'relFrame':[],'relTime':[],'No_Markers':[],'Conf':[],'BodyPart':[]}
                
                # check if wood markers are visible at all 
                wood_visible=[0,0]
                for m in range(start_frame,end_frame):
                    if dlc_markers.iloc[m][wood_sc[0]]>dlc_thresh:
                        wood_visible[0]+=1
                    if dlc_markers.iloc[m][wood_sc[1]]>dlc_thresh:
                        wood_visible[1]+=1
                usewood=wood_visible[0]>1500&(wood_visible[1]>1500) # use wood markers if they are visible to detect if human in front of shelf
                for m in range(start_frame,end_frame):
                    in_range=0
        
                    # find all markers inside targer
                    for ind in dlc_x:
                        if usewood:
                            useable= (dlc_markers.iloc[m][ind+2]>dlc_thresh)&(dlc_markers.iloc[m][wood_sc[0]]>dlc_thresh)&(dlc_markers.iloc[m][wood_sc[1]]>dlc_thresh)
                        else:
                            useable= (dlc_markers.iloc[m][ind+2]>dlc_thresh)    
                                
                        if useable:    
                            x=dlc_markers.iloc[m][ind]*phase_info.Scale_Factor.iloc[n]
                            y=dlc_markers.iloc[m][ind+1]*phase_info.Scale_Factor.iloc[n]
                                      
                            if (x>bbox[0])*(x<bbox[2])&(y>bbox[1])&(y<bbox[3]):
                                in_range+=1
                                if in_range==1:
                                    markers=headers[ind][1]
                                    max_conf=dlc_markers.iloc[m][ind+2]
                                else:
                                    if dlc_markers.iloc[m][ind+2]>max_conf:
                                        markers=headers[ind][1]
                                        max_conf=dlc_markers.iloc[m][ind+2]
                    if in_range>0:
                        results_out['Frame'].append(m)
                        results_out['No_Markers'].append(in_range)
                        results_out['Conf'].append(max_conf)
                        results_out['BodyPart'].append(markers)
                        results_out['relFrame'].append(m-start_frame)
                        results_out['relTime'].append((m-start_frame)/phase_info.FrameRate_Front.iloc[n])
                        
                filename=Save_output_dir+obs_id+'_'+phs+'_pickle.pickle'
                pickle.dump({'dlc':dlc_markers, 'bbox':bbox,'dlc_thresh':dlc_thresh,'orig_bbox':bbox_orig,'width':width,'height':height},open(filename,'wb'))
                        
                data_out=pd.DataFrame.from_dict(results_out)
                data_out.to_csv(Save_output_dir+obs_id+'_'+phs+'_intarget.csv')
                
                if len(results_out['relTime'])>2:
                    first_approach.append(results_out['relTime'][0])
                else:
                    first_approach.append(phase_length[i])
            else:            
                first_approach.append(0)
        else:            
            first_approach.append(0)
    else:            
        first_approach.append(0)

phase_info['First_Approach_OrigYolact']=first_approach           
            
        
            
phase_info.to_csv(Save_output_dir+'Phase_Information_2023_with_Approach.csv')
        
        
        
        

