# Cross-temporal plot.

library(tidyverse)
library(viridis)
library(qvalue)
library(scales)
library(patchwork)
library(glue)
library(comprehenr)

path <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/"
path_ext <- paste0(path,"visual_model/","temporal-cross/")

files <- list.files(path_ext,"*.csv")

main_data = list()
count <- 0


# read csvs corresponding to different analysis types
for (csv in files) {
  count <- count + 1
  level <- str_split(csv,"_")[[1]][1]
  current_csv <- read_csv(paste(path_ext, csv, sep = ""), col_types = cols()) %>% 
    mutate(level = level)
  main_data[[count]] <- current_csv
}

main_data <- do.call(rbind, main_data)

main_data <- main_data %>% 
  mutate(across(level, factor, levels = c("V1", "V2","V4","IT","decoder","word2vec"))) %>% 
  group_by(time1,time2,level) %>% 
  summarise(m = mean(distance))


# check number of permutation files
path <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/permutations/temporal-cross/{level}"

for (level in c("V1","V2","V4","IT","word2vec")){
  
  current <- list.files(glue(path),".csv")
  print(paste(glue("{level}:"),length(current)))
  
  perm <-current %>% 
    tibble() %>% 
    rename("perm"=".") %>% 
    mutate(perm=str_split(perm,"_")) %>% 
    separate(perm,c("1","2","3","4","perm")) %>% 
    mutate(perm=as.numeric(perm)) %>% 
    pull(perm)
  
  missing <- c()
  for (i in c(1:1000)){
    if(!(i %in% perm)){
      missing <- c(missing,i)
    }
  }
  
  print(length(missing))
}


# read the files wherm perms are merged and averaged over items per perm (smaller files)
path <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/permutations/temporal-cross/"
files <- list.files(path,"*avg_merged.csv")

perm_data = list()
count <- 0

# read csvs corresponding to different analysis types
for (csv in files) {
  count <- count + 1
  level <- str_split(csv,"_")[[1]][1]
  current_csv <- read_csv(paste(path, csv, sep = ""), col_types = cols()) %>% 
    mutate(level = level)
  perm_data[[count]] <- current_csv
}

perm_data <- do.call(rbind, perm_data)

# pvalue calculation and fdr correction
pval_calc <- function(perm_data, real_data, model){
  
  current_perm <- perm_data  %>% filter(level==model) %>% arrange(time1,time2) %>%  pull(mean_distance)

  perm_mat <-matrix(current_perm,nrow=2500,byrow = TRUE)
  
  current_real <- main_data %>% filter(level==model) %>% arrange(time1,time2) %>% pull(m)

  pval <- empPvals(-current_real, -perm_mat, pool = FALSE)
  pval_correct <- p.adjust(pval,method="fdr")
  return (tibble(level=model,pval=pval,pval_correct=pval_correct,
                 time1=main_data %>% filter(level==model) %>% arrange(time1,time2) %>% pull(time1),
                 time2=main_data %>% filter(level==model) %>% arrange(time1,time2) %>% pull(time2)))
}

pvals <- map_dfr(c("V1","V2","V4","IT","decoder","word2vec"), ~pval_calc(perm_data,main_data,.x))


pvals %>% 
  ggplot(aes(x=time1,y=time2,fill=pval_correct))+
  geom_tile()+
  facet_wrap(~level)


merged_main_perm <- main_data %>% 
  left_join(pvals)

