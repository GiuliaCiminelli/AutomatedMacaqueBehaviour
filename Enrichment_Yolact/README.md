Enrichment_Yolcat

The goal of the Enrichment_Yolcat project is to analyze the usage of a white tank containing raisins within the macaque enclosure. 
This enrichment is consistently present, with raisins added exclusively on Mondays. Our study aimed to discern usage patterns on Mondays (when the tank is full) 
and Thursdays (when it is empty).

To quantify the usage, we leverage the movement of the enrichment item as a proxy. This involves training a Yolact-based model capable of identifying the white tank in each enclosure. 
The model utilizes the difference in the x, y coordinates of the bounding box as an indicator of movement. We labeled the training and validation dataset using Argos.

As input, this pipeline requires CCTV videos capturing macaques in their enclosure, and it outputs the amount of item movement.

Detailed Workflow:

- EN_Covert_Argos_Coco: This script translates the Argos output (REF) into a format compatible with our pipeline (ask Claire)
- EN_Analyses_Videos: Using the Yolact model, this script processes the CCTV videos, providing bounding box coordinates, masks, confidence scores, and class labels for each detection.
- Enrichment_YOLCAT: Building upon the information obtained from EN_Analyses_Videos, this script extracts the volume of item movements for different weekdays, specifically Mondays and Tuesdays.
