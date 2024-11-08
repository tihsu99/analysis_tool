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
outdir=${2:-"./"}
workdir=$(pwd)
unblind=${3:-""}

for ERA in run2
do
  for region in C SR_2b2j SR_2b3j SR_3b3j SR_3b4j SR_2b4j CR_1b4j
  do
    echo -e "${BCyan}[tmux: $ERA\_$region\_bH]${NC} ${BYellow} python runlimits.py -c C -r ${region} -y ${ERA} --Masses 200 300 350 400 500 600 700 800 900 1000 --datacarddir ${refdir} --analysis_name bH --signal_template  CGToBHpm_a_MASS_rttRTT_rtcRTC --signal_xsec --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir};python runlimits.py -c C -r ${region} -y ${ERA} --Masses 200 300 350 400 500 600 700 800 900 1000 --datacarddir ${refdir} --analysis_name bH --signal_template  CGToBHpm_a_MASS_rttRTT_rtcRTC --signal_xsec --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir} --plot_only; ${NC}"
    tmux new-session -d -s $ERA\_$region\_bH "python runlimits.py -c C -r ${region} -y ${ERA} --Masses 200 300 350 400 500 600 700 800 900 1000 --datacarddir ${refdir} --analysis_name bH --signal_template  CGToBHpm_a_MASS_rttRTT_rtcRTC --signal_xsec --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir};python runlimits.py -c C -r ${region} -y ${ERA} --Masses 200 300 350 400 500 600 700 800 900 1000 --datacarddir ${refdir} --analysis_name bH --signal_template  CGToBHpm_a_MASS_rttRTT_rtcRTC --signal_xsec --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir} --plot_only;"
    echo -e "${BCyan}[tmux: $ERA\_$region\_TH]${NC} ${BYellow} python runlimits.py -c C -r ${region} -y ${ERA} --Masses 200 300 350 400 500 600 700 800 900 1000 --datacarddir ${refdir} --analysis_name tH --signal_template  BGToTHpm_a_MASS_rttRTT_rtcRTC --signal_xsec --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir};python runlimits.py -c C -r ${region} -y ${ERA} --Masses 200 300 350 400 500 600 700 800 900 1000 --datacarddir ${refdir} --analysis_name tH --signal_template  BGToTHpm_a_MASS_rttRTT_rtcRTC --signal_xsec --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir} --plot_only; ${NC}"
    tmux new-session -d -s $ERA\_$region\_TH "python runlimits.py -c C -r ${region} -y ${ERA} --Masses 200 300 350 400 500 600 700 800 900 1000 --datacarddir ${refdir} --analysis_name tH --signal_template  BGToTHpm_a_MASS_rttRTT_rtcRTC --signal_xsec --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir};python runlimits.py -c C -r ${region} -y ${ERA} --Masses 200 300 350 400 500 600 700 800 900 1000 --datacarddir ${refdir} --analysis_name tH --signal_template  BGToTHpm_a_MASS_rttRTT_rtcRTC --signal_xsec --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir} --plot_only;"
    echo -e "${BCyan}[tmux: $ERA\_$region\_Wprime]${NC} ${BYellow} python runlimits.py -c C -r ${region} -y ${ERA} --Masses 300 500 700 900 1100 --datacarddir ${refdir} --analysis_name Wprime --signal_template  WprimeTotb_leptonicDecays_M_MASS  --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir};python runlimits.py -c C -r ${region} -y ${ERA} --Masses 300 500 700 900 1100 --datacarddir ${refdir} --analysis_name Wprime --signal_template  WprimeTotb_leptonicDecays_M_MASS  --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir} --plot_only; ${NC}"
    tmux new-session -d -s $ERA\_$region\_Wprime "python runlimits.py -c C -r ${region} -y ${ERA} --Masses 300 500 700 900 1100 --datacarddir ${refdir} --analysis_name Wprime --signal_template  WprimeTotb_leptonicDecays_M_MASS  --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir};python runlimits.py -c C -r ${region} -y ${ERA} --Masses 300 500 700 900 1100 --datacarddir ${refdir} --analysis_name Wprime --signal_template  WprimeTotb_leptonicDecays_M_MASS  --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir} --plot_only;"
    echo -e "${BCyan}[tmux: $ERA\_$region\_Hplus]${NC} ${BYellow} python runlimits.py -c C -r ${region} -y ${ERA} --Masses 200 300 350 400 500 600 700 800 1000 1250 1500 1750 2000 2500 3000 --datacarddir ${refdir} --analysis_name Hplus --signal_template   HplusToTB_M_MASS  --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir};python runlimits.py -c C -r ${region} -y ${ERA} --Masses 200 300 350 400 500 600 700 800 1000 1250 1500 1750 2000 2500 3000 --datacarddir ${refdir} --analysis_name Hplus --signal_template  HplusToTB_M_MASS  --plot_y_max  1000 --plot_y_min 0.0005 --outputdir ${refdir} --plot_only; ${NC}"
    tmux new-session -d -s $ERA\_$region\_Hplus "python runlimits.py -c C -r ${region} -y ${ERA} --Masses 200 300 350 400 500 600 700 800 1000 1250 1500 1750 2000 2500 3000 --datacarddir     ${refdir} --analysis_name Hplus --signal_template   HplusToTB_M_MASS  --plot_y_max  1000 --plot_y_min 0.005 --outputdir ${refdir};python runlimits.py -c C -r ${region} -y ${ERA} --Masses 200 300 350 400 500 600 700 800 1000 1250 1500 1750 2000 2500 3000 --datacarddir ${refdir} --analysis_name Hplus --signal_template  HplusToTB_M_MASS  --plot_y_max  1000 --plot_y_min 0.0005 --outputdir ${refdir} --plot_only;"


  done
done


