@echo off
schtasks /change /tn BravoWatcherWatchdog /enable
schtasks /run /tn BravoWatcherWatchdog
