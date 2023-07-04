library(tidyverse)
library(patchwork)
library(scales)

# Create the DF
reference = c("TP", "FP")
l_filtering <- c("MC 0.95+", 
  "MC 0.95+, HNR 0.1+", 
  "MC 0.95+, HNR 0.1+, DL 6+", 
  "MC 0.99+, HNR 0.1+, DL 6+")

df_cm <- tibble(Filtering = l_filtering, #c("Filtering 1", "Filtering 2", "Filtering 3", "Filtering 4"),
             TP = c(27, 27,26.15, 22.65),
             FP = c(267,12.8, 10.3, 4.9),
             FN = c(0.1, 0.1, 0.95, 4.45),
             TN = c(16920, 194640, 194820, 195360)) %>% 
  pivot_longer(cols = !Filtering, names_to = "variable", values_to = "values") %>%
  mutate(Type = ifelse(variable == reference, "Positive detection", "Negative detection")) %>% 
  group_by(Filtering, Type) %>% 
  mutate(Proportion = values / sum(values)) %>% 
  group_by(Filtering) %>% 
  mutate(model_proportion = values / sum(values))

df_metrics = tibble(Filtering = l_filtering, #c("Filtering 1", "Filtering 2", "Filtering 3", "Filtering 4"),
                    Precision = c(0.11, 0.5, 0.65, 0.78),
                    Recall = c(0.98, 0.98, 0.94, 0.77),
                    F1 = c(0.20, 0.66, 0.77, 0.78)) %>% 
  pivot_longer(cols = !Filtering, names_to = "variable", values_to = "values")

# Factor the variables
df_cm$variable <- factor(df_cm$variable, levels = c("TP","FP","FN","TN"))
df_metrics$variable <- factor(df_metrics$variable, levels = c("Precision","Recall","F1"))

################## 
# Make the plots #
##################

confmat_text_size=5
text_size = 14
axis_text = 14
title_size=16

### Confusion matrix

a <- ggplot(data=df_cm, aes(x=Filtering, y=variable, fill=Type, alpha=-Proportion)) +
  geom_tile() +
  geom_text(aes(label = values, vjust = .5, fontface  = "bold", alpha = 1), show.legend = FALSE, size=confmat_text_size) +
  scale_fill_manual(values = c("Positive detection"= "#00A572", "Negative detection"="orange")) +
  theme_classic() +
  labs(
    title = "Time (in min) detected in each class",
    y = " ",
    x = "Filtering type"
  ) +
  scale_x_discrete(labels = label_wrap(10)) +
  scale_y_discrete(labels = c("True positive", "False positive", "False negative", "True negative"))
a
### Model performance
b <- ggplot(data=df_metrics, aes(x=Filtering, y=variable, fill=values)) +
         geom_tile() +
  scale_fill_gradient(low = "#b8627dff", high = "#efe350ff") +
  geom_text(aes(label = values), vjust = .5, fontface  = "bold", alpha = 1, size=confmat_text_size) +
  theme_classic() +
  labs(
    title = "Models performance metrics",
    y = "Metrics",
    x = "Filtering type"
  )+
  scale_x_discrete(labels = label_wrap(10))

conf_mat = a / b + plot_annotation(tag_level = "A") & theme(
  plot.tag = element_text(face = 'bold', size = title_size),
  plot.title = element_text(color="black", size=title_size, face="bold.italic"),
  axis.title.x = element_text(color="black", size=title_size),
  axis.title.y = element_text(color="black", size=title_size),
  axis.text.x = element_text(color="black", size=text_size),
  axis.text.y = element_text(color="black", size=text_size),
  legend.text = element_text(color="black", size=text_size),
  legend.title = element_text(color="black", size=text_size)
) 

conf_mat

ggsave("Figures_MS/Figure2.png" ,conf_mat ,dpi=300)
