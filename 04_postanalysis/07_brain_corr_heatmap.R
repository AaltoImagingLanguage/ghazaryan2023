# Heatmap of brain response correlation
# libraries needed
library(tidyverse)
library(R.matlab)
library(glue)
library(lsa)
library(viridis)
library(patchwork)

# load data
path <- "bids/derivatives/meg-derivatives/grand_ave/matricies/modality-picture.mat"
m <- readMat(path)
megdata <- m$megdata

# calculate correlations

datalist = list()
# times of interest
tof <- list(c(1,5), c(1,9),c(1,13), c(1,17),c(1,21),c(1,25),c(1,29),c(1,33))

for (t in seq_along(tof)) {
  # extract the data from the time window
  t1 = tof[t][[1]][1]
  t2 = tof[t][[1]][2]
  current_chunk <- megdata[,,t1:t2]
  reshaped_chunk <- t(matrix(current_chunk, 60))
  # caclulate pairwise correlations
  corr <- cor(reshaped_chunk, method = "pearson") %>% 
    as_tibble() %>% 
    add_column(item1 = 1:60) %>% 
    gather(key = item1, value = "value") %>% 
    mutate(item1 = as.numeric(str_remove(as.character(item1),"V"))) %>% 
    add_column(item2 = rep(1:60, times = 60),
               t1 = t1,
               t2 = t2,
               t = glue("{0}-{t2*20} ms"))
  datalist[[t]] <- corr
}
big_data = do.call(rbind, datalist)


annot_text <- tibble(t="0-420 ms",animals="animals",
                     body="bodyparts", buildings = "buildings",
                     nature = "nature", human = "characters",
                     tools = "tools", vehicles = "vehicles")

labels <- c(animals="animals",
            body="bodyparts", buildings = "buildings",
            nature = "nature", human = "characters",
            tools = "tools", vehicles = "vehicles")

