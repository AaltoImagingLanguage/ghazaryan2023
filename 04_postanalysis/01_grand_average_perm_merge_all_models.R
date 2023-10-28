# Merge all permutation files into one file
library(tidyverse)
library(glue)


 # load permutation data
path <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/permutations/"

path_save <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/permutations/all_perm_merged.csv"
path_save_RDS <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/permutations/all_perm_merged.RDS"

perm_data = list()
count <- 0

files <- list.files(path,pattern = "*merged.csv")
# read csvs corresponding to different analysis types
for (csv in files) {
  count <- count + 1
  level <- str_split(csv,"_")[[1]][1]
  current_csv <- read_csv(paste(path, csv, sep = ""), col_types = cols()) %>% 
    mutate(level = level)
  perm_data[[count]] <- current_csv
}

perm_data <- do.call(rbind, perm_data)
write_csv(perm_data,path_save)
saveRDS(perm_data,path_save_RDS)
