#!/usr/bin/env Rscript

eye_files <- Sys.glob("/Volumes/L/bea_res/Data/Tasks/MGSEncMem/7T/*/eye/*txt")
eye_dfs <- lapply(eye_files, read_avotec )

view_runs(sort_eye_list(eye_dfs), "x_weight")

#eye_dfs[[25]]  %>% filter(!is.na(event) ) %>% group_by(ld8,runno,event,trial) %>% summarise_at(vars(x_correctedgaze,y_correctedgaze),funs(mean,sd)) %>% ggplot() + aes(x_correctedgaze_mean,y_correctedgaze_mean, color=event) + geom_point() + theme_bw() + facet_wrap(~trial)

# ggsave(p, "../etc/eyetracking.pdf")
