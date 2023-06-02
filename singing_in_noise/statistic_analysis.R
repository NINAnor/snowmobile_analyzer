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
setwd("C:/Users/benjamin.cretois/Desktop/projects_research/YELLOWSTONE/analysis")
df_raw = read_csv("bird_event_data_processed_vars.csv") 

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
  filter(closest_ss_before < 600) %>% 
  select(! closest_ss_after)
df_after <- df %>% 
  filter(closest_ss_after < 600)

###############################
# Preliminary analysis: plots #
###############################
library(hexbin)

cut(df_before$closest_ss_before, 60)

# Number of bird calls vs time before / after passage of snowmobile
boxplot_before <- df_before %>% 
  mutate(ranges = cut(closest_ss_before, 15)) %>% 
  group_by(ranges, time_of_day) %>%
  summarise(sum=mean(sum, na.rm=TRUE)) %>%
  mutate(range_num=as.numeric(ranges)) %>% 
  ggplot(aes(x=range_num, y=sum)) +
  geom_histogram(stat="identity") +
  theme_bw() +
  facet_wrap(~time_of_day) +
  scale_x_reverse() 
boxplot_before

# Number of bird calls vs time before / after passage of snowmobile
boxplot_before <- df_before %>% 
  ggplot(aes(x=-closest_ss_before, y=sum, colour = time_of_day, fill = time_of_day)) +
  geom_point(aes(alpha=.7), show.legend = FALSE) +
  theme_bw() +
  scale_fill_viridis(discrete=TRUE) +
  scale_colour_viridis(discrete=TRUE) 
boxplot_before


boxplot_after <- df_after %>% 
  ggplot(aes(x=closest_ss_after, y=as.factor(sum), colour = time_of_day, fill = time_of_day)) +
  geom_violin(aes(alpha=.7)) +
  theme_bw() +
  scale_fill_viridis(discrete=TRUE) +
  scale_colour_viridis(discrete=TRUE) 

(boxplot_before | boxplot_after)

#################
# Stat analysis #
#################

# Correlation between variables
var <- df %>% select(tmpf, relh, alti, sknt, forest_canopy_cover_400m)
cor(var) # All variables have really low correlation

###########################
# Fit the "before" model #
##########################

df_before$location <- as.factor(df_before$location) # 10 sites
df_before$time_of_day <- as.factor(df_before$time_of_day) # 3 differnt time windows

# Transform to datetime
df_before$Date <- as.Date(df_before$interval)
df_before$Time <- format(as.POSIXct(df_before$interval), format = "%H:%M:%S")

unique(df_before$Date) # several years and months.

df_before1 <- df_before %>%
  mutate(Year = str_sub(Date, 1, 4),
         Month = str_sub(Date, 6, 7))

boxplot(sum ~ factor(location), 
        data = df_before,
        ylab = "Sum",
        xlab = "Location",
        cex.lab = 1.5)

df_before %>%
  group_by(location) %>%
  summarise(records = n()) %>%
  arrange(desc(records))

# Select the sites with the most observations
df_before2 <- df_before1 %>%
  filter(location == 'YELLOFWS' | location == 'YELLMJ23' 
         |location == 'YELLFOPP' | location == 'YELLGVLL')

df_before2 %>%
  group_by(time_of_day) %>%
  summarise(records = n()) %>%
  arrange(desc(records))


# POISSON MODEL
################
m_before1 <- glmmTMB(sum ~ 1 + scale(closest_ss_before) * location * time_of_day 
                    + scale(sknt) + scale(tmpf) + scale(relh)
                    + (1 | Date), 
                    family=poisson,
                    data=df_before2
)

summary(m_before1)

#drop1(m_before1, test = "Chi")
m_before2$sdr$pdHess ## Converged ?

#Check overdispersion
performance::check_overdispersion(m_before1)
simulationOutput <- simulateResiduals(fittedModel = m_before1, plot = F)
#residuals(simulationOutput)
plot(simulationOutput)
plot_model(m_before1, type = 'pred', terms = c('closest_ss_before', 'time_of_day')) +
  theme_classic()


