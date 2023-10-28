# Merge individual level plots for figure

library(tidyverse)
library(lemon)

V1_plot <- readRDS("figures/V1_indiv_tr_cum.RDS") +
  scale_x_continuous(breaks = c(0, 350, 650, 1000)) +
  theme(text = element_text(size = 8,  colour = "black"),
        strip.text = element_text(size = 8, color = "black"),
        legend.text = element_text(size = 8, color = "black"),
        axis.text = element_text(family = "sans", size = 8, colour = "black"),
        legend.key.width = unit(10, "pt"),
        legend.key.height = unit(10, "pt"),
        legend.spacing.y = unit(5, "pt"))

ggsave("figures/V1_indiv_tr_cum.pdf",
V1_plot, height = 192, width = 176, units = "mm")


V2_plot <- readRDS("figures/V2_indiv_tr_cum.RDS") +
  scale_x_continuous(breaks = c(0, 350, 650, 1000)) +
  theme(text = element_text(size = 8,  colour = "black"),
        strip.text = element_text(size = 8, color = "black"),
        legend.text = element_text(size = 8, color = "black"),
        axis.text = element_text(family = "sans", size = 8, colour = "black"),
        legend.key.width = unit(10, "pt"),
        legend.key.height = unit(10, "pt"),
        legend.spacing.y = unit(5, "pt"))

ggsave("figures/V2_indiv_tr_cum.pdf",
       V2_plot, height = 192, width = 176, units = "mm")

V4_plot <- readRDS("figures/V4_indiv_tr_cum.RDS") +
  scale_x_continuous(breaks = c(0, 350, 650, 1000)) +
  theme(text = element_text(size = 8,  colour = "black"),
        strip.text = element_text(size = 8, color = "black"),
        legend.text = element_text(size = 8, color = "black"),
        axis.text = element_text(family = "sans", size = 8, colour = "black"),
        legend.key.width = unit(10, "pt"),
        legend.key.height = unit(10, "pt"),
        legend.spacing.y = unit(5, "pt"))

ggsave("figures/V4_indiv_tr_cum.pdf",
       V4_plot, height = 192, width = 176, units = "mm")

IT_plot <- readRDS("figures/IT_indiv_tr_cum.RDS") +
  scale_x_continuous(breaks = c(0, 350, 650, 1000)) +
  theme(text = element_text(size = 8,  colour = "black"),
        strip.text = element_text(size = 8, color = "black"),
        legend.text = element_text(size = 8, color = "black"),
        axis.text = element_text(family = "sans", size = 8, colour = "black"),
        legend.key.width = unit(10, "pt"),
        legend.key.height = unit(10, "pt"),
        legend.spacing.y = unit(5, "pt"))

ggsave("figures/IT_indiv_tr_cum.pdf",
       IT_plot, height = 192, width = 176, units = "mm")

w2v_plot <- readRDS("figures/word2vec_indiv_tr_cum.RDS") +
  scale_x_continuous(breaks = c(0, 350, 650, 1000)) +
  theme(text = element_text(size = 8,  colour = "black"),
        strip.text = element_text(size = 8, color = "black"),
        legend.text = element_text(size = 8, color = "black"),
        axis.text = element_text(family = "sans", size = 8, colour = "black"),
        axis.title = element_text(family = "sans", size = 8, colour = "black"),
        legend.key.width = unit(10, "pt"),
        legend.key.height = unit(10, "pt"),
        legend.spacing.y = unit(5, "pt"))

ggsave("figures/word2vec_indiv_tr_cum.pdf",
       w2v_plot, height = 192, width = 176, units = "mm")


corr_indiv <- readRDS("figures/corr_indiv.RDS") +
  theme(text = element_text(size = 8,  colour = "black"),
        strip.text = element_text(size = 8, color = "black"),
        legend.text = element_text(size = 8, color = "black"),
        axis.text = element_text(family = "sans", size = 8, colour = "black"),
        axis.title = element_text(family = "sans", size = 8, colour = "black"),
        legend.key.width = unit(10, "pt"),
        legend.key.height = unit(10, "pt"),
        legend.spacing.y = unit(5, "pt"))

subject_em <- readRDS("figures/subject_em.RDS") +
  theme(text = element_text(size = 8,  colour = "black"),
        strip.text = element_text(size = 8, color = "black"),
        legend.text = element_text(size = 8, color = "black"),
        axis.text = element_text(family = "sans", size = 8, colour = "black"),
        axis.title = element_text(family = "sans", size = 8, colour = "black"),
        legend.key.width = unit(10, "pt"),
        legend.key.height = unit(10, "pt"),
        legend.spacing.y = unit(5, "pt"))

em_corplot <- readRDS("figures/em_corplot.RDS") +
  theme(text = element_text(size = 8,  colour = "black"),
        strip.text = element_text(size = 8, color = "black"),
        legend.text = element_text(size = 8, color = "black"),
        axis.text = element_text(family = "sans", size = 8, colour = "black"),
        axis.title = element_text(family = "sans", size = 8, colour = "black"),
        legend.key.width = unit(10, "pt"),
        legend.key.height = unit(10, "pt"),
        legend.spacing.y = unit(5, "pt"))

std_plot <- readRDS("figures/std_plot.RDS") +
  scale_x_continuous(breaks = c(0, 350, 650, 1000)) +
  theme(text = element_text(size = 8,  colour = "black"),
        strip.text = element_text(size = 8, color = "black"),
        legend.text = element_text(size = 8, color = "black"),
        axis.text = element_text(family = "sans", size = 8, colour = "black"),
        axis.title = element_text(family = "sans", size = 8, colour = "black"),
        legend.key.width = unit(10, "pt"),
        legend.key.height = unit(10, "pt"),
        legend.spacing.y = unit(5, "pt"))


layout<- "AAAAAA
          AAAAAA
          AAAAAA
          AAAAAA
          AAAAAA
          AAAAAA
          AAAAAA
          BBCCCC
          BBCCCC
          BBCCCC
          BBCCCC"

indiv_combined <- (subject_em +
                     theme(text = element_text(size = 8)) +
                     scale_x_continuous(breaks = c(250, 400, 550))
                   ) + 
  (em_corplot+ theme(legend.position = "none")) +
  (std_plot + facet_rep_wrap(~level, scales = "free_y") +
     theme(legend.position = "none", text = element_text(size = 8))) + 
  plot_layout(design = layout)+plot_annotation(tag_levels = 'A')

ggsave("figures/indiv_combined.pdf", indiv_combined, width = 176, height = 180, units = "mm") 


ggsave("figures/plateau_corr_indiv.pdf", corr_indiv, width = 176, height = 176, units = "mm") 
