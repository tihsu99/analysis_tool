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

# python3 PlotNuisanceShape.py --era 2017 --region SR_2b2j --channel ele_resolved --input_dir /eos/user/t/tihsu/bHplus/full_run2_v7/Limit_study --mass_point 500 --logy

command=${1}

for region in CR_1b4j SR_2b2j SR_2b3j SR_2b4j SR_3b3j SR_3b4j
do
  for channel in ele_resolved mu_resolved
  do
    if [[ "$region" == "CR_1b4j" ]]; then
      unblind_name="--unblind"
    else
      unblind_name=""
    fi
    command_="python3 PlotNuisanceShape.py --region ${region} --channel ${channel} ${command} ${unblind_name}" 
    echo -e "${BCyan}[tmux: ${region}_${channel}]${NC} ${BYellow} ${command_} ${NC}"
    tmux new-session -d -s $region\_$channel "${command_} ${MASS};"
  done
done


