for Lepton in Electron Muon
do
  for era in 2016apv 2016postapv 2017 2018
  do
  cp plot_v2/${era}/bh/${Lepton}/nominal/ScaleFactor.pdf ${1}/plots/TriggerSF/v2/Efficiency_${era}_${Lepton}.pdf
  cp plot_v2/${era}/bh/${Lepton}/nominal/Correlation2D.pdf ${1}/plots/TriggerSF/v2/Correlation2D_${era}_${Lepton}.pdf
  cp data_v2/summary/${era}/bh_${Lepton}_scale_factor_2D_stat.pdf ${1}/plots/TriggerSF/v2/ScaleFactor_${era}_${Lepton}_stat.pdf
  cp data_v2/summary/${era}/bh_${Lepton}_scale_factor_2D_nPV.pdf ${1}/plots/TriggerSF/v2/ScaleFactor_${era}_${Lepton}_nPV.pdf
  cp data_v2/summary/${era}/bh_${Lepton}_scale_factor_2D_nJet.pdf ${1}/plots/TriggerSF/v2/ScaleFactor_${era}_${Lepton}_nJet.pdf
  cp data_v2/summary/${era}/bh_${Lepton}_scale_factor_2D_total.pdf ${1}/plots/TriggerSF/v2/ScaleFactor_${era}_${Lepton}_total.pdf
  cp plot_v2/${era}/bh/${Lepton}/nominal/ScaleFactor.png ${1}/plots/TriggerSF/v2/Efficiency_${era}_${Lepton}.png
  cp plot_v2/${era}/bh/${Lepton}/nominal/Correlation2D.png ${1}/plots/TriggerSF/v2/Correlation2D_${era}_${Lepton}.png
  cp data_v2/summary/${era}/bh_${Lepton}_scale_factor_2D_stat.png ${1}/plots/TriggerSF/v2/ScaleFactor_${era}_${Lepton}_stat.png
  cp data_v2/summary/${era}/bh_${Lepton}_scale_factor_2D_nPV.png ${1}/plots/TriggerSF/v2/ScaleFactor_${era}_${Lepton}_nPV.png
  cp data_v2/summary/${era}/bh_${Lepton}_scale_factor_2D_nJet.png ${1}/plots/TriggerSF/v2/ScaleFactor_${era}_${Lepton}_nJet.png
  cp data_v2/summary/${era}/bh_${Lepton}_scale_factor_2D_total.png ${1}/plots/TriggerSF/v2/ScaleFactor_${era}_${Lepton}_total.png

  done
done
