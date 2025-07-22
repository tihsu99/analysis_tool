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


model=${1}
refdir=${2}
cutjson=${3}
workdir=$(pwd)

for MASS in 200 300 350 400 500 600 700 800 900 1000
do
  for RTT in rhott01 rhott04 rhott06 rhott10
  do
      command="python3 prepareCards.py --PhysicsModel ${model} --year 2016apv 2016postapv 2017 2018 --mass ${MASS} --dataset_dir ${refdir} --outdir ${refdir} --cut_json ${cutjson} --combined --merge --rtt ${RTT} --rtc rhotc01 rhotc04 rhotc06 rhotc10 --randomized_scan --mass_detailed ${MASS}"
      echo -e "${BCyan}[tmux: $MASS\_$RTT\_datacard]${NC} ${BYellow} ${command} ${NC}"
    tmux new-session -d -s $MASS\_$RTT\_datacard "${command}"
  done
done


