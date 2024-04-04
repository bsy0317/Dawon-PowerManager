@echo off 
set cPath=%cd% 
waitress-serve --listen=0.0.0.0:6000 dawon_pm:app 