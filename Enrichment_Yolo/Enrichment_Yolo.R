library(dplyr)
library(tidyverse)
library(reticulate)
library(data.table)
library(tidyr)
library("readxl")
library(ggpubr)
library(ggplot2)
#stats
library(lme4)
library(lmerTest)
library(glmmTMB)

####
#the data in the pickle files are:
#number of monkeys in the ROI that are not overlapping with the front platform 
#area of the monkeys that are not overlapping with the front platform
#timestamp in seconds = the time starts at 7am therefore 0 is 7am




setwd("folder path")
pd <- import("pandas")
#read all pickle files
#create list of all pickle files in folder
picklefiles = list.files(pattern="*interactions.pickle")

# I want a dataframe with Group_ID, Date, Time, numberofmonkeys
df <- data.frame()
for (file in 1:length(picklefiles)){
  assign(picklefiles[file], G <- pd$read_pickle(picklefiles[file]))
  
  numberm <- G$Number
  aream <- G$Area
  time <- G$TimeStamp
  
  #build dataframe
  group_id <- substr(picklefiles[file], 1, 3)
  
  #since G01 is detecting the blue monkey toy as a monkey
  if (group_id=="G01"){
    for(n in 1:length(numberm)){
        if(numberm[n]>=1)
          numberm[n]=numberm[n]-1
        
    }
  }
    
  
  date <- substr(picklefiles[file], 4, 14)
  
  group_size <- 60*60
  #get average numbers of monkeys every hours
  avg_nm <- data.frame("Number_Monkey"=numberm)
  
  Avg_noMonkey <- avg_nm %>% 
    mutate(grp = 1+ (row_number()-1) %/% group_size) %>% 
    group_by(grp) %>% 
   summarise(across(everything(), mean, na.rm = TRUE)) %>% 
    select(-grp)
  
  
  #add time
  Time <- seq(time[1], time[length(time)], by=group_size)
  if (length(Time)!=nrow(Avg_noMonkey))
    Time <- Time[-length(Time)]
  print(picklefiles[file])
   
  
  #from seconds to hh:mm:ss
  hours <- Time %/% 3600+7
  minutes <- (Time %% 3600) %/% 60
  seconds <- Time %% 60
  formatted_time<- sprintf("%02d:%02d:%02d", hours, minutes, seconds)
  # add group_ID
  Group_ID <- rep(group_id,length(Time))
  #add Date
  Date <- rep(date,length(Time))
  avg_df <- data.frame(Group_ID,Date,Avg_noMonkey,"Time_sec"=Time,"Time"=formatted_time)
  df <- rbind(df,avg_df)
}

info_csv <- read.csv("Info.csv")

#change date formatting in info_csv and df

info_csv$Date <- as.Date(info_csv$Date, format = "%d/%m/%Y")
df$Date <- as.Date(df$Date)
df_all <- merge(df,info_csv,by=c("Group_ID","Date"),all.x=TRUE)



df_all$Percentage <- (df_all$Number_Monkey/df_all$Group_No)*100
df_all$Hours <- as.factor(substr(df_all$Time, start = 1, stop = 2))
df_all$Group_Type2<- df_all$Group_Type[df_all$Group_Type %in% c("Female Stock", "Male Stock")] <- "Stock"

#save file
write.csv(df_all,"Enrichement_Yolo.csv",row.names = TRUE)

