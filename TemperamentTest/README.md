# *Temperament Test*

## Aims

The Temperament Test aims to evaluate the temperament and neophobia of macaques. 
The procedure involves transferring a macaque from its social group to an isolated cage, where it is exposed to five different conditions: 
familiar food, novel food, novel object 1, and novel object 2. There were two sets of noveltys, for a total of six different objects.

The primary objective of this test is to gather data that aids in understanding the levels of exploration and neophobia. 
This is achieved by observing behaviors such as latency to approach novel stimuli and amount of freezing.

For each temperament test, two cameras were employed for recording: one positioned at the side of the cage, and another at the front.

Our pipeline takes video feeds from both cameras as input. It processes this input and provides the following outputs for each macaque undergoing the test:
amount of movement and freezing, latency to approach, number of approaches.

To achieve this, three models were utilized: two based on DeepLabCut (DLC) and one based on Yolcat.
- DLC_side_camera: Trained on side camera footage, this model can detect macaque body parts. It was utilized to track the animal's movement around its cage.
- DLC_front_camera: Trained on front camera footage, this model can detect macaque body parts used for interacting with objects (such as hands, mouth, and nose).
- Yolact_front_camera: This model was utilized to detect six different objects.
The last two models, DLC_front_camera and Yolact_front_camera, worked in conjunction to identify approaches to the objects.
An approach is defined as at least three macaque body parts being within the bounding box detected by the YOLACT model.

## Detailed Workflow:

- TT_Convert_Argos_Coco: This script translates the Argos output (REF) into a compatible JSON format for our pipeline. Please note that this code is designed to work for one object at a time.
- TT_Convert_Argos_Coco_Add_Object: This script was used to combined all the novel objetcs together intothe same COCO format training file (json) for training YOLACT.
- TT_Object_Recognition_Metrics: This script is used to compute the object recognition accuracy for the YOLACT model.
- TT_Extract_Movement_From_DLC: Extracts movement information, including the amount of movement and freezing, categorized by phase, from the output of DLC_side_camera.
- TT_Detect_Object_Interaction: This script identifies whether the macaque's body part markers from DLC_side_camera are within the bounding box of objects detected by Yolact_front_camera.

## Credits

- Yolact
```  
  @inproceedings{yolact-iccv2019,
  author    = {Daniel Bolya and Chong Zhou and Fanyi Xiao and Yong Jae Lee},
  title     = {YOLACT: {Real-time} Instance Segmentation},
  booktitle = {ICCV},
  year      = {2019},
}
```

- Argos
  
Ray, S., & Stopfer, M. A. (2021). Argos: A toolkit for tracking multiple animals in complex visual environments. Methods in Ecology and Evolution, 00, 1- 11. [https://doi.org/10.1111/2041-210X.13776](https://doi.org/10.1111/2041-210X.13776)

- DeepLabCut

Mathis et al 2018: [10.1038/s41593-018-0209-y](10.1038/s41593-018-0209-y)

Nath, Mathis et al 2019: [10.1038/s41596-019-0176-0](10.1038/s41593-018-0209-y)
