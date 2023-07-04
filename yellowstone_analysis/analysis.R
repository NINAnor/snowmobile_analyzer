library(tidyverse)
library(glmmTMB)
library(DHARMa)
library(emmeans)
library(sjPlot)
library(sjmisc)
library(patchwork)
library(texreg)
library(lubridate)
library(lme4)
library(viridis)


################
# Set the path #
################
setwd("C:/Users/benjamin.cretois/Desktop/projects_research/YELLOWSTONE/Singing_in_Noise")
df_raw = read_csv("bird_event_data_processed_vars.csv") 

########################
# Set global variables #
########################

# Variables for the analysis
TIME_MAX=240 # We take the yellowstone data from 0 - 180 secondes before / after passage of snowmobile


#################
# Data wangling #
#################

# Aggregate the DF by interval of 15 seconds -> DONT FORGET THAT BIRDNET DOES PREDICTIONS EVERY 3 SECONDS!
df <- df_raw %>% mutate(interval = floor_date(Start, "15 seconds")) %>% 
  filter(during_ss == FALSE) %>% 
  group_by(interval, location) %>% 
  summarise(sum = n(), tmpf = mean(tmpf), relh=mean(relh), 
            alti=mean(alti), sknt=mean(sknt), 
            forest_canopy_cover_400m=mean(forest_canopy_cover_400m),
            closest_ss_before = mean(closest_ss_before),
            closest_ss_after = mean(closest_ss_after))  %>% 
  mutate(time_of_day = ifelse(hour(interval) >= 6 & hour(interval) < 12, "AM",
                              ifelse(hour(interval) >= 12 & hour(interval) < 16, "MM", "PM"))) %>% # the time_of_Day should be in relation to bird activity and not our time, right?
  ungroup() %>% 
  filter(location == 'YELLOFWS' | location == 'YELLMJ23' 
         |location == 'YELLFOPP' | location == 'YELLGVLL')
  
  
# Split the df into before and after
df_before <- df %>% 
  filter(closest_ss_before < TIME_MAX) 
df_after <- df %>% 
  filter(closest_ss_after < TIME_MAX)

#################
# Stat analysis #
#################

# Correlation between variables
var <- df %>% select(tmpf, relh, alti, sknt, forest_canopy_cover_400m)
cor(var) # All variables have really low correlation

########################################
# Look at the baseline number of calls #
########################################

# Baseline however unreliable as we may have missed some snowmobile detection 
# due to the high threshold we chose. Thus, we don't know the influence of snowmobile 
# outside the time range of our analysis (240s)

df_baseline <- df %>% 
  filter(closest_ss_before > 1000) %>% 
  filter(closest_ss_after > 1000)

df_baseline$location <- as.factor(df_baseline$location) # 10 sites
df_baseline$time_of_day <- as.factor(df_baseline$time_of_day) # 3 differnt time windows

# Transform to datetime
df_baseline$Date <- as.Date(df_baseline$interval)
df_baseline$Time <- format(as.POSIXct(df_baseline$interval), format = "%H:%M:%S")

df_baseline <- df_before %>%
  mutate(Year = str_sub(Date, 1, 4),
         Month = str_sub(Date, 6, 7))

# Model the baseline
m_before_baseline <- glmmTMB(log(sum) ~ 1 + scale(closest_ss_before) * time_of_day 
                    + scale(sknt) + scale(tmpf) + scale(relh)
                    + (1 | location) 
                    + (1 | Date), 
                    family=gaussian,
                    data=df_baseline 
)
test(emtrends(m_before_baseline, pairwise ~  time_of_day , var = 'closest_ss_before'))

# Model the baseline
m_after_baseline <- glmmTMB(log(sum) ~ 1 + scale(closest_ss_after) * time_of_day 
                             + scale(sknt) + scale(tmpf) + scale(relh)
                             + (1 | location) 
                             + (1 | Date), 
                             family=gaussian,
                             data=df_baseline 
)
test(emtrends(m_after_baseline, pairwise ~  time_of_day , var = 'closest_ss_after'))

###########################
# Fit the "before" model #
##########################

df_before$location <- as.factor(df_before$location) # 10 sites
df_before$time_of_day <- as.factor(df_before$time_of_day) # 3 differnt time windows

# Transform to datetime
df_before$Date <- as.Date(df_before$interval)
df_before$Time <- format(as.POSIXct(df_before$interval), format = "%H:%M:%S")

df_before1 <- df_before %>%
  mutate(Year = str_sub(Date, 1, 4),
         Month = str_sub(Date, 6, 7))

