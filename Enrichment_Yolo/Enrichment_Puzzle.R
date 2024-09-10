rm(list = ls())

# Load the libraries
lapply(packages, library, character.only = TRUE)
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
#plot
library(sjPlot) #for plotting lmer and glmer mods
library(sjmisc) 
library(effects)
library(sjstats)
library(correlation)
####
#The collection of pickle files that contain information about monkeys observed within a 
#specific region of interest (ROI). These pickle files include data that describe:
  
#Area of the Monkeys: The spatial region covered by the monkeys in the ROI.
#Number of Monkeys: The count of monkeys present in the ROI.
#Timestamp (in seconds): The time at which the observations were recorded. 
#The timestamp starts at 7 AM, with 0 corresponding to 7 AM.
#Additionally, the data represents the monkeys that are not overlapping with the front platform at the same time.


# Set working directory
setwd("path to working directory")

##### extract data from pickles files ####

# Import the pandas package
pd <- import("pandas")

# List all pickle files in the directory with the pattern "*interactions.pickle"
picklefiles = list.files(pattern="*interactions.pickle")

# Initialize an empty dataframe
df <- data.frame()

# Loop over all pickle files
for (file in 1:length(picklefiles)) {
  # Read the pickle file into a variable
  assign(picklefiles[file], G <- pd$read_pickle(picklefiles[file]))
  
  # Extract the number of monkeys and the area data
  numberm <- G$Number
  aream <- G$Area
  
  # Extract the timestamp in seconds (relative to 7 AM as 0)
  time <- G$TimeStamp
  
  # Extract group ID from the file name (first 3 characters)
  group_id <- substr(picklefiles[file], 1, 3)
  
  # Adjust the number of monkeys for Group G01 (to remove blue monkey counts)
  if (group_id == "G01") {
    for (n in 1:length(numberm)) {
      if (numberm[n] >= 1)
        numberm[n] = numberm[n] - 1
    }
  }
  
  # Extract the date from the file name (characters 4 to 14)
  date <- substr(picklefiles[file], 4, 14)
  
  # Define the time interval in seconds (1 hour)
  time_stamp <- 60 * 60
  
  # Create a dataframe with the number of monkeys and corresponding timestamp
  avg_nm <- data.frame("Number_Monkey" = numberm, "time_sec" = time)
  
  # Find the index where the timestamp equals 0 (7 AM)
  seven <- which(time == 0)
  
  # If the video starts after 7 AM, find the first occurrence of a timestamp that is a multiple of 3600
  if (length(seven) == 0) {
    seven <- which(time %% 3600 == 0)[1]
  }
  
  # Remove rows before 7 AM, if any
  if (seven != 1) {
    seven_index = seven - 1
    avg_nm <- as.data.frame(avg_nm[-seq_len(seven_index - 0), ])
  }
  
  # The final averaged number of monkeys is stored in Avg_noMonkey
  Avg_noMonkey <- avg_nm
  
  # Generate a sequence of time values from the 7 AM start time onwards, in hourly intervals
  Time <- seq(time[seven], time[length(time)], by = time_stamp)
  
  # If the last time value exceeds the maximum timestamp in Avg_noMonkey, 
  # remove extra time values
  if (Time[length(Time)] < Avg_noMonkey$time_sec[nrow(Avg_noMonkey)]) {
    torem <- which(Time[length(Time)] <= Avg_noMonkey$time_sec)
    Avg_noMonkey <- Avg_noMonkey[-torem,]
    Time <- Time[-length(Time)]
  }
  
  # Add an hour column to Avg_noMonkey
  Avg_noMonkey$hour <- 7 + (Avg_noMonkey$time_sec %/% 3600)
  
  # Convert seconds into formatted time (hh:mm:ss)
  hours <- Time %/% 3600 + 7
  minutes <- (Time %% 3600) %/% 60
  seconds <- Time %% 60
  formatted_time <- sprintf("%02d:%02d:%02d", hours, minutes, seconds)
  
  # Add group ID and date columns
  Group_ID <- rep(group_id, length(Time))
  Date <- rep(date, length(Time))
  
  # Group Avg_noMonkey by hour and calculate sum and average of monkeys
  Avg_noMonkey_hour <- Avg_noMonkey %>%
    group_by(hour) %>%
    summarise(sum_monkeys = sum(Number_Monkey),
              avg_monkeys = mean(Number_Monkey))
  
  # Create a dataframe with group ID, date, hour-based statistics, time in seconds, and formatted time
  avg_df <- data.frame(Group_ID, Date, Avg_noMonkey_hour, "Time_sec" = Time, "Time" = formatted_time)
  
  # Combine this dataframe with the overall dataframe
  df <- rbind(df, avg_df)
}

