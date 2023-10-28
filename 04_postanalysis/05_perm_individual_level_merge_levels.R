# Merge permutations

library(tidyverse)
library(glue)
library(stringr)

path <- "bids/derivatives/meg-derivatives/{subject}/brain-space/visual_model/perm/merged/{level}/"

# merge permutations per subject

for (subject in c(1:19)) {
  print(subject)
  all_perm <- c()
  subject <- str_pad(subject, 2, pad = "0")
  subject = glue("sub-{subject}")
  count_level <- 0
for (level in c("V1","V2","V4","IT","decoder","word2vec")) {
  print(paste(subject,level))
  count_level <- count_level + 1
  count <- 0
  current_level_perm <- c()
  current <- list.files(glue(path), ".csv")
  for (file in current) {
    count <- count + 1
    current_level_perm[[count]] <- read_csv(paste0(glue(path),file),col_types = cols()) %>% 
      mutate(perm_new = count)
  }
  count_level <- count_level + 1
  current_level_perm <- do.call(rbind, current_level_perm)
  all_perm[[count_level]] <- current_level_perm
}
  all_perm <- do.call(rbind, all_perm)
  write_csv(all_perm,
            glue("bids/derivatives/meg-derivatives/{subject}/brain-space/visual_model/perm/merged/{subject}_perm_merged.csv"))
}
