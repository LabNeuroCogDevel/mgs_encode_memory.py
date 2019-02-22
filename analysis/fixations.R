library(dplyr)
path<-sprintf("%s%s", getwd(), "/mgs_encode_memory.py/analysis")
source(sprintf("%s%s",path,"/eyetracking.R"))
files <- list.files(path=sprintf("%s%s",path,"/runs"), pattern="*.txt", full.names=TRUE, recursive=FALSE)

#results <- data.frame(filename = NA)

GetSpread <- function(fname) {
  
  data <- read_avotec(fname)
  
  ## SCORE ##
  
  data.mt90 <- data %>%
    group_by(trial, event, side,ld8) %>%
    summarise(mt90=mean(tail(x_gaze,90))) %>%
    ungroup() %>%
    mutate(side=ifelse(event=="iti",lag(side),side)) %>%
    spread(event, mt90)
  
  data.mt90$side_num <- grepl("Right",data.mt90$side) %>%
    ifelse(1,-1)
  
  # iti -> cue -> img -> isi -> mgs
  # score:
  #  0 (best) --> 6 (worst)
  #  2 = img-cue, 4 = mgs-isi
  #  (-)score = (+)side
  
  data.sides <- data.mt90 %>%
    mutate(ic=(img-cue)/abs(img-cue), mi=(mgs-isi)/abs(mgs-isi), score=(ic-side_num + (mi-side_num)*2)) %>%
    mutate(basename(fname))
  
#  results$filename <- fname
  
  ## QUALITY ##
  
  # data.trial <- data %>%
  #   group_by(event,trial,side) %>%
  #   summarise(trial.mean=mean(tail(x_gaze,90)),trial.sd=sd(tail(x_gaze,90)))
  # 
  # data.global <- data %>%
  #   group_by(event,side) %>%
  #   summarise(event.mean=mean(tail(x_gaze,90)),event.sd=sd(tail(x_gaze,90))) %>% 
  #   ungroup()
  # 
  # data.all <- merge(data.trial, data.global, by = c("side","event")) %>% arrange(trial, side)
  # 
  # norm.factor <- diff(quantile(data$x_gaze, c(0.05, 0.95)))
  # 
  # data.norm <- data.all %>% mutate(mean.diff = data.all$event.mean - data.all$trial.mean, norm = mean.diff/norm.factor)
    
  #data.norm %>% ggplot()+aes(x=side, y=norm, color=event)+geom_point()
}

doAll <- function() {
  scored.out <- lapply(files[1:2],function(fname) tryCatch(GetSpread(fname), error=function(x) NULL)) %>%
  bind_rows()
}

# for(i in 1:length(files)) {
#   fname <- files[i]
#   Check <- function(fname) {
#     tryCatch(GetSpread(fname), error=function(x) NULL) 
#   }
# }

#data.m90t %>%  ggplot()+aes(x=trial, y=m90t, color=event)+geom_point()
#data.mt90 %>% ggplot()+aes(x=trial, y=mt90, color=event)+geom_point()+geom_smooth(data=data.mt90%>%filter(event %in% c("iti","isi","cue")))

#add subject, use bindrows, plot everyone



# data.spread <- data.group %>%
#   spread(event,pos) %>%
#   mutate(diff = mgs - img)
# }
# 
# data.spread %>%
#   group_by(side) %>%
#   summarise_all(funs(mean,sd))
# 
# data %>% 
#   mutate(time = seq(1, lengths(data)[1])) %>%
#   filter(event %in% c("img","mgs","iti") & trial == 1) %>%
#   ggplot()+aes(x=time, y=x_gaze, color=event)+geom_point()
# 
# data.sd.mean <- data %>%
#   filter(event %in% c("img", "mgs", "iti")) %>%
#   group_by(event,side) %>%
#   summarise(x.sd=sd(x_gaze), x.mean=mean(x_gaze))
# 
# #drop event from data.clean
# data.s.m <- data.sd.mean %>% ungroup() %>%
#   filter(event != "mgs") %>%
#   select(-event)
# 
# #merge data.clean with data
# data.new <- merge(data, data.s.m, by = "side")
# View(data.new)
# data.new <- data.new[c(2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,1, 20,21)]
# 
# View(data.new)
# 
# View(data.group)

#getXFix <- function(fname) {
# FOR EACH FILE IN DIRECTORY
#for(i in 1:length(files)) {
  # CONVERT ".txt" INTO PARSEABLE DATA FRAME
#data <- read_avotec(fname)

#  if(!is.null(data))
#  {
#    cat("Reading file:", files[i], "\n")
    
    # TAKE DIFFERENCE BETWEEN X VALUES, GET THE RUN LENGTH ENCODING OF EACH RUN WHERE
    # THE DISTANCE IS GREATER THAN "max.dist", GET THE INDICES OF RLE WHERE LENGTH GREATER
    # THAN "num.runs" AND THE RLE CONTAINS FALSE VALUES
#     data.x <- data$x_correctedgaze[data$event == "img" & data$trial ==1]
#     drv <- diff(data.x)
#     drv.rle <- rle(abs(drv) > max.dist)
#     rle.ind <-
#       which(drv.rle$lengths > num.runs & drv.rle$values == FALSE)
#     
#     rle.cs <- cumsum(drv.rle$lengths)
#     
#     diff.ends <- rle.cs[rle.ind]
#     #print(length(diff.ends))
#     diff.start <- rle.cs[rle.ind - 1]
#     #print(length(diff.start))
#     trues <- unlist(mapply(seq, diff.start, diff.ends))
#     #ifelse(rle.ind == 1, trues <- seq(1,drv.rle$lengths), )
#     
#     #TODO: fix warning
#     #suppressWarnings(data.x$fixation <- TRUE)
#     
#     x_fix <- data.frame(x = matrix(unlist(data.x)))
#     x_fix <- x_fix %>%
#       mutate(fix = FALSE)
#     
#     x_fix$fix[trues] = TRUE
#     
#     x_fix <- x_fix %>% 
#       mutate(time = seq(1, lengths(x_fix)[1]))
#     
#     View(x_fix %>% filter(fix==TRUE))
#     
#     
#     x_fix %>%
#       filter(fix==TRUE) %>%
#       ggplot()+aes(x=time, y=x, color=fix)+geom_point()
# }
    
    #data$fixation <- x_fix$fix[1:(nrow(x_fix) - 1)]
    
    # p <-
    #   data %>% filter(event %in% c("img", "mgs")) %>% mutate(trial = as.numeric(trial)) %>%
    #   ggplot() + aes(x = x_gaze, y = y_gaze, color = fixation) + geom_point() +
    #   facet_wrap(trial ~ event)
    # 
    # png.fn <- sub("txt", "png", files[i])
    # 
    # ggsave(p, file = png.fn)
    # 
    # cat("Image saved to:", png.fn, "- file count: ", file.count, "\n")
    # file.count = file.count + 1
#  }
#  else {
#    append(bad.files, files[i], after=length(bad.files))
#    file.count = file.count + 1
#  }
#}
