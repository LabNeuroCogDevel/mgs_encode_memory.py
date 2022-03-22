library(testthat)
source("eyetracking.R")
test_that("asl range",{
 expect_equal(asl_range1(263),1)
 expect_equal(asl_range1(263/2),0)
 expect_equal(asl_range1(0),-1)
 expect_equal(asl_range1(c(263,263/2,0)),c(1,0,-1))
})
#asl_range1 <- function(x) max(x,263)/263 - (263/2)