# Import additional metadata information
info_csv <- read.csv("path to Enrichment_Puzzle_Metadata.csv")

# Convert date formats to Date objects
info_csv$Date <- as.Date(info_csv$Date, format = "%d/%m/%Y")
df$Date <- as.Date(df$Date)

# Merge df with info_csv on Group_ID and Date columns, excluding not relevant columns from info_csv
df_all <- merge(df, info_csv[,-c(9,21,18,13,7)], by = c("Group_ID", "Date"), all.x = TRUE)

# Remove duplicate rows from the dataframe
df_all <- df_all %>% distinct()

# Create a factor variable for hours from the first two characters of the Time column
df_all$Hours <- as.factor(substr(df_all$Time, start = 1, stop = 2))

# Save the cleaned dataframe to a new CSV file
write.csv(df_all, "filename.csv", row.names = TRUE)

#####Statostical analyses####
# Stats section: Perform statistical modeling using glmer 
#(generalized linear mixed-effects model)
model <- glmer(sum_monkeys ~ Days_Since_Added + Group_Type + Hours
               + Blue_Monkey +
                 (1 | Group_ID), 
               offset = log(Group_No), family = poisson, data = df_all)

# Output the model summary and ANOVA
summary(model)
anova(model)

#####graphs#### 
# Calculate the mean of Group_No
mean_group_no <- mean(df_all$Group_No, na.rm = TRUE)

# Graph for Blue Monkey Presence
prediction_data_BM <- df_all %>%
  group_by(Hours, Blue_Monkey) %>%
  summarize(mean_sum_monkeys = mean(sum_monkeys))

blue_monkey <- ggplot(prediction_data_BM, aes(x = Blue_Monkey, y = mean_sum_monkeys, color = Blue_Monkey)) +
  theme_classic() +
  theme(plot.title = element_text(size = 23, face = "bold"),
        axis.text = element_text(size = 12),
        axis.title = element_text(size = 14)) +
  geom_boxplot(lwd = 1) +
  xlab('Blue Monkey Present?') +
  ylab('Number of Monkey Interacting') +
  theme(legend.position = "none") +
  theme(plot.title = element_text(hjust = 0.5))

# Prediction and graph for 'Days Since Added'
# Extract intercept and slope from the model coefficients
intercept <- fixef(model)["(Intercept)"]
slope <- fixef(model)["Days_Since_Added"]

# Calculate predictions for 'Days Since Added'
df_all$Pred <- exp(intercept + (slope * df_all$Days_Since_Added) + log(mean_group_no))

# Summarize the prediction data for days since added
prediction_data_days <- df_all %>%
  group_by(Days_Since_Added) %>%
  summarize(mean_sum_monkeys = mean(sum_monkeys),
            Pred_days = mean(Pred))

# Plot for 'Days Since Added'
day_since_added <- ggplot(prediction_data_days, aes(x = Days_Since_Added)) +
  geom_point(aes(y = mean_sum_monkeys), color = "black", size = 4) +  # Mean data points
  geom_line(aes(y = Pred_days), color = "red", size = 2) +  # Prediction line
  theme_classic() +
  theme(plot.title = element_text(size = 23, face = "bold"),
        axis.text = element_text(size = 12),
        axis.text.x = element_text(vjust = 0.5, hjust = 1),
        axis.title = element_text(size = 14)) +
  xlab('Days Since Added') +
  ylab('Average Detections of Monkeys Interacting') +
  theme(legend.position = "none") +
  theme(plot.title = element_text(hjust = 0.5))


# Prediction and graph for 'Hours'

# Extract intercept and slope for Hours from the model
intercept <- fixef(model)["(Intercept)"]
slope <- fixef(model)["Hours"]

# Calculate the predicted values for hours
df_all$Pred_hours <- exp(intercept + (slope * df_all$Hours) + log(mean_group_no))

# Summarize the prediction data for hours
prediction_data_hours <- df_all %>%
  group_by(Hours) %>%
  summarize(mean_sum_monkeys = mean(sum_monkeys),
            Pred_hours = mean(Pred_hours))

# Plot for 'Hours'
hours <- ggplot(prediction_data_hours, aes(x = Hours)) +
  geom_point(aes(y = mean_sum_monkeys), color = "black", size = 4) +  # Mean data points
  geom_line(aes(y = Pred_hours), color = "red", size = 2) +  # Prediction line
  theme_classic() +
  theme(plot.title = element_text(size = 23, face = "bold"),
        axis.text = element_text(size = 12),
        axis.text.x = element_text(vjust = 0.5, hjust = 1),
        axis.title = element_text(size = 14)) +
  xlab('Time of Day') + 
  ylab('Average Detections of Monkeys Interacting') +
  theme(legend.position = "none") +
  theme(plot.title = element_text(hjust = 0.5))