# Select the sites with the most observations
df_before2 <- df_before1 %>%
  filter(location == 'YELLOFWS' | location == 'YELLMJ23' 
         |location == 'YELLFOPP' | location == 'YELLGVLL')

df_before2 %>%
  group_by(time_of_day) %>%
  summarise(records = n()) %>%
  arrange(desc(records))

########################################
# Gaussian model for snowmobile before #
########################################
m_before <- glmmTMB(log(sum) ~ 1 + scale(closest_ss_before) * time_of_day 
                     + scale(sknt) + scale(tmpf) + scale(relh)
                     + (1 | location) 
                     + (1 | Date), 
                     family=gaussian,
                     data=df_before2 
)

# Diagnostic
m_before$sdr$pdHess ## Converged ?

res_before <- resid(m_before)
plot(fitted(m_before), res_before)
qqnorm(res)
qqline(res)
plot(density(res))

simulationOutput_before <- simulateResiduals(fittedModel = m_before, plot = F)
plot(simulationOutput_before)

# Model result
summary(m_before)
trend_before <- emtrends(m_before, pairwise ~  time_of_day , var = 'closest_ss_before')
test(trend_before)
results_before = as.tibble(test(trend_before))


###########################
# Fit the "after" model  #
##########################

df_after$location <- as.factor(df_after$location) # 10 sites
df_after$time_of_day <- as.factor(df_after$time_of_day) # 3 differnt time windows

df_after$Date <- as.Date(df_after$interval)
df_after$Time <- format(as.POSIXct(df_after$interval), format = "%H:%M:%S")


df_after1 <- df_after %>%
  mutate(Year = str_sub(Date, 1, 4),
         Month = str_sub(Date, 6, 7))

df_after1 %>%
  group_by(location) %>%
  summarise(records = n()) %>%
  arrange(desc(records))


df_after2 <- df_after1 %>%
  filter(location == 'YELLOFWS' | location == 'YELLMJ23' 
         |location == 'YELLFOPP' | location == 'YELLGVLL')


#######################################
# Gaussian model for snowmobile after #
#######################################

m_after <- glmmTMB(log(sum) ~ 1 + scale(closest_ss_after) * time_of_day 
                    + scale(sknt) + scale(tmpf) + scale(relh)
                    + (1 | location) 
                    + (1 | Date), 
                    family=gaussian,
                    data=df_after2 
)

# Diagnostic
m_after$sdr$pdHess ## Converged ?

res_after <- resid(m_after)
plot(fitted(m_after), res_after)
qqnorm(res)
qqline(res)
plot(density(res))

simulationOutput_after <- simulateResiduals(fittedModel = m_after, plot = F)
plot(simulationOutput_after)

# Model result
summary(m_after)
trend_after <- emtrends(m_after, pairwise ~  time_of_day , var = 'closest_ss_after')
test(trend_after)
results_after = as.tibble(test(trend_after))


######################
# DO THE PREDICTIONS #
######################

# Create a predictive dataset with mean conditions
pred_dataset = tibble(
  closest_ss_before = rep(seq(0, TIME_MAX-1, 1), 3),
  closest_ss_after = rep(seq(TIME_MAX-1, 0, -1), 3),
  time_of_day = c(rep("AM", TIME_MAX), rep("MM", TIME_MAX), rep("PM", TIME_MAX)),
  forest_canopy_cover_400m = mean(df$forest_canopy_cover_400m),
  alti=mean(df$alti),
  tmpf=mean(df$tmpf),
  relh = mean(df$relh),
  sknt = mean(df$sknt),
  location = "YELLMJ23",
  Date = mean.Date(as.Date(df$interval))
)


pred_sum_before = predict(m_before, pred_dataset, se.fit = TRUE, allow.new.levels = TRUE)
pred_dataset$mean_pred_sum_before = exp(pred_sum_before[[1]])
pred_dataset$lower_pred_sum_before = exp(pred_sum_before[[1]] - pred_sum_before[[2]])
pred_dataset$upper_pred_sum_before = exp(pred_sum_before[[1]] + pred_sum_before[[2]])


pred_sum_after = predict(m_after, pred_dataset, se.fit = TRUE, allow.new.levels = TRUE)
pred_dataset$mean_pred_sum_after = exp(pred_sum_after[[1]])
pred_dataset$lower_pred_sum_after = exp(pred_sum_after[[1]] - pred_sum_after[[2]])
pred_dataset$upper_pred_sum_after = exp(pred_sum_after[[1]] + pred_sum_after[[2]])

#################################
######### DO THE PLOTS ##########
#################################

# Variables for the plots
significance_size=4
text_size = 14
axis_text = 14
title_size=16
size_line = 1


