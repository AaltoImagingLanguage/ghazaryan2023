# Merge all permutation files into one file
library(tidyverse)
library(glue)

path <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/permutations/{level}/"
path_save <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model//permutations/{level}_perm_merged.csv"

for (level in c("V1","V2","V4","IT","decoder","word2vec")){
print(level)
perm_data = list()
files <- list.files(glue(path),pattern = "*.csv")
count <- 0
for(csv in files){
  print(count)
  count <- count + 1
  if (str_detect(csv,"tr")){
    type <- "tr"
  } else{
    type <- "cum"
  }
  current_csv <- read_csv(paste(glue(path),csv,sep = ""),col_types = cols()) %>% 
    mutate(type=type,
           perm=csv)
  perm_data[[count]] <- current_csv
}

perm_data <- do.call(rbind, perm_data)
write_csv(perm_data,glue(path_save))

}

