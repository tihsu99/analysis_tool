#!/bin/bash

###########################################################################
# :Usage                                                                  #  
#  - Use tmux to run plot_Impact.sh in batch                              #
# :Command                                                                #
#  - sh quick_tmux_batch.sh  ./                                           #
# :Input parameter(order is important)                                    #
#  - 1: rtu/rtc                                                           #
#  - 2: output directory                                                  #
###########################################################################

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

outdir=${2:-"./"}
workdir=$(pwd)
unblind=${3:-""}

for ERA in run2
do
  for channel in C
  do
    for fit_model in b_only
    do
      for interfere in interference pure
      do
        for mass in 350 700 900
        do
          # Remember for 2016-2018, default minimizer setting is 1 0.1
          #          for run2,                                   0 1.0
          if [ $ERA == run2 ]; then
            echo -e "${BCyan}[tmux: ${ERA}_${channel}_${fit_model}_${interfere}_${mass}]${NC} ${BYellow}sh example/plot_Impact.sh ${ERA} ${channel} ${mass} ${1}04 ${fit_model} ${interfere} 0 1.0 ${outdir} ${unblind}${NC}"
            tmux new-session -d -s $ERA\_$channel\_$fit_model\_$interfere\_$mass "sh example/plot_Impact.sh ${ERA} ${channel} ${mass} ${1}04 ${fit_model} ${interfere} 0 1.0 ${outdir} ${unblind}"
          else
            echo -e "${BCyan}[tmux: ${ERA}_${channel}_${fit_model}_${interfere}_${mass}]${NC} ${BYellow}sh example/plot_Impact.sh ${ERA} ${channel} ${mass} ${1}04 ${fit_model} ${interfere} 1 0.1 ${outdir} ${unblind}${NC}"
            tmux new-session -d -s $ERA\_$channel\_$fit_model\_$interfere\_$mass "sh example/plot_Impact.sh ${ERA} ${channel} ${mass} ${1}04 ${fit_model} ${interfere} 1 0.1 ${outdir} ${unblind}"
          fi
        done
      done
    done
  done
done
