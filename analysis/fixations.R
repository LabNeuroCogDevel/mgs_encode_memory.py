library(dplyr)
path<-sprintf("%s%s", getwd(), "/mgs_encode_memory.py/analysis")
source(sprintf("%s%s",path,"/eyetracking.R"))
files <- list.files(path=sprintf("%s%s",path,"/runs"), pattern="*.txt", full.names=TRUE, recursive=FALSE)

GetSpread <- function(fname) {
  
  # source(eyetracking.R)
  data <- read_avotec(fname)
  
  ## SCORE ##
  
  # Average of last 90 data points for each id->side->event->trial
  data.mt90 <- data %>%
    group_by(trial, event, side, ld8) %>%
    summarise(mt90=mean(tail(x_gaze,90))) %>%
    ungroup() %>%
    mutate(side=ifelse(event=="iti",lag(side),side)) %>%
    spread(event, mt90)
  
  # Near/Right = 1; Near/Left = -1
  data.mt90$side_num <- grepl("Right",data.mt90$side) %>%
    ifelse(1,-1)
  
  # Run and filename processing
  file_base <- basename(fname)
  reg_start <- regexpr("run.", file_base, TRUE)
  reg_end <- attr(reg_start, "match.length")-1
  run_num <- substr(file_base, reg_start, reg_start+reg_end)
  
  # Trial order:
  #  iti -> cue -> img -> isi -> mgs
  # Scoring:
  #  0 (best) --> 2 (worst)
  #  0 = side_num == ic == mi
  #  1 = side_num == ic != mi
  #  2 = side_num != ic (=/!= mi)
  
  data.sides <- data.mt90 %>%
    mutate(ic=(img-cue)/abs(img-cue), mi=(mgs-isi)/abs(mgs-isi), score=ifelse(side_num==ic,ifelse(ic==mi,0,1),2)) %>%
    mutate(file=file_base, run=run_num)
  
  return(data.sides)
}

# Apply scoring to files[1:last_file] times
doAll <- function() {
  last_file <- 24
  scored.out <- lapply(files[1:last_file], function(fname) tryCatch(GetSpread(fname), error=function(x) NULL)) %>% bind_rows()
}

# Retrieve large row-bound dataframe
scored.out <- suppressWarnings(doAll())

# Box plot
#  x = ld8
#  y = score
#  Jitter points shown (colored by run)
gg_box <- scored.out %>%
  ggplot()+aes(x=ld8,y=score)+geom_boxplot()+geom_jitter(aes(color=as.factor(run)))


