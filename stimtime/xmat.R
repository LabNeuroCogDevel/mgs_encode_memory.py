# functions to redisplay xmat for mgs encode memory task

library(dplyr)
library(cowplot)
library(reshape2)

readXmat<-function(xmatfile) {
  dX <- read.table(xmatfile)
  p<-pipe(sprintf("perl -lne 'print join(\" \", map {s/[#_]/:/g; s/\\W+//g;s/0$//; $_} split(\";\",$1)) if m/.*ColumnLabels.*= \"(.*)\".*/' %s",xmatfile))
  namesX <- readLines(p)
  close(p)
  names(dX) <- strsplit(namesX," ")[[1]]
  return(dX)
}

plotXmat<-function(dX){
   dSmry <- sapply(c('Right','Left','Indoor','Outdoor','None'),
                   function(name) apply(dX[,grepl(name,names(dX))],1,sum))
   dSmry <- as.data.frame(dSmry)

   dSmry$tr <- 1:nrow(dSmry)
   dmSmry <- melt(dSmry,id.vars='tr')
   dmSmry$type <- ifelse(dmSmry$variable %in% c('Right','Left'), 'Side','Type')
   ptl1 <- ggplot(dmSmry) +
      aes(y=tr, x=1, group=variable, fill=variable, alpha=value) +
      geom_tile() +
      facet_grid(.~type) +
      theme(axis.title.x=element_blank(),
            axis.text.x=element_blank(),
            axis.ticks.x=element_blank()) +
      guides(alpha= F)

   #pts <- ggplot(dmSmry) + aes(y=value,x=tr,group=variable,color=variable) + geom_path() + facet_grid(type~.)  
   #ptl <- ggplot(dmSmry) + aes(y=tr,x=variable,group=variable,fill=variable,alpha=value) + geom_tile()
   #plot_grid(pts,ptl)
   return(ptl1)
}

## deal with 1d timings
read1D <- function(f) {
 d <-
  readLines(f) %>% 
  gsub(' ','\n',.) %>% 
  read.table(text=.,sep=":") %>%
  `names<-`(c('onset','dur')) %>%
  mutate(event=gsub('.1D$','',basename(f)))
}

readAllDir <- function(fm,tmversion) {
  globstr <- sprintf(fmt='mri/%s/%s/[^X]*.1D',tmversion,fm) 
  d <- globstr %>% 
   Sys.glob() %>% 
   lapply(read1D) %>% 
   Reduce(x=.,rbind) %>%
   arrange(onset) %>%
   mutate(iti=lead(onset)-onset-dur) 

  iti <- d %>% 
   filter(iti>0) %>% 
   mutate(onset=onset+dur,dur=iti,event='iti')

 d.iti <- rbind(iti,d) %>% arrange(onset) %>% select(-iti)
 return(d.iti)
}

plotTiming <- function(timingtable) {
 noevent <- timingtable %>% mutate(event=gsub("_.*", "", event))
 ggplot(noevent) +
  aes(ymin = onset, ymax = onset + dur, xmin = 1, xmax = 2, fill = event) +
  geom_rect() +
  theme(axis.title.x = element_blank(),
        axis.text.x  = element_blank(),
        axis.ticks.x = element_blank()) +
  scale_fill_manual(values =
                    c("red", "#999999", "#f0f0f0", "lightgreen", "blue"))
}

## plot xmat
plotfile <- function(mzfile, tmversion, mzmeanZ){
  xmat <- sprintf(fmt = "mri/%s/%s/X.xmat.1D", tmversion, mzfile)
  p.vgs <- xmat %>% readXmat %>% plotXmat

  ## timing
  tmz <- mzfile %>% readAllDir(., tmversion)
  p.hist <-
      tmz %>% filter(event %in% c("iti", "dly")) %>%
      ggplot() +
      aes(x = as.factor(dur), fill = event) +
      geom_bar(stat = "count") +
      facet_grid(~event, scales = "free_x") +
      xlab("dur") +
      guides(fill = F)

  p.run <- plotTiming(tmz) +
     ggtitle(sprintf("%s\n%.2f", mzfile, mzmeanZ))

  plot_grid(plot_grid(p.vgs, p.hist, nrow = 2), p.run)
}
