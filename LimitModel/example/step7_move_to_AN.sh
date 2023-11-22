## For Merged Limit Plot

for CHANNEL in C ee mm em
do
  for ERA in 2016apv 2016postapv 2017 2018 run2
  do
      cp $1/Merged_Limit_Plot_rtc/pure/plots_limit/*.pdf $2/plots/ttc_merged/$3/Pure/.
      cp $1/Merged_Limit_Plot_rtc/interference/plots_limit/*.pdf $2/plots/ttc_merged/$3/Interference/.
      cp $1/Merged_Limit_Plot_rtu/pure/plots_limit/*.pdf $2/plots/ttu_merged/$3/Pure/.
      cp $1/Merged_Limit_Plot_rtu/interference/plots_limit/*.pdf $2/plots/ttu_merged/$3/Interference/.
  done
done

## For Limit Table
for CHANNEL in C ee mm em
do
  for ERA in 2016apv 2016postapv 2017 2018 run2
  do
    break
#    cp $2/LimitsTables/$ERA/$CHANNEL/$1*.tex $3/sub_tex/LimitsTables/$ERA/$CHANNEL/.
#    cp -r $2/sub_tex/* $3/sub_tex/.
#    cp -r $2/plots/* $3/plots/.
  done
done


