#!/bin/bash

###########################################################################
# :Usage                                                                  #  
#  - Use tmux to run plot_dis.sh in batch                              #
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

# sh example/plot_Impact_bHplus.sh "--year 2017 --region CR_1b4j --channel mu_resolved --mass_point 500 --outdir /eos/user/t/tihsu/bHplus/Limit_study_full_run2/ --datacard_dir /eos/user/t/tihsu/bHplus/Limit_study_full_run2/datacards_g2HDM_3Bbased/ --cminDefaultMinimizerStrategy 2" 1

command=${1}
step_=${2}


for Mass in 200 300 400 500 600 700 800 900 1000
do
  for channel in C
  do

    if [[ $Mass -gt 550 ]]; then
       rMax=1.0
       rMin=-1.0
    else
       rMax=15.0
       rMin=-15.0
    fi
    command_="sh example/plot_Impact_bHplus.sh '${command} --mass_point ${Mass} --channel ${channel} --rMax ${rMax} --rMin ${rMin}' ${step_}" 
    echo -e "${BCyan}[tmux: ${Mass}_${channel}]${NC} ${BYellow} ${command_} ${NC}"
    tmux new-session -d -s $Mass\_$channel "${command_} ${MASS};"
  done
done


