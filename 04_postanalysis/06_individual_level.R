# Individual level statistics and plots
library(tidyverse)
library(hrbrthemes)
library(sjmisc)
library(qvalue)
library(glue)
library(viridisLite)
library(see)
library(texreg)
library(patchwork)
library(lemon)

mappings <- read_csv("target_cat_mappings.csv") %>% 
  rename(
    "target" = index,
    "item_cat" = category,
    "item_name" = target,
  )

# load data (all_brain)
common_path <- "bids/derivatives/meg-derivatives/"
primary_dirs <- list.files(common_path);


main_data <- c()
count <- 0

for (dir in primary_dirs) {
  if (!(dir %in% c("grand_ave"))) {
    print(dir)
    current_dir = paste(common_path,dir, "/brain-space/visual_model/", sep = "")
    files = list.files(current_dir, pattern = "*.csv")
    for (csv in files) {
      count <- count + 1
      csv_split <- str_split(csv,c("_","-"))
      analysis <- csv_split[[2]][4]
      if (str_contains(csv, "tr")) {
        level <- csv_split[[2]][6]
      } else {
        level <- csv_split[[2]][5]
      }
      current_csv <- read_csv(paste(current_dir, csv, sep = ""), 
                                col_types = cols()) %>% 
        mutate(subject = dir,
               analysis = analysis,
               level = level)
      
      main_data[[count]] <- current_csv
      
    }
  }
}

main_data <- do.call(rbind, main_data)

# calculate mean similarity over items for each time point
true_mean_sim <- main_data %>%
  mutate(
    # calculate similarity
    similarity = distance) %>% 
  group_by(time, analysis, level,subject) %>% 
  # calculate mean similarity over items for each time point
  summarise(sd = sd(similarity), similarity = mean(similarity)) 

true_mean_sim_wide <- true_mean_sim %>% 
  pivot_wider(names_from=analysis,values_from = c(sd, similarity)) %>% 
  rename("cum" = similarity_cum,
         "tr" = similarity_tr) %>% 
  mutate(true_sim_diff = cum-tr) 

perm_data <- c()
count <- 0

for (dir in primary_dirs) {
  if (!(dir %in% c("grand_ave"))) {
    print(dir)
    current_dir = paste(common_path,dir, "/brain-space/visual_model/perm/merged/", sep = "")
    files = list.files(current_dir, pattern = "*.csv")
    for (csv in files) {
      count <- count+1
      current_csv <- read_csv(paste(current_dir, csv, sep = ""), 
                              col_types = cols())
      
      perm_data[[count]] <- current_csv
      
    }
  }
}

perm_data <- do.call(rbind, perm_data)

perm_data <- perm_data %>% 
  filter(perm_new<1000) %>% 
  mutate(cum=-cum_perm,
         tr=-tr_perm)


pval_calc <- function(perm_data, real_data, model,var){
  perm_mat <-matrix(perm_data  %>% filter(level==model) %>%  pull(var),nrow=50,byrow=TRUE) * -1
  pval <- empPvals((real_data %>% filter(level==model) %>% arrange(time) %>% pull(var)) * -1, perm_mat, pool = FALSE)
  pval_correct <- p.adjust(pval,method="fdr")
  return (tibble(level=model,time=0:49,pval=pval,pval_correct=pval_correct))
}

pvals_all <- c()
count <- 0
for (subject in c(1:19)){
  print(subject)
  subject <- str_pad(subject, 2, pad = "0")
  sub = glue("sub-{subject}")
  
  for (analysis in c("cum","tr")){
  count <- count + 1
    
  pvals <- map_dfr(c("V1","V2","V4","IT","decoder","word2vec"), ~pval_calc(perm_data %>% filter(subject==sub),
                                                                               true_mean_sim_wide %>% filter(subject==sub),.x,analysis))
  pvals_all[[count]] <- pvals %>% mutate(subject=sub,analysis=analysis)
  }
  
  }

pvals_all <- do.call(rbind, pvals_all)
  
