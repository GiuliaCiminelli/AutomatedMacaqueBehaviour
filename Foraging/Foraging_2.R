library(tidyverse)
library(reticulate)
library(lubridate)
library(ggpattern)
library(data.table)
library(ggpubr)
library(ggplot2)
library(ptinpoly)
library(reshape2)
library (dplyr)
library(readxl)
library(rcartocolor)
library(viridis)

library(sf)
library(sfheaders)

setwd("folder path")
# cleaning data -----------------------------------------------------------

#get files
ROI <- read.csv("ROI.csv")
pd <- import("pandas")
#read all pickle files
#create list of all pickle files in folder
picklefiles = list.files(pattern="*YL.pickle")
l <- length(picklefiles)
####start####
#make empty data frame to fill with videos 
df <- data.frame()

#for running on number of pickle files
for (i in 1:l){
  dft <- data.frame()
  df1 <- data.frame()#
  assign(picklefiles[i], G <- pd$read_pickle(picklefiles[i]))
  
  file_name <- gsub("[_].+$", "",picklefiles[i])
  date_exp <- gsub(".* ", "",picklefiles[i])
  date_exp <- gsub("_.*", "",date_exp)
  group_name <-gsub("[ ].+$", "",picklefiles[i])
  #extract the boxes data
  p <- G$boxes
  #make it into a data frame, count number of boxes
  #2h is 7200 seconds, model runs every 3 seconds then 7200/3=number of detection
  start_sec <- 1
  start_det <- 1
  end_sec <- start_sec+7200
  end_det <- (end_sec)/3
  #for running on number of detection
  for ( j in 1: end_det){
    #extract bbox for detection i
    dft <- as.data.frame(p[j])[,]
    
    if (identical(dft, numeric(0))){
      dft <- data.frame("X1"=NA,"X2"=NA,"X3"=NA,"X4"=NA)
      Detection <- rep(j,1)
    }else
      Detection <- rep(j,nrow(dft))
    dft <- cbind(dft,Detection)
    df1 <- rbind(df1,dft)
    
  }
  Group_Name <- rep(group_name,nrow(df1))
  Date <- rep(date_exp,nrow(df1))
  df1 <- cbind(df1,Group_Name,Date)
  df <- rbind(df,df1)
}

#NB X1Y1 are up left corner and X2Y2 are bottom right corner
colnames(df)[1:4] <-c( "X1","Y1","X2","Y2")

#find center of bbox
xcentre <- (df$X1+df$X2)/2
ycentre <- (df$Y1+df$Y2)/2
df <- cbind(df,xcentre,ycentre)
#save datarame df
write.csv(df,"Feeding_2.csv",row.names = TRUE)

#######################################################################


# cleaning data: df and roi ------------------------------------------------
setwd("folder path")
df <- read.csv("Feeding_2.csv")

#check if points bbox (xcentre and ycentre) are in polygon= ROI

#check for each group 
df_nona <- na.omit(df)

# polyogn check -----------------------------------------------------------
mypoly <- sfheaders::sf_polygon(ROI, x = "x", y = "y", polygon_id = "Group_Name")
mypoint <- sf::st_as_sf(df_nona, coords = c("xcentre", "ycentre"))

final <- st_join(mypoint, mypoly, st_within)
#save datarame df
write.csv(final,"Final_new.csv")

#only get the row with point in polygon
pol <- subset(final, final$Group_Name.x == final$Group_Name.y)
pol$Group_Name.x <- as.factor(pol$Group_Name.x )
colnames(pol)[6] <- "Group_Name"

##adding group size
group_size <- read_excel("Group Size.xlsx")
gs <- cbind(group_size$Group_Name,group_size$Group_Size)
colnames(gs) <- c("Group_Name","Group_Size")
pol <- merge(pol,gs)
pol$Group_Size <- as.numeric(pol$Group_Size)
pol$Date <- as.Date(pol$Date)
#number of occurrence of group_name in one day is the number of monkeys foraging in 2 hours
monkey_foraging <- pol%>% group_by(Date,Detection)%>%count(Group_Name)
monkey_foraging<- merge(monkey_foraging,gs)
monkey_foraging$Group_Size <- as.numeric(monkey_foraging$Group_Size)
monkey_foraging_p <- monkey_foraging%>% group_by(Group_Name,Date,Detection)%>%summarise(percentage=n/Group_Size)
#tot_percentage is the total percentage of monkeys foraging in one day taking in account their size
monkey_foraging_ps <- monkey_foraging_p%>% group_by(Date,Group_Name)%>%summarise(tot_percentage=mean(percentage))
#diet was applied on the 29 of september, from this day is after the change
#Adding a column A/B based on the date
monkey_foraging_ps$Pellet <-   (ifelse(monkey_foraging_ps$Date > as.Date("2022-09-28"), 
                                              "Big", "Small"))
#write final file
write.csv(monkey_foraging_ps,"Foraging_2.csv")
