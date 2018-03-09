#!/usr/bin/env Rscript
library(dplyr)
library(tidyr)
library(ggplot2)

filename <- "/Volumes/L/bea_res/Data/Tasks/MGSEncMem/7T/10195_20180129/eye/10195_20180129_run3_124337.txt"

perlcmd <- 'BEGIN{$event="NA\\tNA"} $event="$F[2]\\t$F[1]" if/^12/; print join("\\t",@F[1..12],$event) if m/^10/'

pcmd <- sprintf("perl -slane '%s' %s", perlcmd, filename)
eyed <- read.table(text=system(pcmd, intern = TRUE))
names(eyed) <- c("TotalTime", "DeltaTime",
                  "X_Gaze", "Y_Gaze", "X_CorrectedGaze", "Y_CorrectedGaze",
                  "Region", "PupilWidth", "PupilHeight", "Quality",
                  "Fixation", "Count", "event", "event_onset")

edf <-
   eyed %>%
   separate(event, c("event", "side", "imgtype")) %>%
   mutate( trial = lag(event) != event & event == "iti",
          trial = cumsum(ifelse(is.na(trial), T, trial)))

p <- edf %>%
  filter(event %in% c("img", "mgs")) %>%
  ggplot +
  aes(x=X_CorrectedGaze, y=Y_CorrectedGaze, color=event) +
  geom_path(arrow=arrow(ends="first", type="closed")) +
  facet_wrap(~trial) +
  scale_x_continuous(limits=c(0, 1.5)) +
  scale_y_continuous(limits=c(0, 1.5)) +
  theme_bw()

ggsave(p, "../etc/eyetracking.pdf")
