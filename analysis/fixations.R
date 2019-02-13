library(dplyr)
path<-sprintf("%s%s", getwd(), "/mgs_encode_memory.py/analysis")
source(sprintf("%s%s",path,"/eyetracking.R"))

max.dist <- 0.3
num.runs <- 10
file.count = 1

files <- list.files(path=sprintf("%s%s",path,"/runs"), pattern="*.txt", full.names=TRUE, recursive=FALSE)
bad.files <- vector()

#TODO: Add an if statement after data checking if it is null; if null add filename to "bad files" array

# FOR EACH FILE IN DIRECTORY
for(i in 1:length(files)) {
  # CONVERT ".txt" INTO PARSEABLE DATA FRAME
  data <- read_avotec(files[i])

  if(!is.null(data))
  {
    cat("Reading file:", files[i], "\n")
    
    # TAKE DIFFERENCE BETWEEN X VALUES, GET THE RUN LENGTH ENCODING OF EACH RUN WHERE
    # THE DISTANCE IS GREATER THAN "max.dist", GET THE INDICES OF RLE WHERE LENGTH GREATER
    # THAN "num.runs" AND THE RLE CONTAINS FALSE VALUES
    data.x <- data$x_correctedgaze
    drv <- diff(data.x)
    drv.rle <- rle(abs(drv) > max.dist)
    rle.ind <-
      which(drv.rle$lengths > num.runs & drv.rle$values == FALSE)
    
    rle.cs <- cumsum(drv.rle$lengths)
    
    diff.ends <- rle.cs[rle.ind]
    print(length(diff.ends))
    diff.start <- rle.cs[rle.ind - 1]
    print(length(diff.start))
    ifelse(rle.ind == 1, trues <- seq(1,drv.rle$lengths), trues <- unlist(mapply(seq, diff.start, diff.ends)))
    
    #TODO: fix warning
    suppressWarnings(data.x$fixation <- TRUE)
    
    x_fix <- data.frame(x = matrix(unlist(data.x)))
    x_fix <- x_fix %>%
      mutate(fix = FALSE)
    
    x_fix$fix[trues] = TRUE
    
    data$fixation <- x_fix$fix[1:(nrow(x_fix) - 1)]
    
    p <-
      data %>% filter(event %in% c("img", "mgs")) %>% mutate(trial = as.numeric(trial)) %>%
      ggplot() + aes(x = x_gaze, y = y_gaze, color = fixation) + geom_point() +
      facet_wrap(trial ~ event)
    
    png.fn <- sub("txt", "png", files[i])
    
    ggsave(p, file = png.fn)
    
    cat("Image saved to:", png.fn, "- file count: ", file.count, "\n")
    file.count = file.count + 1
  }
  else {
    append(bad.files, files[i], after=length(bad.files))
    file.count = file.count + 1
  }
}