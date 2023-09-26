# **Enrichment_Yolo**

## Aims
The Enrichment_Yolo project is dedicated to analysing the utilization of an enrichment puzzle within the macaque enclosures. 
This puzzle was introduced specifically for this study, representing a novelty to the macaques. 
There are two variations of the puzzle: one containing blue toy monkeys and coloured wooden blocks, and another comprising solely coloured wooden blocks.

The primary objective of our study was to delineate the usage patterns over the course of a month following the introduction of the enrichment. 
This aimed to help identify when the novelty of the enrichment waned for the macaques.

To quantify the usage, we rely on the count of monkeys interactions as a proxy. 
This entails training a Yolo-based model capable of recognizing the macaques in close proximity to the enrichment. 

The training and validation datasets were annotated using the Segment Anything Annotator (SAM). 
While these datasets consist of labelled images containing various objects, it's important to note that not all of these objects were specifically utilized in this study. 
However, the Yolo-based model was trained to detect all of them.

As input, this pipeline requires CCTV videos capturing macaques in their enclosure, and it outputs the amount of macaques interacting with the enrichment.

## Detailed Workflow

- ENY_Yolo_Train_Model: This script is responsible for generating the Yolo-based model.
- ENY_Yolo_Analyse_Vid: This script executes the Yolo model on the CCTV videos, and to manage file sizes, it separates the output into multiple files.
- ENY_Convert_COCO_to_Yolo: This script converts labelled images from COCO format (json) to YOLO format, generating one text file per image.
- ENY_Process_Yolo_Data_Part1: This script represents an intermediate step in processing the Yolo model output.
  It selectively extracts objects pertinent to this study (blue monkey, macaques, coloured wooden blocks, and front platform).
  The data is then consolidated into single files for each day.
- ENY_Process_Yolo_Data_Part2: This script further analyzes the Yolo output, tallying the number and area of monkeys interacting with the enrichment.
  Due to suboptimal detection accuracy for wooden blocks, manual definition of regions of interest for the enrichment is performed (recorded in a CSV file).
  Each detected monkey is checked to determine if its mask (object id 18) overlaps with the region of interest.
  In cases where the enrichment is near a pole, monkeys may overlap with the region while situated on the front platform, without interacting with the enrichment.
  To mitigate false positive interactions, segments overlapping with both the region of interest and the front platform bounding box (object id 10) are excluded.
- Enrichment_Yolo: This script calculates the percentage of macaques interacting with the enrichment, utilizing the output from ENY_Process_Yolo_Data_Part2.

## Credits
 - Yolov8
   
   Jocher, G., Chaurasia, A., & Qiu, J. (2023). YOLO by Ultralytics (Version 8.0.0) [Computer software]. [https://github.com/ultralytics/ultralytics](https://github.com/ultralytics/ultralytics)

  - Segment anything annotator

    https://github.com/haochenheheda/segment-anything-annotator
    
     