#emmeans(m_before2, pairwise ~ time_of_day|closest_ss_before)
emtrends(m_before2, pairwise ~  time_of_day , var = 'closest_ss_before')


# Gaussian model
#################
m_before2 <- glmmTMB(log(sum) ~ 1 + scale(closest_ss_before) * time_of_day 
                     + scale(sknt) + scale(tmpf) + scale(relh)
                     + (1 | location) 
                     + (1 | Date), 
                     family=gaussian,
                     data=df_before2 
)

summary(m_before2)


m_before2$sdr$pdHess ## Converged ?

plot_before <- plot_model(m_before2, type = 'pred', terms = c('closest_ss_before', 'time_of_day')) +
  theme_classic() + 
  scale_x_reverse() +
  theme(legend.position = "none")

emmeans(m_before2, pairwise ~ time_of_day|closest_ss_before)
emtrends(m_before2, pairwise ~  time_of_day , var = 'closest_ss_before')


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

df_after1$Year
df_after1$Month


boxplot(sum ~ factor(location), 
        data = df_after,
        ylab = "Sum",
        xlab = "Location",
        cex.lab = 1.5)


df_after1 %>%
  group_by(location) %>%
  summarise(records = n()) %>%
  arrange(desc(records))


df_after2 <- df_after1 %>%
  filter(location == 'YELLOFWS' | location == 'YELLMJ23' 
         |location == 'YELLFOPP' | location == 'YELLGVLL')


m_after2 <- glmmTMB(sum ~ 1 + scale(closest_ss_after) * time_of_day 
                    + scale(sknt) + scale(tmpf) + scale(relh)
                    + (1 | location) 
                    + (1 | Date), 
                    #+ (1 | time_of_day),        
                    family=poisson,
                    #dispformula = ~1+location,
                    data=df_after2 
)


summary(m_after2)

#drop1(m_after2, test = "Chi")
m_after2$sdr$pdHess ## Converged ?

#Check overdispersion
performance::check_overdispersion(m_after2)
simulationOutput <- simulateResiduals(fittedModel = m_after2, plot = F)
#residuals(simulationOutput)
plot(simulationOutput)

#' Can this model cope with the 25% of zeros?
#testZeroInflation(m_before)
#' Yes.

plot_model(m_after2, type = 'pred', terms = c('closest_ss_after', 'time_of_day')) +
  theme_classic()


#emmeans(m_before2, pairwise ~ time_of_day|closest_ss_before)

emtrends(m_after2, pairwise ~  time_of_day , var = 'closest_ss_after')




m_after2 <- glmmTMB(log(sum) ~ 1 + scale(closest_ss_after) * time_of_day 
                    + scale(sknt) + scale(tmpf) + scale(relh)
                    + (1 | location) 
                    + (1 | Date), 
                    #+ (1 | time_of_day),        
                    family=gaussian,
                    #dispformula = ~1+location,
                    data=df_after2 
)

summary(m_after2)


m_after3$sdr$pdHess ## Converged ?

plot_after <- plot_model(m_after3, type = 'pred', terms = c('closest_ss_after', 'time_of_day')) +
  theme_classic()

#emmeans(m_before2, pairwise ~ time_of_day|closest_ss_before)

trend_after <- emtrends(m_after2, pairwise ~  time_of_day , var = 'closest_ss_after')
trend_after


######################
# DO THE PREDICTIONS #
######################

# Create a predictive dataset with mean conditions
pred_dataset = tibble(
  closest_ss_before = rep(seq(0, 599, 1), 3),
  closest_ss_after = rep(seq(599, 0, -1), 3),
  time_of_day = c(rep("AM", 600), rep("MM", 600), rep("PM", 600)),
  forest_canopy_cover_400m = mean(df$forest_canopy_cover_400m),
  alti=mean(df$alti),
  tmpf=mean(df$tmpf),
  relh = mean(df$relh),
  sknt = mean(df$sknt),
  location = "YELLMJ23",
  Date = mean.Date(as.Date(df$interval))
)