all_plots <- c()
count <- 0 
for (time1 in unique(big_data$t1)){
  print(time1)
  for (time2 in unique(big_data$t2)){
    print(time2)
  count <- count + 1
  current_data <- big_data %>% 
    filter(t1==time1,t2==time2)
  
  cp <- current_data %>% 
    ggplot(aes(x = item1, y = item2, fill = value)) +
    geom_tile() +
    #scale_fill_viridis(option = "magma", discrete = F) +
    scale_fill_distiller(palette = "Spectral",direction=-1, 
                         name = "Corr.", guide = guide_colorbar(barwidth = 0.5, 
                                                                draw.llim = TRUE,
                                                                draw.ulim = TRUE),
                         breaks = ~scales::breaks_width(width = 0.2)(.x)) +
    theme_bw()+
    facet_wrap(~t)+
    theme_bw() +
    xlab("") + ylab("") +
    coord_fixed(clip = F) +
    theme(
      axis.text = element_blank(),
      axis.ticks = element_blank(),
      strip.background = element_blank(),
      panel.grid = element_blank(),
      legend.text = element_text(size = 8),
      strip.text = element_text(size = 8),
      panel.spacing.x = unit(1.2, "cm"),
      legend.title = element_text(size = 8),
      panel.border = element_rect(size = 0.25),
      legend.key.width = unit(8, "pt"),
      legend.key.height = unit(8, "pt"),
      legend.box.spacing = unit(4, "pt"),
      legend.box.margin = margin(0, 0, 0, 0, "pt"),
      plot.margin = margin(0, 0, 0, -10, "pt"),
      panel.spacing.y = unit(0, "pt")
    )
  
  if(time2==21){
      cp <- cp +
        geom_text(data = annot_text, x = -5, y = 58, label=labels[[7]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, x = -5, y = 50, label=labels[[6]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, x = -5, y = 41, label=labels[[5]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, x = -5, y = 32, label=labels[[4]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, x = -5, y = 23, label=labels[[3]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, x = -5, y = 14, label=labels[[2]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, x = -5, y = 5, label=labels[[1]], inherit.aes = F, hjust = "right", size = 7 / .pt)+
        # x axis
        geom_text(data = annot_text, y = -5, x = 62, angle = 45, label = labels[[7]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, y = -5, x = 53, angle = 45, label = labels[[6]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, y = -5, x = 43, angle = 45, label = labels[[5]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, y = -5, x = 33, angle = 45, label = labels[[4]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, y = -5, x = 22, angle = 45, label = labels[[3]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, y = -5, x = 12, angle = 45, label = labels[[2]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, y = -5, x = 2, angle = 45, label = labels[[1]], inherit.aes = F, hjust = "right", size = 7 / .pt)
    }

  all_plots[[count]] <- cp
  
  }}

layout = "ABCD
          EFGH"
cum <- all_plots[[1]]+all_plots[[2]]+all_plots[[3]]+all_plots[[4]]+
all_plots[[5]]+all_plots[[6]]+all_plots[[7]]+all_plots[[8]]+
  plot_layout(design = layout)

cum

## sliding

datalist = list()
# times of interest
tof <- list(c(4,5), c(8,9),c(12,13), c(16,17),c(20,21),c(24,25),c(28,29),c(32,33))

for (t in seq_along(tof)) {
  # extract the data from the time window
  t1 = tof[t][[1]][1]
  t2 = tof[t][[1]][2]
  current_chunk <- megdata[,,t1:t2]
  reshaped_chunk <- t(matrix(current_chunk, 60))
  # caclulate pairwise correlations
  corr <- cor(reshaped_chunk, method = "pearson") %>% 
    as_tibble() %>% 
    add_column(item1 = 1:60) %>% 
    gather(key = item1, value = "value") %>% 
    mutate(item1 = as.numeric(str_remove(as.character(item1),"V"))) %>% 
    add_column(item2 = rep(1:60, times = 60),
               t1 = t1,
               t2 = t2,
               t = glue("{t1*20}-{t2*20} ms"))
  datalist[[t]] <- corr
}
big_data = do.call(rbind, datalist)


annot_text <- tibble(t="400-420 ms",animals="animals",
                     body="bodyparts", buildings = "buildings",
                     nature = "nature", human = "characters",
                     tools = "tools", vehicles = "vehicles")

labels <- c(animals="animals",
            body="bodyparts", buildings = "buildings",
            nature = "nature", human = "characters",
            tools = "tools", vehicles = "vehicles")

all_plots <- c()
count <- 0 
for (time1 in unique(big_data$t1)){
  print(time1)
  for (time2 in unique(big_data$t2)){
    print(time2)
    if (time2-time1!=1){
      next
    }
    count <- count + 1
    current_data <- big_data %>% 
      filter(t1==time1,t2==time2)
    
    cp <- current_data %>% 
      ggplot(aes(x = item1, y = item2, fill = value)) +
      geom_tile() +
      #scale_fill_viridis(option = "magma", discrete = F) +
      scale_fill_distiller(palette = "Spectral",direction=-1,
                           name = "Corr.", guide = guide_colorbar(barwidth = 0.5,
                                                                  draw.llim = TRUE,
                                                                  draw.ulim = TRUE),
                           breaks = ~scales::breaks_width(width = 0.2)(.x)) +
      theme_bw()+
      facet_wrap(~t)+
      theme_bw() +
      xlab("") + ylab("") +
      coord_fixed(clip = F) +
      theme(
        axis.text = element_blank(),
        axis.ticks = element_blank(),
        strip.background = element_blank(),
        panel.grid = element_blank(),
        legend.text = element_text(size = 8),
        strip.text = element_text(size = 8),
        panel.spacing.x = unit(1.2, "cm"),
        legend.title = element_text(size = 8),
        panel.border = element_rect(size = 0.25),
        legend.key.width = unit(8, "pt"),
        legend.key.height = unit(8, "pt"),
        legend.box.spacing = unit(4, "pt"),
        legend.box.margin = margin(0, 0, 0, 0, "pt"),
        plot.margin = margin(0, 0, 0, 0, "pt")
        )
    if(time2==21){
      cp <- cp +
        geom_text(data = annot_text, x = -5, y = 58, label=labels[[7]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, x = -5, y = 50, label=labels[[6]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, x = -5, y = 41, label=labels[[5]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, x = -5, y = 32, label=labels[[4]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, x = -5, y = 23, label=labels[[3]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, x = -5, y = 14, label=labels[[2]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, x = -5, y = 5, label=labels[[1]], inherit.aes = F, hjust = "right", size = 7 / .pt)+
        # x axis
        geom_text(data = annot_text, y = -5, x = 62, angle = 45, label = labels[[7]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, y = -5, x = 53, angle = 45, label = labels[[6]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, y = -5, x = 43, angle = 45, label = labels[[5]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, y = -5, x = 33, angle = 45, label = labels[[4]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, y = -5, x = 22, angle = 45, label = labels[[3]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, y = -5, x = 12, angle = 45, label = labels[[2]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
        geom_text(data = annot_text, y = -5, x = 2, angle = 45, label = labels[[1]], inherit.aes = F, hjust = "right", size = 7 / .pt)
    }

    all_plots[[count]] <- cp
    
  }}

layout = "ABCD
          EFGH"

tr <- all_plots[[1]]+all_plots[[2]]+all_plots[[3]]+all_plots[[4]]+
  all_plots[[5]]+all_plots[[6]]+all_plots[[7]]+all_plots[[8]]+
  plot_layout(design = layout)


brain <- tr/cum + plot_annotation(tag_levels = c(tag_levels = list(c('A',' ',' ','  ',
                                                          ' ',' ',' ','  ',
                                                          'B',' ',' ','  ',
                                                     ' ',' ',' ','  '))),
                                theme = theme(text = element_text(size = 8), plot.margin = margin(0, 0, 0, 20))) &
  theme(plot.tag = element_text(size = 10))


ggsave( "figures/brain_dsm.pdf",height=176,width=176, units = "mm")

model_dsms <- c()
count = 0
#model DSM
for (level in c("V1","V2","V4","IT","word2vec")) {
  count=count+1
  if (level !="word2vec"){
path <- glue("CORnet_vectors/CORnet_{level}.mat")}else{
  path <- glue("CORnet_vectors/word2vec.mat")}
    
m <- readMat(path)
m <- t(m$vectors)
test <- (cosine(m)) %>% 
  as_tibble() %>% 
  add_column(item1 = 1:60) %>% 
  gather(key = item1,value="value") %>% 
  add_column(item2 = rep(1:60, times=60)) %>% 
  mutate(item1 = as.numeric(str_remove(as.character(item1),"V")),
         level=level)


current <- test %>% 
  ggplot(aes(x=item1,y=item2,fill=value))+
  geom_tile()+
  scale_fill_distiller(palette = "Spectral",direction=-1,
                       name = "Cosine\nsimilarity", guide = guide_colorbar(barwidth = 0.5,
                                                                           draw.llim = TRUE,
                                                                           draw.ulim = TRUE),
                       breaks = ~scales::breaks_extended(n = 4)(.x)
                       )+
  facet_wrap(~level)+
  theme_bw()+
  coord_fixed(clip = "off")+
  theme(
    axis.title = element_blank(),
    axis.text = element_blank(),
    axis.ticks = element_blank(),
    strip.background = element_blank(),
    panel.grid = element_blank(),
    legend.text = element_text(size = 8),
    strip.text = element_text(size = 8),
    panel.spacing.x = unit(1.2, "cm"),
    legend.key.width = unit(8, "pt"),
    legend.key.height = unit(8, "pt"),
    legend.box.spacing = unit(4, "pt"),
    legend.title = element_text(size = 8),
    panel.border = element_rect(size = 0.25),
    legend.box.margin = margin(0, 0, 0, 0, "pt"),
    plot.margin = margin(0, 0, 0, 0, "pt")
  ) 

if (level=="IT"){
  current <- current+
    geom_text(data = annot_text, x = -5, y = 58, label=labels[[7]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
    geom_text(data = annot_text, x = -5, y = 50, label=labels[[6]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
    geom_text(data = annot_text, x = -5, y = 41, label=labels[[5]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
    geom_text(data = annot_text, x = -5, y = 32, label=labels[[4]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
    geom_text(data = annot_text, x = -5, y = 23, label=labels[[3]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
    geom_text(data = annot_text, x = -5, y = 14, label=labels[[2]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
    geom_text(data = annot_text, x = -5, y = 5, label=labels[[1]], inherit.aes = F, hjust = "right", size = 7 / .pt)+
    # x axis
    geom_text(data = annot_text, y = -5, x = 58, angle = 45, label = labels[[7]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
    geom_text(data = annot_text, y = -5, x = 50, angle = 45, label = labels[[6]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
    geom_text(data = annot_text, y = -5, x = 41, angle = 45, label = labels[[5]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
    geom_text(data = annot_text, y = -5, x = 32, angle = 45, label = labels[[4]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
    geom_text(data = annot_text, y = -5, x = 23, angle = 45, label = labels[[3]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
    geom_text(data = annot_text, y = -5, x = 13, angle = 45, label = labels[[2]], inherit.aes = F, hjust = "right", size = 7 / .pt) +
    geom_text(data = annot_text, y = -5, x = 5, angle = 45, label = labels[[1]], inherit.aes = F, hjust = "right", size = 7 / .pt)
   
}

  model_dsms[[count]] <- current

}

model_dsm <- model_dsms[[1]]+model_dsms[[2]]+model_dsms[[3]]+model_dsms[[4]]+model_dsms[[5]] + plot_annotation(
  theme = theme(text = element_text(size = 8), plot.margin = margin(0, 0, 0, 35)))

ggsave( "figures/model_dsm.pdf",height=150,width=176, units = "mm")
