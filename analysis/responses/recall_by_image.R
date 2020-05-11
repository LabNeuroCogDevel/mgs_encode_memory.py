#!/usr/bin/env Rscript
library(dplyr)
library(magrittr)

# 20200511WF - init
#  recall by image (OR)

f1 <- Sys.glob("/Volumes/L/bea_res/Data/Tasks/MGSEncMem/7T/1*_2*/*/*recall*.csv")
f2 <- Sys.glob("/Volumes/L/bea_res/Data/Tasks/MGSEncMem/7T/1*_2*/*/*/*recall*.csv")
d <- lapply(c(f1, f2), read.csv) %>% bind_rows
unique(d$score)

# normalize path
d %<>% mutate(imgfile = gsub("\\\\+", "/", imgfile) %>% gsub('img/','',.))

# score from ../../mgs_recall.py
# +5  = correct side    (105, 205)  +15 = exactly correct (115,215)
#
# v did\said>:  see         not       maybe
# see           200,205,215 0         100,105,115
# not           1           201       101

s <- d %>%
   select(imgfile, pos, score) %>%
   mutate(imgfile = gsub("\\\\+", "/", imgfile),
          saw       = !is.na(pos),
          said_no   = score ==   0 | score == 201,
          said_maybe= score >= 100 & score <  200,
          said_yes  = score >= 200 | score ==   1) %>%
   select(-pos, -score) %>%
   group_by(imgfile, saw) %>%
   summarize_all(sum) %>%
   arrange(-said_yes)

write.csv(s, "image_by_seen.csv", row.names=F, quote=F)

by_score <-
   d %>%
   group_by(imgfile, score) %>%
   tally %>%
   tidyr::spread(score, n)

write.csv(by_score, "image_by_score.csv", row.names=F, quote=F)