pred_dataset$significance = ifelse(pred_dataset$time_of_day == "PM", "N.S.", "***")

lab = c("AM"="Morning - [6AM and 12PM] ", "MM"="Afternoon - [12PM, 4PM]", "PM"="Evening - [4PM, 12AM]")

significance_before <- tibble(time_of_day=c("AM", "MM", "PM"),
                              significance = paste("pvalue =", signif(results_before$emtrends$p.value, 2)))

boxplot_before <- df_before %>% 
  mutate(ranges = cut(closest_ss_before, 16)) %>% 
  group_by(ranges, time_of_day) %>%
  summarise(sum=mean(sum, na.rm=TRUE)) %>%
  mutate(range_num=as.numeric(ranges)*(TIME_MAX/16)) %>% 
  ggplot(aes(x=range_num, y=sum, col=time_of_day, fill=time_of_day)) +
  geom_histogram(stat="identity", alpha=.3, show.legend = FALSE) +
  theme_bw() +
  facet_wrap(~time_of_day, labeller = as_labeller(lab), ncol=1) +
  scale_x_reverse() +
  coord_cartesian(ylim=c(1.2, 1.7)) +
  xlab(" ") +
  ylab("Number of bird vocalizations") +
  geom_line(data=pred_dataset, aes(x=closest_ss_before, y=mean_pred_sum_before, col=time_of_day, fill=time_of_day), show.legend = FALSE, size=size_line) +
  geom_ribbon(data=pred_dataset, aes(x=closest_ss_before, y=mean_pred_sum_before, ymin=lower_pred_sum_before, ymax=upper_pred_sum_before), alpha=.4, show.legend = FALSE) +
  scale_fill_manual(values=c("#403891ff", "#a65c85ff", "#f68f46ff")) +
  scale_color_manual(values=c("#403891ff", "#a65c85ff", "#f68f46ff")) +
  geom_text(data=significance_before, aes(x=TIME_MAX, y=1.65, label=significance),  size=significance_size, vjust=0, hjust=0, col="red") + 
  theme(text = element_text(size=text_size),
        axis.text = element_text(size=axis_text),
        axis.title = element_text(size=title_size),
        strip.text = element_text(size=axis_text)) 
boxplot_before

significance_after <- tibble(time_of_day=c("AM", "MM", "PM"),
                              significance = paste("pvalue =", signif(results_after$emtrends$p.value, 2)))

boxplot_after <- df_after %>% 
  mutate(ranges = cut(closest_ss_after, 16)) %>% 
  group_by(ranges, time_of_day) %>%
  summarise(sum=mean(sum, na.rm=TRUE)) %>%
  mutate(range_num=as.numeric(ranges)*(TIME_MAX/16)) %>% 
  ggplot(aes(x=range_num, y=sum, col=time_of_day, fill=time_of_day)) +
  geom_histogram(stat="identity", alpha=.3, show.legend = FALSE) +
  theme_bw() +
  facet_wrap(~time_of_day, labeller = as_labeller(lab), ncol=1) +
  coord_cartesian(ylim=c(1.2, 1.7)) +
  xlab(" ") +
  ylab(" ") +
  geom_line(data=pred_dataset, aes(x=closest_ss_after, y=mean_pred_sum_after, col=time_of_day, fill=time_of_day), show.legend = FALSE, size=size_line) +
  geom_ribbon(data=pred_dataset, aes(x=closest_ss_after, y=mean_pred_sum_after, ymin=lower_pred_sum_after, ymax=upper_pred_sum_after), alpha=.4, show.legend = FALSE) +
  scale_fill_manual(values=c("#403891ff", "#a65c85ff", "#f68f46ff")) +
  scale_color_manual(values=c("#403891ff", "#a65c85ff", "#f68f46ff")) +
  geom_text(data=significance_after, aes(x=0, y=1.65, label=significance),  size=significance_size, vjust=0, hjust=0, col="red") +
  theme(text = element_text(size=text_size),
        axis.text = element_text(size=axis_text),
        axis.title = element_text(size=title_size),
        strip.text = element_text(size=axis_text),
        axis.text.y = element_blank(),
        axis.ticks = element_blank())


fig_trends = (boxplot_before | boxplot_after) +
  plot_annotation(tag_levels = "A") +
  xlab("Time before (A) and after (B) detection of a snowmobile (in seconds)") +
  theme(axis.title.x = element_text(hjust=1.2)) 
fig_trends

ggsave("Figures_MS/Figure3.png" ,fig_trends ,dpi=300, width = 9, height = 7.5)
