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

refdir=${1}
datacarddir=${1}/datacards_${3}
outdir=${1}
workdir=$(pwd)
POI=${2}
ERA=run2

for RTT in 0.1 0.4 0.6 1.0
do
  for RTC in 0.1 0.4 0.6 1.0
    do
        echo -e "${BCyan}[tmux: rtt${RTT}_rtc${RTC}_Scan2D]${NC} ${BYellow} python3 runlimits.py --year ${ERA} --channel C --region C --datacard_dir ${datacarddir} --outputdir ${outdir} --POI_name ${POI}  --Masses 200 300 350 400 500 --signal_template CGToBHpm_a_MASS_rhottRTT_rhotcRTC --rtt ${RTT} --rtc ${RTC}; \n 
         python3 runlimits.py --year ${ERA} --channel C --region C --datacard_dir ${datacarddir} --outputdir ${outdir} --POI_name ${POI}  --Masses 600 700 800 900 1000 --signal_template CGToBHpm_a_MASS_rhottRTT_rhotcRTC --rMax 0.1 --rtt ${RTT} --rtc ${RTC};  ${NC}"
        tmux new-session -d -s rtt${RTT}\_rtc${RTC}\_Scan2D "python3 runlimits.py --year ${ERA} --channel C --region C --datacard_dir ${datacarddir} --outputdir ${outdir} --POI_name ${POI}  --Masses 200 300 350 400 500 --signal_template CGToBHpm_a_MASS_rhottRTT_rhotcRTC --rtt ${RTT} --rtc ${RTC}; python3 runlimits.py --year ${ERA} --channel C --region C --datacard_dir ${datacarddir} --outputdir ${outdir} --POI_name ${POI}  --Masses 600 700 800 900 1000 --signal_template CGToBHpm_a_MASS_rhottRTT_rhotcRTC --rMax 0.1 --rtt ${RTT} --rtc ${RTC};"
    done

done
