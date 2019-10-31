function [w, hid, et] = mgs_setup()
 sca; close all; clearvars;
 %Eyelink('Initialize')
 bg = [0 0 0];
 screen = 0;
 res = [0 0 800 600];
 w = Screen('OpenWindow', screen, bg, res);
 hid = 0;
 et = 0;

end