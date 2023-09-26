Foraging

The Foraging project is focused on analysing the extent of foraging behavior in various scenarios.

Foraging Mixes
This sub-project aims to determine the amount of foraging activity exhibited by macaques each day of the week. 
The monkeys are provided with different foraging mixes corresponding to each day of the week.

Pellet Size
In this sub-project, we investigate the foraging behavior of macaques when presented with either small and large-sized pellets.

Seasons
This sub-project seeks to identify variations in foraging behavior during different seasons: breeding season and birth season.

To quantify the amount of macaques engaging in foraging, we employ a Yolact-based model trained to recognize macaques within their enclosures. 
To detect wich monkeys were foraging, a region of interest was manually drown to containe the region where the food was positioned by the staff.

The training and validation datasets underwent annotation using Argos.

Detailed Workflow:

- FG_Analyse_Videos: This script applies the YOLO-based model to analyse CCTV camera footage for monkey detection. 
  It provides output in the form of bounding boxes, masks, scores, and class labels for each detection, which is then saved to a pickle file.
- FG_Convert_Argos_Coco: Using the YOLO-based model, this script processes CCTV videos to generate bounding box coordinates, masks, confidence scores, and class labells for each detection.
- Foraging_ForagingMixes: This script calculates the number of detected macaques within the defined region of interest and extracts the quantity of animals foraging for each specific foraging mix.
- Foraging_PelletSize: This script tallies the number of detected macaques within the region of interest and determines the amount of foraging activity when presented with both small and large pellet sizes.
- Foraging_Seasons: This script counts the number of detected macaques in the region of interest and extracts the amount of animals engaged in foraging over a span of six months, 
  comprising three months of breeding season and three months of birth season.
