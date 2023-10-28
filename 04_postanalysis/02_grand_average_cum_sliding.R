# Cumulative vs sliding plot
library(tidyverse)
library(viridis)
library(sjmisc)
library(glue)
library(patchwork)
library(qvalue)


# load data
path <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/"

main_data = list()


count <- 0

files <- list.files(path,pattern = "*.csv")
# read csvs corresponding to different analysis types
for (csv in files) {
  count <- count + 1
  type <- str_split(csv,"_")[[1]][2]
  level <- str_split(csv,"_")[[1]][1]
  current_csv <- read_csv(paste(path, csv, sep = ""), col_types = cols()) %>% 
    mutate(type = type,
           level = level)
  main_data[[count]] <- current_csv
}

main_data <- do.call(rbind, main_data)

# first check
main_data %>%
  mutate(across(level, factor, levels = c("V1", "V2","V4","IT","decoder","word2vec"))) %>% 
  group_by(time,type,level) %>% 
  summarise(similarity=mean(-distance)) %>% 
  ggplot(aes(x=time*20,y=similarity,color=type))+
  geom_line()+
  facet_wrap(~level,nrow=2,scales="free_y") +
  xlab("time") +
  ylab("similarity (negative distance)")+
  geom_vline(xintercept = 9*20)


# calculate mean similarity over items for each time point
true_mean_sim <- main_data %>%
  mutate(
    # calculate similarity
    similarity = -distance) %>% 
  group_by(time, type, level) %>% 
  # calculate mean similarity over items for each time point
  summarise(sd = sd(similarity), similarity = mean(similarity))


true_mean_sim_wide <- true_mean_sim %>% 
  pivot_wider(names_from=type,values_from=c(sd, similarity)) %>% 
  rename("cum_true" = similarity_cum,
         "tr_true" = similarity_tr) %>% 
  mutate(true_sim_diff = cum_true-tr_true)


### t test
true_mean_sim_t <- main_data %>% 
  pivot_wider(names_from=type,values_from=distance) %>% 
  rename("cum_true" = cum,
         "tr_true" = tr) %>% 
  mutate(cum_true_sim = -cum_true,
         tr_true_sim = -tr_true) %>% 
  group_by(time, level) %>% 
  summarise(true_sim_diff = mean(cum_true - tr_true),
            sd_diff = sd(cum_true - tr_true)/sqrt(60),
         ttest = abs(t.test(x = cum_true_sim, y = tr_true_sim, paired = TRUE)$statistic))




# check number of permutation files
path <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/permutations/{level}"

for (level in c("V1","V2","V4","IT","word2vec")){
  
  current <- list.files(glue(path),".csv")

  perm <-current %>% 
    tibble() %>% 
    rename("perm"=".") %>% 
    mutate(perm=str_split(perm,"_")) %>% 
    separate(perm,c("1","2","type","4","perm"))
  
  for (t in c("cum","tr")){
  current_perm <- perm%>% 
    filter(type==t) %>% 
    mutate(perm=as.numeric(perm)) %>% 
    pull(perm)
  
  missing <- c()
  for (i in c(1:1000)){
    if(!(i %in% current_perm)){
      missing <- c(missing,i)
    }
  }
  print(paste(level,t,length(missing)))
  
  }
}

path <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/"

perm_data <- readRDS(paste0(path,"permutations/all_perm_merged.RDS"))


perm_data_mean <- perm_data %>% 
  mutate(similarity= -distance) %>%
  group_by(level,perm,time,type) %>% 
  summarise(similarity=mean(similarity))

perm_data_t <- perm_data %>% 
  mutate(perm=str_split(perm,"_", simplify = TRUE)[, 3]) %>% 
  pivot_wider(names_from = type, values_from = distance) %>%
  rename("cum_perm" = cum,
         "tr_perm" = tr) %>% 
  mutate(cum_perm_sim = -cum_perm,
         tr_perm_sim = -tr_perm) %>% 
  ungroup() %>% 
  group_by(time, level, perm) %>% 
  arrange(target) %>% 
  summarise(true_sim_diff = mean(cum_perm)-mean(tr_perm),
         ttest = t.test(cum_perm_sim, tr_perm_sim, paired = TRUE)$statistic)

perm_data_mean %>% 
  group_by(time,type,level) %>% 
  summarise(m=mean(similarity)) %>% 
  ggplot(aes(x=time,y=m,color=type))+
  geom_line()+
  facet_wrap(~level,scales = "free_y")

perm_mean_sim_wide <- perm_data_mean %>%
  mutate(perm=str_split(perm,"_")[[1]][3]) %>% 
  spread(key=type,value=similarity) %>% 
  rename("cum_perm" = cum,
         "tr_perm" = tr) %>% 
  mutate(perm_sim_diff = cum_perm-tr_perm) %>% 
  mutate(perm = as.numeric(str_split(perm,"-")[[1]][2]))

