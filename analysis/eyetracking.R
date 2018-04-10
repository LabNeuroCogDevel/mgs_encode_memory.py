#!/usr/bin/env Rscript
require(dplyr)
require(tidyr)
require(ggplot2)
require(cowplot)
#library(eyetrackingR)
#library(gazetools) # https://github.com/RyanHope/gazetools
#library(saccades) # https://github.com/tmalsburg/saccades

# read avotec text output using perl pipe to add event
# add ld8 and runno as parsed from filename
# add trial by changes event change to iti (iti included as first part of trial)
read_avotec <- function (filename, trial_start_event="iti") {
   perlcmd <- 'BEGIN{$event="NA\\tNA"} $event="$F[2]\\t$F[1]" if/^12/;
               print join("\\t",@F[1..12],$event) if m/^10/'

   pcmd <- sprintf("perl -slane '%s' %s", perlcmd, filename)

   ld8   <- stringr::str_extract(filename, "\\d{5}_\\d{8}")
   runno <- stringr::str_extract(filename, "(?<=run)\\d+")

   eyed <- tryCatch( read.table(text=system(pcmd, intern = TRUE)) %>%
                    `names<-`(c("totaltime", "deltatime",
                     "x_gaze", "y_gaze", "x_correctedgaze", "y_correctedgaze",
                     "region", "pupilwidth", "pupilheight", "quality",
                     "fixation", "count", "event", "event_onset")),
                    error=function(e) {
                       warning("parse: ", filename, ": ", e)
                       return(NULL)
                    })
   if (is.null(eyed)) return(NULL)

   edf <-
      eyed %>%
      separate(event, c("event", "side", "imgtype"),
               fill="right", extra="merge") %>%
      filter(!is.na(side)) %>%
      mutate(ld8=ld8, runno=as.numeric(runno),
             trial = lag(event) != event & event == trial_start_event,
             trial = cumsum(ifelse(is.na(trial), T, trial)))
}

plot_eyedf <- function(edf) {
   edf %>%
    filter(event %in% c("img", "mgs")) %>%
    ggplot +
    aes(x=x_correctedgaze, y=y_correctedgaze, color=event) +
    geom_path(arrow=arrow(ends="first", type="closed")) +
    facet_wrap(~trial) +
    scale_x_continuous(limits=c(-1.5, 1.5)) +
    scale_y_continuous(limits=c(-1.5, 1.5)) +
    theme_bw()
}


trial_xpos_plot <- function(fsum, x,normalize=T) {
   # subtract center from xposition
   if(normalize) x <- paste0(x, " - x_isi_wmode")
   ggplot(fsum) +
   aes_string(size="ldur", color="event", shape="side",
       x=x, y="trial") +
   geom_point() + theme_bw()
   #facet_wrap(~trial)
}

weight_hist_mid <- function(x, dur) {
   h <- weights::wtd.hist(x, weight=dur, plot=F)
   h$mids[which.max(h$counts)]
}

fixation_summary <- function (rundf, fixation_event="isi",
                              keep_events=c("img", "mgs", "isi")) {
  d <- rundf %>%
       mutate(tt=paste(trial, event, side)) %>%
       select(time=totaltime, x=x_gaze, y=y_gaze, trial=tt)
  f <- detect.fixations(d, smooth.coordinates=T, smooth.saccades=T) %>%
     separate(trial, c("trial", "event", "side")) %>%
     mutate(trial=as.numeric(trial)) %>%
     # add onsets
     merge(rundf %>%
           group_by(trial, event) %>%
           summarise(event_onset=first(event_onset)),
          by=c("trial", "event")) %>%
     mutate(start_rel=start-event_onset)

  # remove unwanted events if we have keep events
  if (length(keep_events)>0L) {
     f <- f %>% filter(event %in% keep_events )
  }

  fsum <- f %>%
     mutate(trial=as.numeric(trial)) %>%
     group_by(trial, event, side) %>%
     mutate(dur_w=dur/sum(dur)) %>%
     summarize( lidx=which.max(dur), ldur=max(dur),
               x_long=x[lidx], y_long=y[lidx],
               x_weight= sum(x*dur_w), y_weight=sum(y*dur_w),
               x_mean=mean(x), y_mean=mean(y))

  # skip merging if no fixation_event to use as normalizer
  if (length(fixation_event)==0L) return(fsum)

  # grab the place they were looking the most during isi
  # as the center fix
  # ggplot(f %>% filter(event=='isi')) + aes(x=x,weight=dur) + geom_histogram() + facet_wrap(~trial)

  isi_xpos <- f %>%
     group_by(trial, event) %>%
     summarise(x_isi_wmode = weight_hist_mid(x, dur)) %>%
     filter(event=="isi") %>% select(-event)

  # return summary and best idea of fixation position
  # add x_isi_wmode
  merge(fsum, isi_xpos, by="trial")
}

sort_eye_list <- function(run_list) {
   # make id like date_luna_run so we can better sort
   sortableid <- sapply(run_list, function(x) {
        vals <- list(
                   substr(x[1, "ld8"], 7, 7+8), # date
                   substr(x[1, "ld8"], 0, 0+5), # lunaid
                   x[1, "runno"],               # run
                   nrow(x))                     # length
        vals <- sapply(vals, function(v){
                   bad <- is.null(v) || length(v)==0 || is.na(v)
                   ifelse(bad, "99999999", sprintf("%08.0f", as.numeric(v)))
                   })
      as.numeric(paste0(collapse="", vals))
   } )
   this_order <- order(sortableid)
   return(run_list[this_order])
}

# view "best" fixation (xvar in x_{long,mean,weight)
# new plot for each run dfs in a list (run_list)
# x=xvar, y=trial no
view_runs <-function(run_list, xvar="x_long") {
   for (rundf in run_list[this_order]) {
      if (is.null(rundf)) next
      tinfo <- paste(collapse=" ", rundf[1, c("ld8", "runno")])
      fsum <- fixation_summary(rundf)
      p <- trial_xpos_plot(fsum, xvar) # x_long, x_mean, x_weight
      print(p + ggtitle(tinfo) )
     readline(prompt=sprintf("%s, next?", tinfo))
   }
}

# view each trials trace for img isi and mgs
# print plot for each trial of a given eye tracking dataframe (single run)
view_trial_traces <- function(eydf) {
   ntrial <- max(eydf$trial)
   d <- eydf %>%
       filter(event %in% c( "img", "isi", "mgs"))

   for (i in 1:ntrial) {
     td <- d %>% filter(trial==i)
     tinfo <- paste(td[1, "ld8"], td[1, "runno"], td[1, "side"], i)

     ## raw traces
     p <- ggplot(td) +
      aes(x=x_gaze, y=y_gaze, color=event) +
      geom_path() +
      ggtitle(sprintf("raw: %s", tinfo))

     pc <- ggplot(td) +
      aes(x=x_correctedgaze, y=y_correctedgaze, color=event) +
      geom_path() +
      ggtitle(sprintf("correct: %s", tinfo))
     print(plot_grid(p,pc))

     # prompt for enxt
     readline(prompt=sprintf("%d, next?", i)) }
}

