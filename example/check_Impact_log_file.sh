# sh quick_check_Impact_log_file.sh [rtc/rtu] [outputdir] [mode]

RED='\033[0;31m'
NC='\033[0m'
UBlue='\033[4;34m'        # Blue
BYellow='\033[1;33m'      # Yellow
BGreen='\033[1;32m'       # Green

for era in 2018 run2
do
  for channel in ee em mm C
  do
    for mass in 350 900
    do
      interference_mass=$(($mass-50))
      echo -e "${UBlue}${era}${NC} ${BYellow}${channel}${NC} ${UBlue}${mass}${NC} ${BYellow}b_only${NC}"
      cat $2/SignalExtraction/$era/$channel/${1}04/A/$mass/b_only/ttc_${1}04_datacard_$era\_SR_$channel\_$channel\_MA$mass\_$3\.log
      echo "\n"

      echo -e "${UBlue}${era}${NC} ${BYellow}${channel}${NC} ${UBlue}${mass}${NC} ${BYellow}s_plus_b${NC}"
      cat $2/SignalExtraction/$era/$channel/${1}04/A/$mass/s_plus_b/ttc_${1}04_datacard_$era\_SR_$channel\_$channel\_MA$mass\_$3\.log
      echo "\n"

      echo -e "${UBlue}${era}${NC} ${BYellow}${channel}${NC} ${UBlue}${mass}${NC} ${BYellow}b_only${NC} ${BGreen}interference${NC}"
      cat $2/SignalExtraction/$era/$channel/${1}04/A_interfered_with_S0/$mass/b_only/ttc_${1}04_datacard_$era\_SR_$channel\_$channel\_MA$mass\_MS$interference_mass\_$3\.log
      echo "\n"

      echo -e "${UBlue}${era}${NC} ${BYellow}${channel}${NC} ${UBlue}${mass}${NC} ${BYellow}s_plus_b${NC} ${BGreen}interference${NC}"
      cat $2/SignalExtraction/$era/$channel/${1}04/A_interfered_with_S0/$mass/s_plus_b/ttc_${1}04_datacard_$era\_SR_$channel\_$channel\_MA$mass\_MS$interference_mass\_$3\.log
    done
  done
done


