#import libraries
library(tidyverse)
library(reticulate)
library(lubridate)
library(ggpattern)
library(data.table)
library(ggpubr)
library(readxl)
#stats
library(lme4)
library(lmerTest)
options(scipen=999)

# Set the working directory
setwd("path to working directory")

# Read the Excel file containing feeding time data
Feeding_time <- read_excel("path to Feeding_time_Enrichment_Drum.xlsx")

#### CLEAN DATA ####
# Import the pandas package for handling pickle files
pd <- import("pandas")

# List all pickle files in the directory that match the pattern "*YL.pickle"
picklefiles = list.files(pattern="*YL.pickle")

#### START PROCESSING PICKLE FILES ####
# Initialize empty dataframes to store results
df <- data.frame()
dft <- data.frame()
df1 <- data.frame()

# Loop through the first 54 pickle files
for (i in 1:54) {
  
  # Read the current pickle file using pandas
  assign(picklefiles[i], G <- pd$read_pickle(picklefiles[i]))
  
  # Extract metadata (file name, date, group name) from the file name
  file_name <- gsub("[_].+$", "", picklefiles[i])
  date_exp <- gsub(".* ", "", picklefiles[i])
  date_exp <- gsub("_.*", "", date_exp)
  group_name <- gsub("[ ].+$", "", picklefiles[i])
  
  # Extract the bounding box data from the pickle file
  p <- G$boxes
  
  # Get the feeding start time in seconds and convert it to detection frame number (every 3 seconds)
  start_sec <- Feeding_time$Feeding_frame[i]
  start_det <- start_sec / 3
  
  # Define the end time as 6 hours (21600 seconds) after feeding start time and convert to detection frames
  end_sec <- start_sec + 21600
  end_det <- end_sec / 3
  
  # Extract the first bounding box data at feeding start time
  dft <- as.data.frame(p[start_det])[1, ]
  
  # Handle case where there is no data (NA) for the first bounding box
  if (is.na(dft)) {
    dft <- data.frame("X1" = NA, "X2" = NA, "X3" = NA, "X4" = NA)
  }
  
  print(file_name)
  
  # Loop through frames from feeding start time to end time, extracting bounding box data
  count = 1
  for (j in (start_det + 1):end_det) {
    df1 <- data.frame(p[j])[1, ]
    dft <- rbind(dft, df1)
    count = count + 1
  }
  
  # Set column names for bounding box coordinates
  colnames(dft) <- c("X1", "Y1", "X2", "Y2")
  
  # Add frame number and seconds (timestamps) to the dataframe
  Seconds <- seq(start_sec, end_sec, by = 3)
  Frame <- Seconds * 15
  dft <- cbind(Frame, dft)
  
  # Calculate center coordinates for the bounding boxes
  xcentre <- (dft$X1 + dft$X2) / 2
  ycentre <- (dft$Y1 + dft$Y2) / 2
  dft <- cbind(dft, xcentre, ycentre)
  
  # Add metadata (video name, group name, experiment date) to the dataframe
  Video_name <- rep(file_name, nrow(dft))
  Group_name <- rep(group_name, nrow(dft))
  Date_exp <- rep(date_exp, nrow(dft))
  dft <- cbind(Video_name, Group_name, Date_exp, dft)
  
  # Convert experiment date to Date format and extract the weekday
  dft$Date_exp <- as.Date(dft$Date_exp)
  Weekday <- wday(dft$Date_exp)
  dft <- add_column(dft, Weekday, .after = 3)
  
  # Remove rows with missing data (NA) for bounding boxes
  dft <- na.omit(dft)
  
  # Calculate movement thresholds based on average change in bounding box center coordinates
  tresholdx <- mean(abs(diff(dft$xcentre)))
  tresholdy <- mean(abs(diff(dft$ycentre)))
  absdiffx <- c(0, abs(diff(dft$xcentre)))
  absdiffy <- c(0, abs(diff(dft$ycentre)))
  
  # Smooth the data using a Gaussian kernel
  k <- c(-10:10)
  smooth_kernel <- dnorm(k, mean = 0, sd = 3)  # Create a Gaussian kernel
  kk <- rev(replace(0 * absdiffx, seq_along(smooth_kernel), rev(smooth_kernel)))
  smooth_absdiffx <- convolve(absdiffx, kk)  # Convolve x-coordinate changes
  smooth_absdiffy <- convolve(absdiffy, kk)  # Convolve y-coordinate changes
  
  # Identify movement based on smoothed data and thresholds
  movement <- ifelse(smooth_absdiffx > tresholdx | smooth_absdiffy > tresholdy, 1, 0)
  dft <- cbind(dft, movement)
  dft <- cbind(dft, smooth_absdiffx, smooth_absdiffy)
  
  # Append the results to the main dataframe
  df <- rbind(df, dft)
  
}

