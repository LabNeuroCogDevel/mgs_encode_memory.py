#!/usr/bin/env Rscript
library(readxl)
library(dplyr)
library(tidyr)

d <- read_xlsx('hierarchy_three_levels/three_levels.xlsx',skip=1)

d.txt <-
   d %>% 
   gather('specific','value',-category,-indoor,-`outdoor, natural`,-`outdoor, man-made`) %>%
   filter(value==1) %>% select(-value) %>%
   gather('generic','value',-category,-specific) %>%
   filter(value==1) %>% select(-value) 
write.table(d.txt,'levels.txt',quote=F,row.names=F,sep="\t")