perm_mean_sim_wide <-perm_mean_sim_wide %>% 
  arrange(time,level,perm)

pval_calc <- function(perm_data, real_data, model){
  perm_mat <-matrix(perm_data  %>% filter(level==model) %>%  pull(perm_sim_diff),nrow=50,byrow=TRUE)
  pval <- empPvals(real_data %>% filter(level==model) %>% arrange(time) %>% pull(true_sim_diff), perm_mat, pool = FALSE)
  pval_correct <- p.adjust(pval,method="fdr")
  return (tibble(level=model,time=0:49,pval=pval,pval_correct=pval_correct))
}

pval_calc_t <- function(perm_data, real_data, model){
  perm_mat <- matrix(perm_data  %>% filter(level==model, time > 0) %>%  pull(ttest) %>%  abs(),nrow=49,byrow=TRUE)
  pval <- empPvals(real_data %>% filter(level==model, time > 0) %>% arrange(time) %>% pull(ttest) %>%  abs(), perm_mat, pool = FALSE)
  pval_correct <- p.adjust(pval,method="fdr")
  return (tibble(level=model,time=1:49,pval=pval,pval_correct=pval_correct))
}

pvals <- map_dfr(c("V1","V2","V4","IT","decoder","word2vec"), ~pval_calc(perm_mean_sim_wide,true_mean_sim_wide,.x))

pvals_t <- map_dfr(c("V1","V2","V4","IT","decoder","word2vec"), ~pval_calc_t(perm_data_t, true_mean_sim_t,.x))

signi <- true_mean_sim_t %>%
  left_join(pvals_t,by=c("level","time")) %>% 
  mutate(signif = if_else(pval < 0.05,TRUE,NA)) 

pval_calc <- function(perm_data, real_data, model,var){
  perm_mat <-matrix(perm_data  %>% filter(level==model) %>%  pull(var),nrow=50,byrow=TRUE)
  pval <- empPvals(real_data %>% filter(level==model) %>% arrange(time) %>% pull(var), perm_mat, pool = FALSE)
  pval_correct <- p.adjust(pval,method="fdr")
  return (tibble(level=model,time=0:49,pval=pval,pval_correct=pval_correct))
}

perm_mean_sim_wide_new <-perm_mean_sim_wide %>% 
  rename("cum"=cum_perm,
         "tr"= tr_perm)


true_mean_sim_wide_new <- true_mean_sim_wide %>% 
  rename("cum"=cum_true,
         "tr"= tr_true)

pvals_all <- c()
count <- 0
  for (analysis in c("cum","tr")){
    count <- count + 1
    
    pvals <- map_dfr(c("V1","V2","V4","IT","decoder","word2vec"), ~pval_calc(perm_mean_sim_wide_new,
                                                                             true_mean_sim_wide_new,.x,analysis))
    pvals_all[[count]] <- pvals %>% mutate(analysis=analysis)
  }
  


pvals_all <- do.call(rbind, pvals_all)

pvals_all <-pvals_all %>% 
  mutate(signif = if_else(pval_correct < 0.05,TRUE,NA)) %>% 
  mutate(timesig = if_else(signif, time, NA)) %>% 
  pivot_wider(names_from=analysis,values_from=timesig) %>% 
  mutate("cum_sig"=cum,
         "tr_sig"=tr)


# plateau calculation
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
  filter(type == "cum") %>%
  filter(level != "decoder") %>%
  group_by(level, target) %>%
  arrange(time) %>%
  mutate(similarity = -distance) %>%
  mutate(run_max_t = part_max(similarity, prop = 0.95, eps = 0.01)[1],
         run_max = part_max(similarity, prop = 0.95, eps = 0.01)[2])




m <- afex::mixed(run_max_t~level+(1|target),data=plateaus)

plateau_stat <- emmeans::emmeans(m,pairwise~level)$emmeans %>% 
  as_tibble()
  



main_data %>%
  filter(level != "decoder", type == "cum") %>% 
  group_by(level, target) %>%
  arrange(time) %>%
  mutate(similarity = -distance) %>%
  mutate(run_max_t = part_max(similarity, prop = 0.95, eps = 0.01)[1], run_max = part_max(similarity, prop = 0.95, eps = 0.01)[2]) %>%
  select(level, run_max_t, run_max) %>%
  ungroup() %>%
  group_by(level) %>% 
  ggplot(aes(x = run_max_t*20, fill = level)) +
  stat_summary(fun = median, aes(y = level))