# Add movement information for the first and second hours after feeding time
# Get unique video names
video_names <- unique(df$Video_name)
first <- df[match(unique(df$Video_name), df$Video_name),]
first_h <- first$Frame +54000
second_h <-first_h +54000
third_h <- second_h+ 54000
fourth_h <- third_h+54000
fifth_h <-fourth_h +54000
sixth_h <- fifth_h +54000

# Initialize an empty dataframe for storing movement data by hour
df_hours <- data.frame()

# Loop through each video to calculate movement per hour
for (i in 1:length(video_names)) {
  df_p <- df[df$Video_name == video_names[i], ]
  
  # Define hour bins and ensure correct number of labels
  hour_bins <- c(-Inf, first_h[i], second_h[i], third_h[i], fourth_h[i], fifth_h[i], sixth_h[i], Inf)
  
  # The number of intervals is always 1 less than the number of breaks, so make sure the labels match
  hour_labels <- c("1H", "2H", "3H", "4H", "5H", "6H", "Other")  # Add "Other" to match the intervals
  
  # Get number of frames with movement for each hour
  df_ultimate <- df_p %>%
    group_by(Video_name, Group_name, Weekday, Hour = cut(Frame, breaks = hour_bins, labels = hour_labels)) %>%
    summarise(movement_hour = sum(movement, na.rm = TRUE)) %>%
    complete(Hour, fill = list(movement_hour = 0))
  
  # Get number of frames with detection for each hour
  df_count <- df_p %>%
    group_by(Hour = cut(Frame, breaks = hour_bins, labels = hour_labels)) %>%
    summarise(n = n()) %>%
    complete(Hour, fill = list(n = 0))
  
  # Merge the two data frames on 'Hour'
  df_tot <- merge(df_ultimate, df_count, by = "Hour", all = TRUE)
  
  df_tot <- df_tot %>% filter(Hour != "Other")
  
  # Calculate percentage of movement, handling division by zero
  df_tot$Percentage_movement <- ifelse(df_tot$n == 0, NA, df_tot$movement_hour / df_tot$n)
  
  # Bind rows to the final data frame
  df_hours <- bind_rows(df_hours, df_tot)
}

# Rename the "n" column to "detection_hour"
colnames(df_hours)[which(names(df_hours) == "n")] <- "detection_hour"

# Add group type information based on group name
Group_name <- unique(df_hours$Group_name)
Group_type <- c("BG", "BG", "JG", "BG", "BG", "JG", "JG", "BG", "JG")  # Example group types
group_type <- data.frame(Group_name, Group_type)

# Merge group type information with the main dataframe
data_hours <- merge(df_hours, group_type)

### Statistical Analyses ####

# Fit a linear mixed-effects model to analyze movement by hour, group type, and weekday
mov_hours <- lmer(movement_hour ~ detection_hour + Hour + Group_type + Weekday +
                    (1 | Group_name), data = data_hours)

# Display model summary
summary(mov_hours)

#### Graph ####

# Create a boxplot of movement per hour, colored by weekday (Mondays vs. Thursdays)
ggplot(data = data_hours, aes(Hour, y = movement_hour)) +
  theme_classic() +
  theme(plot.title = element_text(size = 23, face = "bold"),
        axis.text = element_text(size = 12),
        axis.title = element_text(size = 14)) +
  geom_boxplot(aes(color = factor(Weekday, levels = c(2, 5))), position = position_dodge(0.9), lwd = 1) +
  xlab('Time Since Food Given') +
  ylab('Drum Movement per Hour') +  
  theme(legend.position = "right") +  # Adjust legend position as needed
  scale_color_discrete(name = "Days", labels = c("Mondays", "Thursdays"))
  
