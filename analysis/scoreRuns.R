#!/usr/bin/env Rscript
library(plotly)
library(dplyr)
library(tidyr)

source("eyetracking.R")

taskpath <- "/Volumes/L/bea_res/Data/Tasks/MGSEncMem"
to_score <- Sys.glob(file.path(taskpath, "/*/*/eye/1*_2*_run[1-4]_*.txt"))

# TODO: remove already scored

# score
eye_dfs <- lapply(to_score, function(x) x %>% read_avotec %>% fixation_summary )
score_dfs <- lapply(eye_dfs, eye_score, "x_weight")
plot_scored(score_dfs[[9]]) # %>% ggplotly

# ## Shiny app
# # https://plot.ly/r/shiny-coupled-events/
# library(shiny)
# library(plotly)
# ui <- fluidPage(
#        #h2("EyeTracking Score"),
#        #sliderInput("score_i", "score#:", min=1, max=length(score_dfs), value=1),
#        plotlyOutput("score_plot")
#        #fixedRow(column(6, plotlyOutput("p_raw_eye")))
# )
# server <- function(input, output) {
#    d <- score_dfs[[1]]
#    output$score_plot <- renderPlot({plot_scored(d)})
# 
#    # update score plot based on slider
#    observeEvent(input$score_i, {
#      i <- input$score_i
#      d <- score_dfs[[i]]
#      output$score_plot <- renderPlotly({
#         p <- d %>% plot_scored
#      })
#    })
# }
# shinyApp(ui,server)

