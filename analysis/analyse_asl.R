#!/usr/bin/env Rscript
# 20220322 WF - quick look at asl mgsencmem data

source('eyetracking.R')
fnames <- list("/Volumes/L/bea_res/Data/Temporary Raw Data/7T/11738_20181213/11738_20181213_mgs1.eyd")
all_runs <- lapply(fnames,read_asl)
rundf<-all_runs[[1]]
plot_eyedf(rundf)
fsum <- fixation_summary(rundf)
p <- trial_xpos_plot(fsum, "x_mean") # x_long, x_mean, x_weight