pred_sum_before = predict(m_before2, pred_dataset, se.fit = TRUE, allow.new.levels = TRUE)
pred_dataset$mean_pred_sum_before = exp(pred_sum_before[[1]])
pred_dataset$lower_pred_sum_before = exp(pred_sum_before[[1]] - pred_sum_before[[2]])
pred_dataset$upper_pred_sum_before = exp(pred_sum_before[[1]] + pred_sum_before[[2]])


pred_sum_after = predict(m_after2, pred_dataset, se.fit = TRUE, allow.new.levels = TRUE)
pred_dataset$mean_pred_sum_after = exp(pred_sum_after[[1]])
pred_dataset$lower_pred_sum_after = exp(pred_sum_after[[1]] - pred_sum_after[[2]])
pred_dataset$upper_pred_sum_after = exp(pred_sum_after[[1]] + pred_sum_after[[2]])

pred_dataset$significance = ifelse(pred_dataset$time_of_day == "PM", "N.S.", "***")

lab = c("AM"="Morning", "MM"="Middle day", "PM"="Evening")

text_size = 12
axis_text = 12
title_size=16
size_line = 1

boxplot_before <- df_before %>% 
  mutate(ranges = cut(closest_ss_before, 10)) %>% 
  group_by(ranges, time_of_day) %>%
  summarise(sum=mean(sum, na.rm=TRUE)) %>%
  mutate(range_num=as.numeric(ranges)*60) %>% 
  ggplot(aes(x=range_num, y=sum, col=time_of_day, fill=time_of_day)) +
  geom_histogram(stat="identity", alpha=.3, show.legend = FALSE) +
  theme_bw() +
  facet_wrap(~time_of_day, labeller = as_labeller(lab), ncol=1) +
  scale_x_reverse() +
  coord_cartesian(ylim=c(1.2, 1.7)) +
  xlab(" ") +
  ylab("Number of bird vocalisations") +
  geom_line(data=pred_dataset, aes(x=closest_ss_before, y=mean_pred_sum_before, col=time_of_day, fill=time_of_day), show.legend = FALSE, size=size_line) +
  geom_ribbon(data=pred_dataset, aes(x=closest_ss_before, y=mean_pred_sum_before, ymin=lower_pred_sum_before, ymax=upper_pred_sum_before), alpha=.4, show.legend = FALSE) +
  scale_fill_manual(values=c("#403891ff", "#a65c85ff", "#f68f46ff")) +
  scale_color_manual(values=c("#403891ff", "#a65c85ff", "#f68f46ff")) +
  geom_text(data=pred_dataset, aes(x=-Inf, y=-Inf, label=significance),  size=4, vjust=-16, hjust=1.5, col="red") +
  theme(text = element_text(size=text_size),
        axis.text = element_text(size=axis_text),
        axis.title = element_text(size=title_size),
        strip.text = element_text(size=axis_text)) 

boxplot_after <- df_after %>% 
  mutate(ranges = cut(closest_ss_after, 10)) %>% 
  group_by(ranges, time_of_day) %>%
  summarise(sum=mean(sum, na.rm=TRUE)) %>%
  mutate(range_num=as.numeric(ranges)*60) %>% 
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
  geom_text(data=pred_dataset, aes(x=-Inf, y=-Inf, label=significance),  size=4, vjust=-16, hjust=-17, col="red") +
  theme(text = element_text(size=text_size),
        axis.text = element_text(size=axis_text),
        axis.title = element_text(size=title_size),
        strip.text = element_text(size=axis_text),
        axis.text.y = element_blank(),
        axis.ticks = element_blank())


(boxplot_before | boxplot_after) +
  plot_annotation(tag_levels = "A") +
  xlab("Time before (A) and after (B) passage of a snowmobile (in seconds)") +
  theme(axis.title.x = element_text(hjust=1.2)) 


#################################
# Make plots for the manuscript #
#################################
(plot_before | plot_after)