draw_key_cust <- function(data, params, size) {
  if (data$colour == "green") {
    data$size <- .5
    draw_key_vpath(data, params, size)
  } else {
    data$size <- 2
    draw_key_path(data, params, size)
  }
}


threshold <- inner_join(
  true_mean_sim_wide, 
  perm_data_t %>% group_by(time, level) %>% summarise(diff = quantile(true_sim_diff, 0.05))) %>% 
  filter(level != "decoder")

perm_q <- perm_mean_sim_wide %>% 
  filter(level != "decoder") %>% 
  group_by(level,time) %>% 
  summarise(q_cum = quantile(cum_perm,0.95),
            q_tr = quantile(tr_perm,0.95))


options(bitmapType="cairo")

plot_data <- true_mean_sim_wide %>% 
  inner_join(perm_q) %>% 
  left_join(signi %>% filter(level != "decoder") %>% select(time, level, signif)) %>% 
  left_join(pvals_all %>% select(time, level, cum_sig,tr_sig))


plot_data %>% 
  unique() %>% 
  group_by(level) %>% 
  arrange(time) %>% 
  filter(!(is.na(signif))) %>% 
  arrange(level, time) %>% 
  ggplot(aes(x=time,y=signif))+
  geom_point()+
  facet_wrap(~level,scales="free_x") +
  scale_x_continuous(n.breaks = 25)

scaleFUN <- function(x) sprintf("%.1f", x)


for (l in c("V1","V2","V4","IT","word2vec")){
  print(l)
  
  cumvstr_vis <- plot_data %>% 
    filter(level==l) %>% 
    mutate(timesig = if_else(signif, time, NA)) %>% 
    mutate(across(level, factor, levels = c("V1", "V2","V4","IT","word2vec"))) %>% 
    ggplot(aes(x=time*20),width=2)+
    geom_ribbon(aes(ymin = abs(cum_true - sd_cum/sqrt(60)),
                    ymax = abs(cum_true + sd_cum/sqrt(60)), fill="cumulative"), alpha = 0.15) +
    geom_ribbon(aes(ymin = abs(tr_true - sd_tr/sqrt(60)),
                    ymax = abs(tr_true + sd_tr/sqrt(60)),fill="sliding"), alpha = 0.15) +
    geom_line(aes(y = abs(cum_true), color = "cumulative"))+  
    geom_line(aes(y = abs(tr_true), color = "sliding"))+
    facet_wrap(~level,scales="free_y",nrow=2)+
    theme_bw() + 
    geom_point(aes(x=timesig*20,y = abs(mean(tr_true) - 4 * sd(tr_true)),
                   shape="models differ"), inherit.aes = FALSE,size=0.5)+
    geom_point(aes(x=cum_sig*20,y = abs(mean(tr_true) - 3.5* sd(tr_true)),
                   color="cumulative"), size = 0.5, inherit.aes = FALSE)+
    geom_point(aes(x=tr_sig*20,y = abs(mean(tr_true) - 3* sd(tr_true)),
                   color="sliding"), size = 0.5, inherit.aes = FALSE)+
    scale_fill_brewer(type = "qual", palette = "Set2", name = "Model type") +
    scale_color_brewer(type = "qual", palette = "Set2", name = "Model type")+
    scale_shape_manual(values=c(15,15,15),name="")+
    ylab("Distance")+
    xlab("Time")+
    theme_bw() +
    theme(
          panel.grid = element_blank(),
          strip.background = element_blank(),
          panel.border = element_rect(size = 1))+
    scale_y_continuous(labels=scaleFUN)
  
  
  cumvstr_vis
saveRDS(object = cumvstr_vis, file = glue("figures/grand_average/cum_vs_tr_{l}.RDS"))

}

accumulation_data <- plateau_stat %>% 
  inner_join(tibble(level = c("V1", "V2", "V4", "IT", "word2vec"),
                    start = c(11.5, 11.5, 12.5, 12.5, 13.5))) # values from cross temporal plot

accumulation_plot <- accumulation_data %>% 
  mutate(level = factor(level, levels = rev(c("V1", "V2", "V4", "IT", "word2vec")))) %>% 
  rename(plateau_mean = emmean) %>% 
  ggplot(aes(y=level))+
  geom_point(aes(x = start*20, color="Start of generalization window"),size=3)+
  geom_pointrange(aes(
    x=plateau_mean*20,
    xmin = asymp.LCL * 20,
    xmax = asymp.UCL * 20,
    color="Plateau point")) +
  xlab("Time (ms)")+
  ylab("Feature model")+
  scale_color_brewer(type = "qual", palette = "Set1", direction = -1, name=NULL)+
  theme_bw() +
  theme(panel.grid = element_blank())

saveRDS(object = accumulation_plot, file = glue("figures/grand_average/accumplot.RDS"))

