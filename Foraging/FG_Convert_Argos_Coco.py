# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 09:21:25 2022

@author: c.witham
"""
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 16:54:58 2022

Conversion code to convert output from the argos labeller (REF) to a more useful format for Yolact
 (the argos output augmentation produces some odd images)

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
newdir=path_to_new_dir # for combined model
imgdir=path_to_img_dir # from original argos labels
pickleFileName=path_to_pickle_file # from original argos labels
jsonTrainFileName=path_to_original_training_json_file # from original argos labels
jsonValidFileName=path_to_original_validation_json_file # from original argos labels
picklePrefix = path_used_as_prefix_pickle_file # from original argos labels


objs='Monkey'
catid=1
imgadd_train=300 # current number of images in combined json traiining file
annadd_train=522 # current number of annotations in combined json training file
imgadd_valid=300 # current number of images in combined json validation file
annadd_valid=134 # current number of annotations in combined json validation file
imgpre='GC_'


pck=pickle.load(open(pickleFileName,'rb'))
pck=pck['seg_dict']
imglist=list(pck.keys())
fpath=imglist[-1]
i=fpath.find('\\')
fpath=fpath[0:i+1]


# do training set first
new_json=json.load(open(newdir+'training/annotations.json','r'))
old_json=json.load(open(jsonTrainFileName,'r'))
anno_id=[]

for anno in old_json['annotations']:
    anno_id.append(anno['image_id'])

anno_old=[]
for anno in new_json['annotations']:
    anno_old.append(anno['image_id'])
no_ann=max(anno_old)
    
for image in old_json['images']:
    fname=image['file_name']
    fname=fname[10:-6]+'.png'
    imgadd_train+=1
    
    fname2=fpath+fname

    if fname2 in imglist:
        img=cv2.imread(imgdir+fname)
        h,w,c=img.shape
        img=cv2.resize(img,(550,550))
        cv2.imwrite(newdir+'training/PNGimages/'+imgpre+fname,img)
        annots=pck[fname2]

        ann_list=[i for i,x in enumerate(anno_id) if x==image['id']]
        no=-1
        for b in annots:
            anno=annots[b]
            coords=[]
            allx=[]
            ally=[]
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
            if no<len(ann_list):
                a=old_json['annotations'][ann_list[no]]
            else:
                a=old_json['annotations'][ann_list[0]]
            a['segmentation']=[coords]
            a['bbox']=bbox
            a['area']=area
            annadd_train+=1
            a['id']=annadd_train
            a['image_id']=imgadd_train
            a['category_id']=catid
            new_json['annotations'].append(a)
    image['id']=imgadd_train
    image['file_name']=imgpre+fname
    new_json['images'].append(image)

   
            
with open(newdir+"training/annotations.json", "w") as write_file:
    json.dump(new_json, write_file)
print(imgadd_train)
print(annadd_train)         


# do validation set second
new_json=json.load(open(newdir+'validation/annotations.json','r'))
old_json=json.load(open(jsonValidFileName,'r'))


anno_id=[]
for anno in old_json['annotations']:
    anno_id.append(anno['image_id'])

anno_old=[]
for anno in new_json['annotations']:
    anno_old.append(anno['image_id'])
no_ann=max(anno_old)
  
for image in old_json['images']:
    fname=image['file_name']
    fname=fname[10:-6]+'.png'
    imgadd_valid+=1
    
    fname2=fpath+fname

    if fname2 in imglist:
        img=cv2.imread(imgdir+fname)
        h,w,c=img.shape

        img=cv2.resize(img,(550,550))
        cv2.imwrite(newdir+'validation/PNGimages/'+imgpre+fname,img)
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
            if no<len(ann_list):
                a=old_json['annotations'][ann_list[no]]
            else:
                a=old_json['annotations'][ann_list[0]]
            a['segmentation']=[coords]
            a['bbox']=bbox
            a['area']=area
            annadd_valid+=1
            a['id']=annadd_valid
            a['image_id']=imgadd_valid
            a['category_id']=catid
            new_json['annotations'].append(a)
    image['id']=imgadd_valid
    image['file_name']=imgpre+fname
    new_json['images'].append(image)      
print(imgadd_valid)
print(annadd_valid)        

     

with open(newdir+"validation/annotations.json", "w") as write_file:
    json.dump(new_json, write_file)
    
    
                    





