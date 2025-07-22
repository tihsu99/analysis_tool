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

# sh example/plot_Impact_bHplus.sh "--year 2017 --region CR_1b4j --channel mu_resolved --mass_point 500 --outdir /eos/user/t/tihsu/bHplus/Limit_study_full_run2/ --datacard_dir /eos/user/t/tihsu/bHplus/Limit_study_full_run2/datacards_g2HDM_3Bbased/ --cminDefaultMinimizerStrategy 2  --cut_json ../data/cut_cr_top_mass_top_mass_cut.json" 1

command=${1}
step_=${2}


for region in SR_2b2j SR_2b3j SR_2b4j SR_3b3j SR_3b4j C
do
  for channel in mu_resolved
  do
    command_="sh example/plot_Impact_bHplus.sh '${command} --region ${region} --channel ${channel}' ${step_}"
    echo -e "${BCyan}[tmux: ${region}_${channel}]${NC} ${BYellow} ${command_} ${NC}"
    tmux new-session -d -s $region\_$channel "${command_} ${MASS};"
  done
done