pvals_all <- pvals_all %>% 
  mutate(signif = if_else(pval_correct < 0.05,TRUE,NA)) %>% 
  mutate(timesig = if_else(signif, time, NA)) %>% 
  pivot_wider(names_from=analysis,values_from=timesig) %>% 
  mutate("cum_sig"=cum,
         "tr_sig"=tr)
  


true_mean_sim_t <- main_data %>% 
  pivot_wider(names_from=analysis,values_from=distance) %>% 
  mutate(cum_true_sim = cum,
         tr_true_sim = tr) %>% 
  group_by(time, level,subject) %>% 
  summarise(true_sim_diff = mean(cum_true_sim - tr_true_sim),
            sd_diff = sd(cum_true_sim- tr_true_sim)/sqrt(60),
            ttest = abs(t.test(x = cum_true_sim,y = tr_true_sim, paired = TRUE)$statistic))


pval_calc_t <- function(perm_data, real_data, model){
  perm_mat <- matrix(perm_data  %>% filter(level==model, time > 0) %>%  pull(ttest) %>%  abs(),nrow=49,byrow=TRUE)
  pval <- empPvals(real_data %>% filter(level==model, time > 0) %>% arrange(time) %>% pull(ttest) %>%  abs(), perm_mat, pool = FALSE)
  pval_correct <- p.adjust(pval,method="fdr")
  return (tibble(level=model,time=1:49,pval=pval,pval_correct=pval_correct))
}


pvals_all_t <- c()
count <- 0
for (subject in c(1:19)){
  count <- count + 1
  print(subject)
  subject <- str_pad(subject, 2, pad = "0")
  sub = glue("sub-{subject}")
  
pvals_t <- map_dfr(c("V1","V2","V4","IT","decoder","word2vec"), ~pval_calc_t(perm_data %>% filter(subject==sub),
                                                                             true_mean_sim_t %>% filter(subject==sub),.x))

pvals_all_t[[count]] <- pvals_t %>% mutate(subject=sub)
}

pvals_all_t <- do.call(rbind, pvals_all_t)


signi <- true_mean_sim_t %>%
  left_join(pvals_all_t,by=c("level","time","subject")) %>% 
  mutate(signif_diff = if_else(pval < 0.05,TRUE,NA)) %>% 
  mutate(timesig_diff = if_else(signif_diff, time, NA)) 

plot_data <- true_mean_sim_wide %>% 
  left_join(signi %>% select(time, level, timesig_diff,subject)) %>% 
  left_join(pvals_all %>% select(time, level, cum_sig,tr_sig,subject))

options(bitmapType="cairo")

for (level_name in c("V1","V2","V4","IT","word2vec")){
  # cumulative vs sliding
cumvstrplt <- plot_data %>% 
    filter(level==level_name) %>% 
    mutate(subject2 = as.numeric(str_remove(subject, "sub-"))) %>%  
    ggplot(aes(x=time*20))+
    geom_line(aes(y=abs(cum), color = "cumulative"))+
    geom_line(aes(y=abs(tr), color = "sliding"))+
    facet_rep_wrap(~subject2,ncol = 4) +
    scale_color_brewer(type = "qual", palette = "Set2", name = "Model type")+
    geom_ribbon(aes(ymin = abs(cum - sd_cum/sqrt(60)),
                    ymax = abs(cum + sd_cum/sqrt(60)),fill="cumulative"), alpha = 0.15) +
    geom_ribbon(aes(ymin = abs(tr - sd_tr/sqrt(60)),
                    ymax = abs(tr + sd_tr/sqrt(60)),fill="sliding"), alpha = 0.15) +
    geom_point(aes(x=timesig_diff*20,y = abs(mean(tr) + 4 * sd(tr)),
                  shape="models differ"), size = 0.5, inherit.aes = FALSE)+
    geom_point(aes(x=cum_sig*20,y = abs(mean(tr) + 3.5* sd(tr)),
                   color="cumulative"), size = 0.5, inherit.aes = FALSE)+
    geom_point(aes(x=tr_sig*20,y = abs(mean(tr) + 3* sd(tr)),
                   color="sliding"), size = 0.5, inherit.aes = FALSE)+
    scale_fill_brewer(type = "qual", palette = "Set2", name = "Model type") +
    scale_shape_manual(values=c(15,15,15),name="")+
    ylab("Distance")+
    xlab("Time (ms)") +
    theme_bw() +
    theme(legend.position = c(0.9, 0.075),
          legend.margin = margin(),
          legend.title = element_blank(),
          plot.margin = margin(5,10,5,5),
          panel.grid = element_blank(),
          strip.background = element_blank(),
          panel.border = element_rect(size = 1)) +
  guides(colour = guide_legend(order = 2, reverse = TRUE), fill = guide_legend(order = 2, reverse = TRUE), shape = guide_legend(order = 1))

  
    
    saveRDS(cumvstrplt, glue("figures/{level_name}_indiv_tr_cum.RDS"))
}
  

