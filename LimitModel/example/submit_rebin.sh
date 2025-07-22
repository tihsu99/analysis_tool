#!/bin/bash

RED='\033[0;31m'
NC='\033[0m'
UBlue='\033[4;34m'        # Blue
BBlack='\033[1;30m'       # Black
BRed='\033[1;31m'         # Red
BGreen='\033[1;32m'       # Green
BYellow='\033[1;33m'      # Yellow
BBlue='\033[1;34m'        # Blue
BPurple='\033[1;35m'      # Purple
BCyan='\033[1;36m'        # Cyan
BWhite='\033[1;37m'       # White

command_=${1}
tag_=${2}
for era in 2016apv 2016postapv 2017 2018
do 
  echo -e "${BYellow}python3 ReBin_condor.py ${command_} --year ${era} --farm Farm_${era}_${tag_}; ${NC}"
  tmux new-session -d -s $era\_${tag_} "python3 ReBin_condor.py ${command_} --year ${era} --farm Farm_${era}_${tag_}"
done
