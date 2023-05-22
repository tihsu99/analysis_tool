for era in run2
do
  for channel in C
  do
    for mass in 350 900
    do 
      for mode in preFit impact pull
      do
        for coupling in rtc04
        do
          for Type in A A_interfered_with_S0
          do
            for fit in Unblind
            do
              mkdir -p $1/sub_tex/${mode}/${era}/${channel}/${coupling}/${Type}/${mass}/${fit}
              mkdir -p $1/plots/${mode}/${era}/${channel}/${coupling}/${Type}/${mass}/${fit}
              if [[ $mode == preFit ]]; then
                mkdir -p $1/plots/postFit/${era}/${channel}/${coupling}/${Type}/${mass}/${fit}
              fi

              cp sub_tex/${mode}/${era}/${channel}/${coupling}/${Type}/${mass}/${fit}/* $1/sub_tex/${mode}/${era}/${channel}/${coupling}/${Type}/${mass}/${fit}/. 
              cp plots/${mode}/${era}/${channel}/${coupling}/${Type}/${mass}/${fit}/* $1/plots/${mode}/${era}/${channel}/${coupling}/${Type}/${mass}/${fit}/.
              if [[ $mode == preFit ]]; then
                cp plots/postFit/${era}/${channel}/${coupling}/${Type}/${mass}/${fit}/* $1/plots/postFit/${era}/${channel}/${coupling}/${Type}/${mass}/${fit}/.

              fi
            done
          done
        done
      done
    done
  done
done
