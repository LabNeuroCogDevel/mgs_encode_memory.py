library(dplyr)
readrun <-function(f, r) read.csv(f) %>%
   mutate(run=r, imgfile=as.character(imgfile))
see <- readrun("subj_info/startat2/01/test_mgsenc-A_20181011/startat2_20181011_test_1_view.csv", 1) %>%
   rbind(readrun("subj_info/startat2/01/test_mgsenc-A_20181011/startat2_20181011_test_2_view.csv", 2)) %>%
   mutate(pos = gsub("Left", "-1", side) %>% gsub("Right", "1", .) %>%
                gsub("Near", ".5 * ", .) %>%
                lapply(function(x) eval(parse(text=x))) %>% unlist)


recall <-
 readrun("subj_info/startat2/01/test_mgsenc-A_20181011/startat2_20181011_test_1_runs1-1_recall-A_20181011102515.csv", 1) %>%
 rbind(readrun("subj_info/startat2/01/test_mgsenc-A_20181011/startat2_20181011_test_1_runs2-2_recall-A_20181011102829.csv", 2)) %>%
 mutate(corkeys=gsub("[^0-9,]", "", corkeys)) %>%
   tidyr::separate(corkeys, c("know", "side"), sep=",")


## baseline sanity check
seeinrecall <- !is.na(recall$pos) # in recall, say have seen
# see in recall actually seen
all(recall$imgfile[seeinrecall] %in% see$imgfile)
# all positions match
all(paste(recall$imgfile[seeinrecall], recall$pos[seeinrecall]) %in%
    paste(see$imgfile, see$pos))

# never an recall claimed unseen in actuall see
!any(recall$imgfile[!seeinrecall] %in% see$imgfile)

# all in seen are in recall (ignore empyt image display in see)
all( see$imgfile[see$img != "None"] %in% recall$imgfile )

## no crossing between runs
# nothing in recall that is in the other run
all(! recall$imgfile[recall$run==2] %in% see$imgfile[see$run==1])
all(! recall$imgfile[recall$run==1] %in% see$imgfile[see$run==2])
# not in see and in other recall run
all(! see$imgfile[see$run==2 & see$img != "None"] %in% recall$imgfile[recall$run==1])
all(! see$imgfile[see$run==1 & see$img != "None"] %in% recall$imgfile[recall$run==2])
