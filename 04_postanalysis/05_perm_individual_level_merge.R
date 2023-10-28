# summarise tr and cumulative permutations and merge + tstat
# subject, level, perm

library(tidyverse)
library(glue)

args <- commandArgs(trailingOnly = TRUE)
subject <- args[[1]]
level <- args[[2]]
perm <- args[[3]]


subject <- str_pad(subject, 2, pad = "0")
subject = glue("sub-{subject}")
path <- glue("bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/perm/{level}")

perm_data <- c()
count <- 0
for (type in c("cum","tr-1")) {
  count = count + 1
  results <- read_csv(glue("{path}/{subject}_modality-picture-{type}-{level}-{perm}-results.csv")) %>% 
    mutate(type = type,
           level = level,
           perm = perm)
  perm_data[[count]] <- results
  
}

perm_data <- do.call(rbind, perm_data)

perm_data_mean <- perm_data %>% 
  mutate(similarity= -distance) %>%
  group_by(level,perm,time,type) %>% 
  summarise(mean_similarity=mean(similarity)) %>% 
  pivot_wider(names_from = type, values_from = mean_similarity) %>%
  rename("cum_perm" = cum,
         "tr_perm" = `tr-1`) 


perm_data_t <- perm_data %>% 
  pivot_wider(names_from = type, values_from = distance) %>%
  rename("cum_perm" = cum,
         "tr_perm" = `tr-1`) %>% 
  mutate(cum_perm_sim = -cum_perm,
         tr_perm_sim = -tr_perm) %>% 
  ungroup() %>% 
  group_by(time, level, perm) %>% 
  arrange(target) %>% 
  summarise(true_sim_diff = mean(cum_perm) - mean(tr_perm),
            ttest = t.test(cum_perm_sim, tr_perm_sim, paired = TRUE)$statistic)

merged_df <- left_join(perm_data_mean,perm_data_t,by = c("level","perm","time")) %>% 
  mutate(subject = subject)

to_save_dir <- glue("bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/perm/merged/{level}/")
if (!dir.exists(to_save_dir)) {
  dir.create(to_save_dir,recursive = TRUE)
}

write_csv(merged_df,glue("{to_save_dir}{subject}_modality-picture-{level}-{perm}-merged-results.csv"))

# delete original files (taking too much space)
for (type in c("cum","tr-1")) {
  for (end in c("csv","mat")) {
  file.remove(glue("{path}/{subject}_modality-picture-{type}-{level}-{perm}-results.{end}"))
}}