part_max <- function(x, prop, ...){
  
  # sequence starts at 0
  x <- x - x[1]
  
  # set full maximum
  real_max <- max(x)
  
  current_max <- -Inf
  # stop when reached % of maximum
  for (i in x) {
    if (i >= prop * real_max) {
      current_max <- i
      break
    }
  }
  return(c(which(x == current_max), current_max + x[1]))
}


plateaus <- main_data %>%
  filter(analysis == "cum") %>%
  filter(level != "decoder") %>%
  group_by(level, subject, target) %>%
  arrange(time) %>%
  mutate(similarity = -distance) %>%
  mutate(run_max_t = part_max(similarity, prop = 0.95, eps = 0.01)[1],
         run_max = part_max(similarity, prop = 0.95, eps = 0.01)[2])

m <- afex::mixed(run_max_t~subject * level + (1|target),data=plateaus %>% filter(time==0))

m

emmeans::emmeans(m,pairwise~level)

emmeans::emmeans(m,pairwise~level|subject)$emmeans %>% 
  as_tibble() %>% 
  group_by(level) %>% 
  summarise(min=min(emmean)*20,max=max(emmean)*20,se=mean(SE)*20)


emmeans::emmeans(m,pairwise~level|subject)$emmeans %>% 
  as_tibble() %>% 
  group_by(subject) %>% 
  summarise(min=min(emmean)*20,max=max(emmean)*20,se=mean(SE)*20)


emmeans::emmeans(m,pairwise~level|subject)$emmeans %>% 
  as_tibble() %>% 
  mutate(level=factor(level,levels=c("V1","V2","V4","IT","word2vec"))) %>% 
  arrange(level) %>% 
  ggplot(aes(x=level,y=emmean))+
  geom_boxplot()+
  geom_point(aes(color=subject))



levels_m <- afex::mixed(run_max_t ~ level + (1|subject), 
                        data = plateaus)


all_corr <- c()
done <- c()
count <- 0 
for(level1 in c("V1","V2","V4","IT","word2vec")){
  for(level2 in c("V1","V2","V4","IT","word2vec")){
    if (level1==level2){
      next
    }
    current_comb1 = paste0(level1,level2)
    current_comb2 = paste0(level2,level1)
    if ((current_comb1 %in% done)|(current_comb2 %in% done)){
      next
    }else{
      done <- c(done,current_comb1,current_comb2)
    }
    for (subject in c(1:19)){
      print(paste(level1,level2,subject))
      count <- count+1
      subject <- str_pad(subject, 2, pad = "0")
      sub = glue("sub-{subject}")
      df <- plateaus %>% 
        select(run_max_t,level,target,subject) %>%
        unique() %>% 
        filter(subject==sub,level %in% c(level1,level2)) %>% 
        pivot_wider(names_from=level,values_from=run_max_t) 
      
      c <- cor(df[level1], df[level2], method = c("pearson"), 
          use = "complete.obs")[1]
      current <- tibble(subject=sub,l1=level1,l2=level2,correl=c)
      all_corr[[count]] <- current
    }
  }}


all_corr <- do.call(rbind, all_corr)



