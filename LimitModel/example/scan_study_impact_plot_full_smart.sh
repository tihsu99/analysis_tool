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

# sh exapmle/scan_study_impact_plot_full_smart.sh "--year 2017 --region CR_1b4j --channel mu_resolved --mass_point 500 --outdir /eos/user/t/tihsu/bHplus/Limit_study_full_run2/ --datacard_dir /eos/user/t/tihsu/bHplus/Limit_study_full_run2/datacards_g2HDM_3Bbased/ --cminDefaultMinimizerStrategy 2 --cut_json ..." step
# step 0: GoF
# step 1: Full chain
# step 3: PlotShape
# step 2/else: summary for impacts

# step
command=${1}
step_=${2}
MAX_CONCURRENT=20  # Limit of parallel tmux sessions
SESSION_PREFIX="bHplusImpact"

get_running_sessions() {
    tmux ls 2>/dev/null | grep "^${SESSION_PREFIX}" | wc -l
}

for Mass in 200 300 400 500 600 700 800 900 1000; do
  for channel in ele_resolved mu_resolved C; do
    for region in SR_2b2j SR_2b3j SR_2b4j SR_3b3j SR_3b4j C; do

      # Determine rMax/rMin based on Mass
      if [[ $Mass -gt 550 ]]; then
         rMax=1.0
         rMin=-1.0
      else
         rMax=15.0
         rMin=-15.0
      fi

      # Construct command and session name
      command_="sh example/plot_Impact_bHplus.sh '${command} --mass_point ${Mass} --channel ${channel} --region ${region} --rMax ${rMax} --rMin ${rMin}' ${step_}"
      session_name="${SESSION_PREFIX}_${Mass}_${region}_${channel}"

      # Wait if too many sessions are running
      while [[ $(get_running_sessions) -ge $MAX_CONCURRENT ]]; do
        sleep 5
      done

      echo -e "${BCyan}[tmux: ${session_name}]${NC} ${BYellow}  $command_ ${NC}"
      tmux new-session -d -s "${session_name}" "${command_}"
    done
  done
done

