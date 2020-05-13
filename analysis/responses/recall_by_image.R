#!/usr/bin/env Rscript
library(dplyr)
library(magrittr)
library(ggplot2)

# 20200511WF - init
#  recall by image (OR)

f <- Sys.glob("/Volumes/L/bea_res/Data/Tasks/MGSEncMem/7T/1*_2*/*/*/*recall*.csv")
#### redo with key pushes. also merge task to check

# all tasks

bname <- function(x) as.character(x) %>% gsub("\\\\+", "/", .) %>% basename()

read_task_recall <- function(recall_f) {
    g <- file.path(dirname(recall_f), "*_view.csv")
    recall <- read.csv(recall_f) %>%
      mutate(imgfile = bname(imgfile))
    task <- Sys.glob(g) %>% lapply(read.csv) %>% bind_rows %>% mutate(imgfile=bname(imgfile))
    b <- merge(recall, task, all.x=T, by="imgfile")

    b$ld8 <- stringr::str_extract(recall_f,"\\d{5}_\\d{8}")
    b %>%
        mutate(corkeys = gsub("[^0-9,]", "", corkeys)) %>%
        tidyr::separate(corkeys,c("know_cor","dir_cor")) %>%
        select(ld8, dly, mgs, know_cor, know_key, dir_cor, dir_key, score, pos, side, imgfile)
    
}

# "/Volumes/L/bea_res/Data/Tasks/MGSEncMem/7T/10129_20180917/01_mri_B/10129_20180917_mri_1_recall-B_20180917184856.csv"
all_tskrcl <- lapply(f,read_task_recall) %>% bind_rows

# -1   very wrong
# -0.5 maybe, but wrong
#  0.5 maybe, correct
#  1   correct
all_tskrcl <- all_tskrcl %>%
  mutate(
      seen = ifelse(is.na(pos),'novel','familiar'), 
      cor = 2*(ifelse(know_key %in% c(1,2), 1, 0) == know_cor) - 1,
      resp = cor - sign(cor)*ifelse(know_key %in% c(2, 9), .5, 0),
      corstr = factor(resp, labels=c("wrong","wrong, maybe", "correct, maybe", "correct")), 
      # -1 = incorrect => novel      =>1 seen  
      # -1 - incorrect => familiar => -1: novel
      respstr = ifelse(is.na(pos),-1*resp, resp) %>% factor(labels=c("novel","novelmaybe", "familiarmaybe", "familiar"))) 

# general distribution
all_tskrcl %>% 
 ggplot() + aes(x=respstr,fill=seen) +
 geom_histogram(stat='count',position='dodge') +
    cowplot::theme_cowplot()

all_tskrcl %>%
    group_by(ld8, seen) %>%
    tally() %>% group_by(n, seen) %>% tally() %>%
    tidyr::spread(seen, nn)
# 125 (of 129) saw 48 seen and and 48 unseen images

cnts <-
    all_tskrcl %>%
    group_by(imgfile, respstr, seen) %>%
    tally(name="picked") %>% ungroup() 
    #group_by(imgfile) %>%
    #dplyr::mutate(total=sum(picked), )

cnts %>%
 tidyr::spread(respstr,picked)  %>%
 write.csv("image_seenXpicked.csv", row.names=F, quote=F)
    

# how often is an image correctly identified
# faceted by if correct is seen or unseen
p <- ggplot(cnts) +
    aes(fill=respstr, x=picked) +
    geom_density(alpha=.75) +
    scale_fill_manual(values=c('red','orange','blue','green')) +
    facet_grid(seen~.) + cowplot::theme_cowplot() +
    ggtitle('image response counts: seen by picked')
ggsave('seenXpicked_perimgcnts.svg', p)


## using score
# d <- lapply(f, read.csv) %>%
#     bind_rows %>% 
#     # normalize path
#     mutate(imgfile = gsub("\\\\+", "/", imgfile) %>% gsub('img/','',.))
# 
# # score from ../../mgs_recall.py
# # +5  = correct side    (105, 205)  +15 = exactly correct (115,215)
# #
# # v did\said>:  see         not       maybe
# # see           200,205,215 0         100,105,115
# # not           1           201       101
# 
# s <- d %>%
#    select(imgfile, pos, score) %>%
#    mutate(imgfile = gsub("\\\\+", "/", imgfile),
#           saw       = !is.na(pos),
#           #saw2      = score %in% c(0, 100, 105, 115, 200, 205, 215),
#           said_no   = score ==   0 | score == 201,
#           said_maybe= score >= 100 & score <  200,
#           said_yes  = score >= 200 | score ==   1) %>%
#    select(-pos, -score) %>%
#    group_by(imgfile, saw) %>%
#    summarize_all(sum) %>%
#    arrange(-said_yes)
# by_score <-
#    d %>%
#    group_by(imgfile, score) %>%
#    tally %>%
#    tidyr::spread(score, n)
# 
# # write.csv(s, "image_by_seen.csv", row.names=F, quote=F)
# # write.csv(by_score, "image_by_score.csv", row.names=F, quote=F)
# 
# # # plot to see how crazy it is
# # s %>% tidyr::gather(said, n, -imgfile, -saw) %>%
# #    ggplot() + aes(y=n, fill=said) + geom_density() +
# #    facet_wrap(~saw) + coord_flip() + cowplot::theme_cowplot() +
# #    scale_fill_manual(values=c("lightblue", "pink", "lightgreen"))