tc_fig <- function(l,pval_c=TRUE){
  if(pval_c==TRUE){
  f <- merged_main_perm %>% 
  ungroup() %>% 
  mutate(final_value = if_else(pval_correct < 0.05, m,NA),
         across(level, factor, levels = c("V1", "V2","V4","IT","decoder","word2vec"))) %>% 
  filter((level == l)) %>% 
    group_by(level) %>% 
    mutate(scaled_m = scale(final_value)[,1])}else
  {
    f <- merged_main_perm %>% 
      ungroup() %>% 
      mutate(final_value = m,
             across(level, factor, levels = c("V1", "V2","V4","IT","decoder","word2vec"))) %>% 
      filter((level == l)) %>%  
      group_by(level) %>% 
      mutate(scaled_m = scale(final_value)[,1])
  }
  p <-f %>% 
    #filter(time1 > 3) %>% 
  ggplot(aes(x = time1* 20, y = time2 * 20, fill = final_value)) +
  geom_tile() +
  #geom_tile(aes(alpha=final_value),fill="white") +
  #scale_fill_distiller(palette = "Spectral") +
  scale_fill_viridis(option = "inferno", discrete = F,na.value = "white",
                     direction = -1,
                    name = "Distance",guide = guide_colourbar(title.position="top",
                                                                          )) +
  xlim(0, 1000) +
  ylim(0, 1000) +
  theme_bw() +
  coord_fixed() +
  theme(
    panel.grid = element_blank(),
          strip.background = element_blank(),
          panel.border = element_rect(size = 1)
  ) +
  xlab("Train time (ms)") +
  ylab("Test time (ms)") +
  facet_wrap(~level,nrow=1)+
  scale_alpha_manual(values = c(0,1), breaks = c("good", "bad"), guide=FALSE)
  return (p)
  }

visual_figs <- c()
count <- 0
for (l in c("V1","V2","V4","IT","word2vec")){
  count <- count + 1
  current <- tc_fig(l)
  visual_figs[[count]] <- current
  saveRDS(object = current, file = glue("figures/grand_average/temporal_cross_heatmap_{l}_p.RDS"))
}

visual_figs_orig <- c()
count <- 0
for (l in c("V1","V2","V4","IT","word2vec")) {
  count <- count + 1
  current <- tc_fig(l, pval_c = FALSE)
  visual_figs_orig[[count]] <- current
  saveRDS(object = current, file = glue("figures/grand_average/temporal_cross_heatmap_{l}_o.RDS"))
}


layout <- "
AABB##
AABBEE
CCDDEE
CCDD##
"

tc_plot_p <- visual_figs[[1]]+visual_figs[[2]] + visual_figs[[3]] + visual_figs[[4]] + visual_figs[[5]] +
  plot_layout(design=layout,tag_level = "new") +
  plot_annotation(tag_levels = c(tag_levels = list(c('A', '','','','B'))))

tc_plot_o <- visual_figs_orig[[1]]+visual_figs_orig[[2]] + visual_figs_orig[[3]] + visual_figs_orig[[4]] + visual_figs_orig[[5]] +
  plot_layout(design = layout,tag_level = "new") +
  plot_annotation(tag_levels = c(tag_levels = list(c('A', '','','','B'))))


# checking starting points of generalization


V1_plot <- readRDS(glue("figures/grand_average/temporal_cross_heatmap_V1_p.RDS"))

V1_plot +
  geom_segment(aes(x = 230, y = 230, xend = 1000, yend = 230), linetype = "dashed") +
  geom_segment(aes(x = 230, y = 230, xend = 230, yend = 1000), linetype = "dashed")

V2_plot <- readRDS(glue("figures/grand_average/temporal_cross_heatmap_V2_p.RDS"))

V2_plot +
  geom_segment(aes(x = 230, y = 230, xend = 1000, yend = 230), linetype = "dashed") +
  geom_segment(aes(x = 230, y = 230, xend = 230, yend = 1000), linetype = "dashed")

V4_plot <- readRDS(glue("figures/grand_average/temporal_cross_heatmap_V4_p.RDS"))

V4_plot +
  geom_segment(aes(x = 250, y = 250, xend = 1000, yend = 250), linetype = "dashed") +
  geom_segment(aes(x = 250, y = 250, xend = 250, yend = 1000), linetype = "dashed")

IT_plot <- readRDS(glue("figures/grand_average/temporal_cross_heatmap_IT_p.RDS"))

IT_plot + geom_segment(aes(x = 250, y = 250, xend = 1000, yend = 250), linetype = "dashed") +
  geom_segment(aes(x = 250, y = 250, xend = 250, yend = 1000), linetype = "dashed")

word2vec_plot <- readRDS(glue("figures/grand_average/temporal_cross_heatmap_word2vec_p.RDS"))

word2vec_plot + geom_segment(aes(x = 270, y = 270, xend = 1000, yend = 270), linetype = "dashed") +
  geom_segment(aes(x = 270, y = 270, xend = 270, yend = 1000), linetype = "dashed")

