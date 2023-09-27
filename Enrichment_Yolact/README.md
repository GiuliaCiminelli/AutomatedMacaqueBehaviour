# **Enrichment_Yolcat**

## Aims
The goal of the Enrichment_Yolcat project is to analyse the usage of a white tank containing raisins within the macaque enclosure. 
This enrichment is consistently present, with raisins added exclusively on Mondays. Our study aimed to discern usage patterns on Mondays (when the tank is full) 
and Thursdays (when it is empty).

To quantify the usage, we leverage the movement of the enrichment item as a proxy. This involves training a Yolact-based model capable of identifying the white tank in each enclosure. 
The model utilizes the difference in the x, y coordinates of the bounding box as an indicator of movement. We labelled the training and validation dataset using Argos.

As input, this pipeline requires CCTV videos capturing macaques in their enclosure, and it outputs the amount of item movement.

## Detailed Workflow

- EN_Covert_Argos_Coco: This script translates the Argos output (REF) into a format compatible with our pipeline (json)
- EN_Analyses_Videos: Using the Yolact model, this script processes the CCTV videos, providing bounding box coordinates, masks, confidence scores, and class labells for each detection.
- Enrichment_YOLCAT: Building upon the information obtained from EN_Analyses_Videos, this script extracts the volume of item movements for different weekdays, specifically Mondays and Tuesdays.

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
