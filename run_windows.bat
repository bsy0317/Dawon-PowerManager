@echo off 
set cPath=%cd% 
waitress-serve --listen=0.0.0.0:5001 dawon_pm:app 