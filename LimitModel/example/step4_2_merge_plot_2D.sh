
source ./env.sh
python3 Merged_Plots.py -y run2 -c C --coupling_values rtu0p1 rtu0p4 rtu0p8 rtu1p0 --outputdir $1 $2 --Masses 200 300 350 400 500 600 700 800 900 1000 --interp --paper
python3 Merged_Plots.py -y run2 -c C --coupling_values rtc0p1 rtc0p4 rtc0p8 rtc1p0 --outputdir $1 $2 --Masses 200 300 350 400 500 600 700 800 900 1000 --interp --paper
python3 Merged_Plots.py -y run2 -c C --coupling_values rtu0p1 rtu0p4 rtu0p8 rtu1p0 --outputdir $1 $2 --Masses 250 300 350 400 550 700 800 900 1000 --interp --interference --paper
python3 Merged_Plots.py -y run2 -c C --coupling_values rtc0p1 rtc0p4 rtc0p8 rtc1p0 --outputdir $1 $2 --Masses 250 300 350 400 550 700 800 900 1000 --interp --interference --paper
