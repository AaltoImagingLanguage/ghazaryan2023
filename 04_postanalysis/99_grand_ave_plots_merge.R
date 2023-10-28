# Merge grand average plots for figure

library(patchwork)
library(ggplot2)
library(glue)
library(tidyverse)

path <- "figures/grand_average/"
options(bitmapType="cairo")

all_figs <- list.files(path)

tc_o <- c()
tc_p <- c()
cum_vs_tr <- c()
count <- 0
for (l in c("V1","V2","V4","IT","word2vec")){
  count <- count+1
  o <- readRDS(glue("{path}temporal_cross_heatmap_{l}_o.RDS"))
  p <- readRDS(glue("{path}temporal_cross_heatmap_{l}_p.RDS"))
  vs <- readRDS(glue("{path}cum_vs_tr_{l}.RDS"))
  tc_o[[count]]<- o + 
    scale_x_continuous(breaks = c(0, 350, 650, 1000)) +
    theme(text = element_text(family = "sans", size = 8, colour = "black"),
                            strip.text = element_text(size = 8, color = "black"),
                            legend.text = element_text(size = 8, color = "black"),
                            axis.text = element_text(family = "sans", size = 8, colour = "black"),
                            legend.key.width = unit(8, "pt"),
                            legend.key.height = unit(8, "pt"),
                            legend.box.spacing = unit(2, "pt"),
                            plot.margin = margin(0, 0, 0, 0, "pt"))
  tc_p[[count]]<- p +
    scale_x_continuous(breaks = c(0, 350, 650, 1000)) +
    theme(text = element_text(size = unit(8, "pt"), colour = "black"),
                            strip.text = element_text(size = 8, color = "black"),
                            legend.text = element_text(size = 8, color = "black"),
                            axis.text = element_text(family = "sans", size = 8, colour = "black"),
                            legend.key.width = unit(8, "pt"),
                            legend.key.height = unit(8, "pt"),
                            legend.box.spacing = unit(2, "pt"),
                            plot.margin = margin(0, 0, 0, 0, "pt"))
  cum_vs_tr[[count]] <- vs +
    scale_x_continuous(breaks = c(0, 350, 650, 1000)) +
    theme(text = element_text(size = 8,  colour = "black"),
                                   strip.text = element_text(size = 8, color = "black"),
                                   legend.text = element_text(size = 8, color = "black"),
                                   axis.text = element_text(family = "sans", size = 8, colour = "black"),
                                   legend.key.width = unit(10, "pt"),
                                   legend.key.height = unit(10, "pt"),
                                   legend.spacing.y = unit(5, "pt"),
                                   legend.margin = margin(b = 1),
                                   legend.box.spacing = unit(2, "pt"),
                                   plot.margin = margin(0, 0, 0, 0, "pt")) +
    guides(colour = guide_legend(order = 2, reverse = TRUE), fill = guide_legend(order = 2, reverse = TRUE), shape = guide_legend(order = 1))
}

cum_vs_tr[[1]] <- cum_vs_tr[[1]] + scale_y_continuous(breaks = c(140, 160, 180))
cum_vs_tr[[2]] <- cum_vs_tr[[2]] + scale_y_continuous(breaks = c(60, 70, 80), labels = c(" 60", " 70", " 80"))
cum_vs_tr[[3]] <- cum_vs_tr[[3]] + scale_y_continuous(breaks = c(50, 60, 70), labels = c(" 50", " 60", " 70"))
cum_vs_tr[[4]] <- cum_vs_tr[[4]] + scale_y_continuous(breaks = c(45, 50, 55, 60), labels = c(" 45", " 50", " 55", " 60"))



visual <- (tc_o[[1]] + tc_p[[1]] + cum_vs_tr[[1]])/
(tc_o[[2]] + tc_p[[2]] + cum_vs_tr[[2]])/
(tc_o[[3]] + tc_p[[3]] + cum_vs_tr[[3]])/
(tc_o[[4]] + tc_p[[4]] + cum_vs_tr[[4]])/
(tc_o[[5]] + tc_p[[5]] + cum_vs_tr[[5]])

visualplt <- visual +
  plot_layout(tag_level = "new")+
  plot_annotation(tag_levels = c(tag_levels = list(c('A','B','C',
                                                     ' ','   ','   ',
                                                     ' ','   ','   ',
                                                     ' ','   ','   ',
                                                     ' ','   ','   '))))
                                                     
ggsave("figures/combine_grand_distance.pdf",
       visualplt,
       height=192,width=176, units = "mm")


accum_plot <- readRDS(glue("{path}accumplot.RDS"))

accumplt <- accum_plot +
  scale_x_continuous(limits = c(200, 500), breaks = c(200, 300, 400, 500)) +
  theme(text = element_text(size = 8,  colour = "black"),
        strip.text = element_text(size = 8, color = "black"),
        legend.text = element_text(size = 8, color = "black"),
        axis.text = element_text(family = "sans", size = 8, colour = "black"),
        legend.key.width = unit(10, "pt"),
        legend.key.height = unit(10, "pt"),
        legend.spacing.y = unit(5, "pt"))


ggsave("figures/grand_accum.pdf",
       accumplt,
       height=50,width=150, units = "mm")
