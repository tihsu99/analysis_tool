unblind="${3:-''}"

## Compare coupling value
for ERA in run2
do
  for CHANNEL in ee em mm C
  do
    python ./Merged_Plots.py --channel $CHANNEL --year $ERA --coupling_values ${1}0p1 ${1}0p4 ${1}1p0 --plot_y_max 500000 --plot_y_min 0.005 --outputdir $2/Merged_Limit_Plot_$1/pure $unblind --paper
    python ./Merged_Plots.py --channel $CHANNEL --year $ERA --coupling_values ${1}0p1 ${1}0p4 ${1}1p0 --plot_y_max 500000 --plot_y_min 0.005 --outputdir $2/Merged_Limit_Plot_$1/interference --interference $unblind --paper
  done
done

## Compare era
for CHANNEL in ee em mm C
do 
python ./Merged_Plots.py --channel $CHANNEL --year 2016apv 2016postapv 2017 2018 run2 --coupling_values ${1}0p4 --plot_y_max 800 --plot_y_min 0.1 --outputdir $2/Merged_Limit_Plot_$1/pure $unblind
python ./Merged_Plots.py --channel $CHANNEL --year 2016apv 2016postapv 2017 2018 run2 --coupling_values ${1}0p4 --plot_y_max 800 --plot_y_min 0.1 --outputdir $2/Merged_Limit_Plot_$1/interference --interference $unblind
done

for ERA in 2016apv 2016postapv 2017 2018 run2
do
python ./Merged_Plots.py --channel ee em mm C --year $ERA --coupling_values ${1}0p4 --plot_y_max 800 --plot_y_min 0.1 --outputdir $2/Merged_Limit_Plot_$1/pure $unblind
python ./Merged_Plots.py --channel ee em mm C --year $ERA --coupling_values ${1}0p4 --plot_y_max 800 --plot_y_min 0.1 --outputdir $2/Merged_Limit_Plot_$1/interference --interference $unblind
done

