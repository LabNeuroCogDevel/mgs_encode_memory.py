library(dplyr)
library(reshape2)
library(ggplot2)
library(cowplot)
source("xmat.R") # readXmat, plotXmat, read1D, readAllDir

tmversion <- "s6e6_neverfirst"
deconfile <- sprintf("mri_decon/%s.txt", tmversion)

d <- read.table(deconfile, header = T, numerals = "no.loss")
dplt <- melt(d, id.vars = "file")
dplt$type <- gsub(".*_", "", dplt$variable)

# dist std norm over files (boxplot)
p.allnorm <-
    ggplot(dplt) +
    aes(x = variable, y = value, color = type) +
    geom_boxplot() +
    theme_bw()
print(p.allnorm)

## best overall, zscore, sum, desc order (min is best)
mz <-
   dplt %>% group_by(variable) %>%
   mutate(z = LNCDR::zscore(value)) %>%
   group_by(file) %>%
   summarise(mean.z = mean(z)) %>%
   arrange(mean.z)

# save top 20
mz %>% head(20) %>%
 write.table(file = sprintf("mri_decon/%s_20.txt", tmversion),
               quote = F, row.names = F, sep = "\t")


plotfile(mz$file[1], tmversion, mz$mean.z[1])
plotfile(mz$file[nrow(mz)], tmversion, mz$mean.z[nrow(mz)])
dev(sprintf('mri_decon/%s.pdf',tmversion))
for (i in 1:20) {
  print(plotfile(mz$file[i], tmversion, mz$mean.z[i]))
  grid.newpage()
}
dev.off()

#mz$file[1] %>% readAllDir %>% write.table(file="exampleout.txt",row.names=F,quote=F)


# ## get min variable
# dm <- dplt %>% group_by(variable) %>% slice(which.min(value))
# 
# # best vgs_dly, dly_mgs, vgs, mgs
# x3642 <- unique(dm$file[duplicated(dm$file)])
# dm[dm$file == x3642,] 
# dplt[dplt$file == x3642,]
# d[d$file == x3642,]