corr_indiv <- all_corr %>% 
  mutate(l1=factor(l1,levels=c("V1","V2","V4","IT","word2vec")),
         l2=factor(l2,levels=c("V1","V2","V4","IT","word2vec"))) %>% 
  mutate(subject = as.numeric(str_remove(subject, "sub-"))) %>%
  ggplot(aes(x=l1,y=l2,fill=correl))+
  geom_tile()+
  facet_wrap(~subject)+
  geom_text(aes(label = round(correl,2)), size = 2.5) +
  scale_fill_distiller(palette = "Reds", direction = 1, name = "Correlation") +
  theme_bw() +
  theme(
    panel.grid = element_blank(),
    panel.border = element_rect(size = 1),
    strip.background = element_blank(),
  )+
  xlab("") +
  ylab("") +
  coord_equal()

saveRDS(corr_indiv, "figures/corr_indiv.RDS")

ggsave("figures/plateau_corr_indiv.pdf", corr_indiv, height = 20, width = 20, units = "cm")


em_corplot <- emmeans::emmeans(m,pairwise~level|subject)$emmeans %>% 
  as_tibble() %>% 
  select(subject,level,emmean) %>% 
  pivot_wider(names_from=level,values_from=emmean) %>% 
  select(-subject) %>% 
  as.matrix() %>% 
  cor() %>% 
  as.matrix() %>% 
  as_tibble(rownames = "l1") %>% 
  pivot_longer(-l1, names_to = "l2") %>% 
  mutate(l1=ordered(l1,levels=c("V1","V2","V4","IT","word2vec")),
         l2=ordered(l2,levels=c("V1","V2","V4","IT","word2vec"))) %>% 
  filter(l1 < l2) %>% 
  ggplot(aes(x = l1, y = l2)) +
  geom_tile(aes(fill = value)) +
  geom_text(aes(label = round(value,2)), size = 3) +
  scale_fill_distiller(type = "seq", palette = "Reds", direction = 1, name = "Correlation") +
  theme_classic() + 
  xlab("") +
  ylab("")

saveRDS(em_corplot, "figures/em_corplot.RDS")

std_plot <- main_data %>%
  filter(analysis=="cum",level!="decoder") %>% 
  group_by(level, subject, time) %>%
  mutate(distance = mean(distance)) %>% 
  mutate(level = factor(level, levels = c("V1", "V2", "V4", "IT", "word2vec"))) %>% 
  ungroup() %>%
  group_by(level, time) %>%
  summarise(m = sd(-distance)) %>%
  ungroup() %>% 
  group_by(level) %>% 
  ggplot(aes(x = time * 20, y = m, color = level)) +
  geom_line() +
  ylab("Standard deviation") +
  xlab("Time (ms)")+
  facet_wrap(~level,scales="free_y") +
  scale_color_brewer(type = "qual", palette = "Set1") +
  theme_bw() +
  theme(legend.position = "none",
        panel.grid = element_blank(),
        strip.background = element_blank(),
        panel.border = element_rect(size = 1),
        plot.margin = unit(c(0.5,0.5,0.5,0.5), "cm"))

saveRDS(std_plot, "figures/std_plot.RDS")

subject_em <- emmeans::emmeans(m,pairwise~level|subject)$emmeans %>% 
  as_tibble() %>% 
  mutate(level=factor(level,levels=c("V1","V2","V4","IT","word2vec"))) %>% 
  select(subject,level,emmean,SE,asymp.LCL,asymp.UCL) %>% 
  ggplot(aes(x=emmean*20,y=level,color=level))+
  geom_point()+
  geom_pointrange(aes(xmin = asymp.LCL*20, xmax = asymp.UCL*20,fill=level), shape = 22) +
  facet_wrap(~subject)+
  ylab("")+
  xlab("Time (ms)")+
  theme_bw()+
  scale_color_brewer(type = "qual", palette = "Set1") +
  scale_fill_brewer(type = "qual", palette = "Set1") +
  theme(
    legend.position = "none",
    panel.grid = element_blank(),
    panel.border = element_rect(size = 1),
    strip.background = element_blank(),
  )

saveRDS(subject_em, "figures/subject_em.RDS")


corplot <- em_corplot + coord_equal() +
  theme_bw() +
  theme(panel.grid = element_blank(),
        panel.border = element_rect(size = 1),
        legend.position = "none")

saveRDS(corplot, "figures/corplot.RDS")
