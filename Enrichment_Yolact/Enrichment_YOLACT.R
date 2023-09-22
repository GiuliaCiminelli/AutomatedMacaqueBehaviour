library(tidyverse)
library(reticulate)
library(lubridate)
library(ggpattern)
library(data.table)
library(ggpubr)
library(readxl)



setwd("folder path")
Feeding_time <- read_excel("Feeding_time.xlsx")

pd <- import("pandas")
#read all pickle files
#create list of all pickle files in folder
picklefiles = list.files(pattern="*YL.pickle")

####start####
#make empty data frame to fill with videos 
df <- data.frame()
dft <- data.frame()
df1 <- data.frame()#

for (i in 1:54){
  
  assign(picklefiles[i], G <- pd$read_pickle(picklefiles[i]))

  file_name <- gsub("[_].+$", "",picklefiles[i])
  date_exp <- gsub(".* ", "",picklefiles[i])
  date_exp <- gsub("_.*", "",date_exp)
  group_name <-gsub("[ ].+$", "",picklefiles[i])
  #extract the boxes data
  p <- G$boxes
  
  #12h is 43200 seconds, we run every 3 seconds then 43200/3
  
  #with feeding time
  #the YOLACT model runes every 3 seconds
  #start frame from seconds, which in detection is 21600/3
  start_sec <- Feeding_time$Feeding_frame[i]
  start_det <- start_sec/3
  end_sec <- start_sec+21600
  end_det <- (end_sec)/3
  dft <- as.data.frame(p[start_det])[1,]
  
  if (is.na(dft)){
    dft <- data.frame("X1"=NA,"X2"=NA,"X3"=NA,"X4"=NA)
  }
 
  print(file_name)
  count=1
  for (j in (start_det+1):end_det){
    df1 <- data.frame(p[j])[1,]
    dft <- rbind(dft,df1)
    count=count+1
  }
  #NB X1Y1 are up left corner and X2Y2 are bottom right corner
  colnames(dft) <-c( "X1","Y1","X2","Y2")
  # add Frames (bbox every 3 seconds)
  #1 detection every 3 sec=1 detection every 15*3 frames
 
  Seconds <- seq(start_sec,(( end_sec)),by=(3))
  Frame <- Seconds*15
  
  dft <- cbind(Frame, dft)
  #add coordinate for center of bbox

  xcentre <- (dft$X1+dft$X2)/2
  ycentre <- (dft$Y1+dft$Y2)/2
  dft <- cbind(dft,xcentre,ycentre)
  #add video information
  Video_name <- rep(file_name,nrow(dft))
  #add group name
  Group_name <- rep(group_name ,nrow(dft))
  #add week day
  Date_exp <- rep(date_exp,nrow(dft))
  dft <-cbind(Video_name,Group_name, Date_exp,dft)
  dft$Date_exp <- as.Date(dft$Date_exp)
  Weekday <- wday(dft$Date_exp)
  dft<- add_column(dft, Weekday,.after = 3)
  
  #dft is the dataframe for only one video
  
  #remove row with NA (not detected boxes)
  dft <- na.omit(dft)
  #treshold
  tresholdx <- (mean(abs(diff(dft$xcentre)))) 
  tresholdy <- (mean(abs(diff(dft$ycentre))))
  absdiffx <- c(0,abs(diff(dft$xcentre)))
  absdiffy <- c(0,abs(diff(dft$ycentre)))
  #smooth
  k <- c(-10:10)
  
  smooth_kernel <- dnorm(k,mean=0,sd=3) # create my kernel
  kk <- rev(replace(0 * absdiffx, seq_along(smooth_kernel), rev(smooth_kernel)))
  smooth_absdiffx <- convolve(absdiffx,kk)#convolves the two traces
  smooth_absdiffy <- convolve(absdiffy,kk)#convolves the two traces
  #create column for movements yes/no
  movement <- ifelse(smooth_absdiffx>tresholdx | smooth_absdiffy>tresholdy , 1,0)
  dft <- cbind(dft,movement)
  dft <- cbind(dft,smooth_absdiffx ,smooth_absdiffy )
  
  df <- rbind(df,dft)
  
}
#save file
write.csv(df,"Enrichment.csv",row.names = TRUE)
# make graph for threshold
plot(df$Frame,df$smooth_absdiffx,pch = 21,col = "black", bg = "black",xlab = "Frame", ylab = " x coordinate of bbox center")
abline(h = tresholdx, col = "red", lty = 2,lwd = 6)
text(x = 22, y = 12, "x treshold", pos = 2, col = "red", font = 9)
#####---------------------------------------



a <- read.csv("EnrichmentPSGB_tot_FT_new.csv")
df <- a

#add movement 1st hour, 2nd hour, other, after feeding time
#video name
video_names <- unique(df$Video_name)
first <- df[match(unique(df$Video_name), df$Video_name),]
first_h <- first$Frame +54000
second_h <-first_h +54000


df_hours <- data.frame()
for (i in 1:length(video_names)){
  df_p <- df[df$Video_name==video_names[i],]
  
  #get number of frame with movement for each hour
  df_ultimate <- df_p %>% 
    group_by(Video_name, Group_name, Weekday,  Hour = cut(Frame, breaks = 
            c(-Inf, first_h[i],second_h[i],#third_h[i],fourth_h[i]#,
              Inf), 
                                    labels = c("1H","2H",#"3H","4H",
                                               "Other"))) %>% 
    summarise(movement_hour = sum(movement)) %>% 
    complete(Hour)
  #get number of frame with detection for each hour
  df_count <- df_p %>% 
    group_by(Hour = cut(Frame, breaks = c(-Inf, first_h[i],second_h[i],#third_h[i],fourth_h[i], 
                                          Inf), 
                                           labels = c("1H","2H",#"3H","4H",
                                                      "Other")))%>% count(Hour)
  #merge the two df
  df_tot <- merge(df_ultimate,df_count)
  
  #percentage of movement
  df_tot$Percentage_movement <- df_tot$movement_hour/df_tot$n
  
  df_hours <- rbind(df_hours,df_tot)
}
write.csv(df_hours,"Enrichment_hours.csv",row.names = TRUE)

