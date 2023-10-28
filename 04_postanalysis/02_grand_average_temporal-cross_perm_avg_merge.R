# Merge all permutation files into one file
library(tidyverse)
library(glue)

path <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/permutations/temporal-cross/{level}/"
path_save <- "bids/derivatives/meg-derivatives/grand_ave/brain-space/visual_model/permutations/temporal-cross/{level}_tc_perm_avg_merged.csv"

for (level in c("V1")){
print(level)
perm_data = list()
files <- list.files(glue(path),pattern = "*.csv")
count <- 0
print(files)
start <- read_csv(paste0(glue(path), files[[1]]), col_types = cols())%>%
	group_by(time1,time2)%>%
        summarise(mean_distance = mean(distance), median_distance = median(distance))%>%
        mutate(perm = files[[1]])



write_csv(start, glue(path_save), append = FALSE)

for (filenum in 2:length(files)) {

	read_csv(paste0(glue(path), files[[filenum]]), col_types = cols()) %>%
        group_by(time1, time2) %>%
        summarise(mean_distance = mean(distance), median_distance = median(distance)) %>%
	mutate(perm = files[[filenum]]) %>%
	write_csv(glue(path_save), append = TRUE)

}
}
