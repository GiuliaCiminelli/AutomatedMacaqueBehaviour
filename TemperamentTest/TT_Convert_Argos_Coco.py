# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 16:54:58 2022

@author: c.witham

Conversion code if using Argos (REF!) labeller to label images, code for a single object
"""

import json
import os
import pickle
import cv2
import numpy as np

#calculate area of polygon
def PolyArea(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

#filepaths - update before using
newdir=path_to_new_dir
imgdir=path_to_img_dir
pickleFileName=path_to_pickle_file
jsonTrainFileName=path_to_original_training_json_file
jsonValidFileName=path_to_original_validation_json_file
picklePrefix = path_used_as_prefix_pickle_file

#load the argos labeller pickle file
pck=pickle.load(open(pickleFileName,'rb'))
pck=pck['seg_dict']
imglist=list(pck.keys())



os.makedirs(newdir)
os.makedirs(newdir+'training/PNGImages/')
os.makedirs(newdir+'validation/PNGImages/')

# do training set first
old_json=json.load(open(jsonTrainFileName,'r'))
# check the annotations for image id
anno_id=[]
for anno in old_json['annotations']:
    anno_id.append(anno['image_id'])
    
no_ann=len(old_json['annotations'])   
for image in old_json['images']:
    fname=image['file_name']
    fname=fname[10:-6]+'.png'
    
    fname2='picklePrefix'+fname
    
    if fname2 in imglist:
        img=cv2.imread(imgdir+fname) # read in original image
        h,w,c=img.shape
        img=cv2.resize(img,(550,550)) # resize images to 550x550
        cv2.imwrite(newdir+'training/PNGimages/'+'MPH'+fname,img) # save resized image 
        annots=pck[fname2] 

        ann_list=[i for i,x in enumerate(anno_id) if x==image['id']] # find all annotations for that image
        no=-1
        #for each annotation rescale the coordinates so that they are correct for the 550 x 550 image
        for b in annots:
            coords=[]
            allx=[]
            ally=[]
            anno=annots[b]
            for x,y in anno:
                x=x*(550/w)
                y=y*(550/h)
                coords.append(int(x))
                coords.append(int(y))
                allx.append(int(x))
                ally.append(int(y))
            bbox=[min(allx),min(ally),max(allx)-min(allx),max(ally)-min(ally)] # calculate new bounding box
            area=PolyArea(allx,ally) # calculate area of polygon
            no+=1
            if (no+1)<=len(ann_list): # update annotation list
                a=old_json['annotations'][ann_list[no]]
                a['segmentation']=[coords]
                a['bbox']=bbox
                a['area']=area
                a['category_id']=1
                old_json['annotations'][ann_list[no]]=a
            else:
                a=old_json['annotations'][ann_list[-1]]
                a['bbox']=bbox
                a['area']=area
                a['segmentation']=[coords]
                no_ann+=1
                a['id']=no_ann
                a['category_id']=1
                old_json['annotations'].append(a)
print(no_ann)
print(len(old_json['images']))         
#update file names in json list       
for n in range(len(old_json['images'])):
    fname=old_json['images'][n]['file_name']
    fname=fname[10:-6]+'.png'
    old_json['images'][n]['file_name']='MPH'+fname

# save updated json training file            
with open(newdir+"training/annotations.json", "w") as write_file:
    json.dump(old_json, write_file)
        
# do validation set first
old_json=json.load(open('C://Users/c.witham/OneDrive - MRC Harwell/Giulia - PhD/Argos_giulia_TT/Annotated_img/Mr_Potato/validation/annotations.json','r'))
anno_id=[]
for anno in old_json['annotations']:
    anno_id.append(anno['image_id'])
    
no_ann=len(old_json['annotations'])   
for image in old_json['images']:
    fname=image['file_name']
    fname=fname[10:-6]+'.png'
    
    fname2='C:/PhD/Single-Animal/Front_Camera_TT/DL_model/ARGOS/Mr_Potato\\'+fname
    
    if fname2 in imglist:
        img=cv2.imread(imgdir+fname)
        h,w,c=img.shape
        img=cv2.resize(img,(550,550))
        cv2.imwrite(newdir+'validation/PNGimages/'+'MPH'+fname,img)
        annots=pck[fname2]

        ann_list=[i for i,x in enumerate(anno_id) if x==image['id']]
        no=-1
        for b in annots:
            coords=[]
            allx=[]
            ally=[]
            anno=annots[b]
            for x,y in anno:
                x=x*(550/w)
                y=y*(550/h)
                coords.append(int(x))
                coords.append(int(y))
                allx.append(int(x))
                ally.append(int(y))
            bbox=[min(allx),min(ally),max(allx)-min(allx),max(ally)-min(ally)]
            area=PolyArea(allx,ally)
            no+=1
            if (no+1)<=len(ann_list):
                a=old_json['annotations'][ann_list[no]]
                a['segmentation']=[coords]
                a['bbox']=bbox
                a['area']=area
                a['category_id']=1
                old_json['annotations'][ann_list[no]]=a
            else:
                a=old_json['annotations'][ann_list[-1]]
                a['bbox']=bbox
                a['segmentation']=[coords]
                a['area']=area
                no_ann+=1
                a['id']=no_ann
                a['category_id']=1
                old_json['annotations'].append(a)                

print(no_ann)
print(len(old_json['images']))  
for n in range(len(old_json['images'])):
    fname=old_json['images'][n]['file_name']
    fname=fname[10:-6]+'.png'
    old_json['images'][n]['file_name']='MPH'+fname
    
# save updated json validation
with open(newdir+"validation/annotations.json", "w") as write_file:
    json.dump(old_json, write_file)
    
    
                    




