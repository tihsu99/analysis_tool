unblind=${3:-""}
for ERA in run2
do
  for channel in C
  do
    for fit_model in b_only
    do
#      for interfere in pure
      for interfere in pure interference
      do
#        for mass in 200 300 350 400 500 600 700 800 900 1000
        for mass in 200 250 300 350 400 500 550 600 700 800 900 1000

        do
          expectSignal=""
          if [[ $fit_model == "s_plus_b" ]]; then
          expectSignal="--expectSignal"
          fi
          interference=""
          if [[ $interfere == "interference" ]]; then
          interference="--interference"
          fi

          python ./SignalExtraction_Estimation.py -y $ERA -c $channel --mode Plot_Impacts --coupling_value ${1} --mass_point $mass $expectSignal $interference --outdir $2 $unblind

        done
      done
    done
  done
done

