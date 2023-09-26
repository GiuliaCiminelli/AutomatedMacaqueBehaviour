# -*- coding: utf-8 -*-
"""
Created on Tue May 16 14:33:58 2023

Calculate object recognition accuracy for Yolact model
"""

import pandas as pd
import pickle


# file paths - update before using
CSVfile=path_to_CSV_file
Yolact_output_dir=path_to_Yolact_Output
Save_output_dir=path_to_dir_save_files


sect_times=[300,120,120,120]
objects=['Mr_Potato','Novel_Food','Owl','Raisins','RopeToy','YellowToy']

phases=pd.read_csv(CSVfile)
no=-1
sessions=phases['Obs_ID'].values.tolist()
sessions=set(sessions)


data={'Session':[],'Object':[],'TP_Count':[],'FP_Count':[],'No_Frames':[]}
for sess in sessions:
    no+=1
    info=phases.query('Obs_ID==@sess')
    
    with open(Yolact_output_dir+sess+'_Front_camera_out.pickle','rb') as f:
        S=pickle.load(f)

    no_corr=[0,0,0,0,0,0]
    no_incorr=[0,0,0,0,0,0]
    no_frames=[0,0,0,0,0,0]
    for n in range(4):
        if n==0:
            objs=[3,1,info['Object1'].iloc[n],info['Object2'].iloc[n]]
            
        st=info['Time_Start'].iloc[n]
        fr=info['FrameRate_Front'].iloc[n]
        
        frs=st*fr
        fre=st*fr+(sect_times[n]*fr)
        if n==2:
            no_frames[info['Object1'].iloc[n]]=fre-frs
        elif n==3:
            no_frames[info['Object2'].iloc[n]]=fre-frs
        elif n==0:
            no_frames[3]=fre-frs
        else:
            no_frames[1]=fre-frs
            
        
        for m in range(int(frs),int(fre)):
            if len(S['classes'][m])>0:
                if S['classes'][m][0]==objs[n]:
                    no_corr[S['classes'][m][0]]+=1
                else:
                    no_incorr[S['classes'][m][0]]+=1
    for n in range(6):
        data['Session'].append(sess)
        data['Object'].append(objects[n])
        data['TP_Count'].append(no_corr[n])
        data['FP_Count'].append(no_incorr[n])
        data['No_Frames'].append(no_frames[n])
        
df=pd.DataFrame(data)
df.to_csv(Save_output_dir+'/TempTest_ObjectDectectionAccuracy_all.csv')        
        
        
        
        
        
