library(tuneR)
library(tidyverse)
library(seewave)
library(khroma)

afile_path <- "C:/Users/benjamin.cretois/Desktop/projects_research/YELLOWSTONE/YELLOFWS_20100129_090634-WINDOW.wav"

i_wav <- readWave(afile_path)
spect <- spectro(wave = i_wav, plot=F)


# Make the plot in ggplot

# set the colnames and rownames
colnames(spect$amp) <- spect$time
rownames(spect$amp) <- spect$freq

spect_df <-
  spect$amp %>% 
  # coerce the row names to a column
  as_tibble(rownames = "freq") %>% 
  # pivot to long format
  pivot_longer(
    # all columns except freq
    -freq, 
    names_to = "time", 
    values_to = "amp"
  ) %>% 
  # since they were names before,
  # freq and time need conversion to numeric
  mutate(
    freq = as.numeric(freq),
    time = as.numeric(time)
  )

# Dynamic range
dyn = -50
spect_df_floor <- 
  spect_df %>% 
  mutate(
    amp_floor = case_when(
      amp < dyn ~ dyn,
      TRUE ~ amp  
    )
  )


spect_df_floor %>% 
  ggplot(aes(time, freq))+
  stat_contour(
    aes(
      z = amp_floor,
      fill = after_stat(level)
    ),
    geom = "polygon",
    bins = 300
  )+
  scale_fill_batlow()+
  guides(fill = "none")+
  labs(
    x = "time (s)",
    y = "frequency (kHz)",
    title = "spectrogram contour plot"
  )
  #coord_cartesian(ylim = c(0, 10)) +
  # Plot window for snowmobile detection
  geom_rect(aes(xmin = start_sn_event, xmax = end_sn_event, ymin = 0, ymax=10))
  # Plot window for 

