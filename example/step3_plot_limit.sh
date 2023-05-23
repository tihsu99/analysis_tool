unblind=$3
for CHANNEL in C
do
  for ERA in run2
  do
    if [ $1 == rtc ]; then
      python runlimits.py -c $CHANNEL --coupling_value rtc01 -y $ERA --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir $2/limit_plot_rtc/$ERA/$CHANNEL/pure --plot_only --plot_y_max 100000 $unblind;
      python runlimits.py -c $CHANNEL --coupling_value rtc01 -y $ERA --Masses 250 300 350 400 550 700 800 900 1000 --outputdir $2/limit_plot_rtc/$ERA/$CHANNEL/interference --plot_only --plot_y_max 100000 --interference $unblind;
    else
      python runlimits.py -c $CHANNEL --coupling_value rtu01 -y $ERA --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir $2/limit_plot_rtu/$ERA/$CHANNEL/pure --plot_only --plot_y_max 10000 $unblind;
      python runlimits.py -c $CHANNEL --coupling_value rtu01 -y $ERA --Masses 250 300 350 400 550 700 800 900 1000 --outputdir /$2/limit_plot_rtu/$ERA/$CHANNEL/interference --plot_only --plot_y_max 10000 --interference $unblind;
    fi

    for coupling in ${1}04 ${1}10 ${1}08
    do
    python runlimits.py -c $CHANNEL --coupling_value $coupling -y $ERA --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir $2/limit_plot_$1/$ERA/$CHANNEL/pure --plot_only --plot_y_max 1000 $unblind --plot_y_min 0.01;
    python runlimits.py -c $CHANNEL --coupling_value $coupling -y $ERA --Masses 250 300 350 400 550 700 800 900 1000 --outputdir $2/limit_plot_$1/$ERA/$CHANNEL/interference --plot_only --plot_y_max 1000 --interference $unblind --plot_y_min 0.01;
    done    
  done
done

