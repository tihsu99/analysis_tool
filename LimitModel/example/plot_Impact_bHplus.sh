
command=$1

if [[ $2 == 0 ]]; then
python3 SignalExtraction_Estimation.py --mode datacard2workspace ${command}
python3 SignalExtraction_Estimation.py --mode Impact_doInitFit ${command}
python3 SignalExtraction_Estimation.py --mode Impact_doFits ${command}
python3 SignalExtraction_Estimation.py --mode SubmitFromEOS ${command}
elif [[ $2 == 1 ]]; then
python3 SignalExtraction_Estimation.py --mode datacard2workspace ${command}
python3 SignalExtraction_Estimation.py --mode FitDiagnostics     ${command}
python3 SignalExtraction_Estimation.py --mode FinalYieldComputation ${command}
python3 SignalExtraction_Estimation.py --mode PlotShape --shape_type preFit --plotRatio ${command}
python3 SignalExtraction_Estimation.py --mode PlotShape --shape_type postFit --plotRatio ${command}
python3 SignalExtraction_Estimation.py --mode diffNuisances ${command}
python3 SignalExtraction_Estimation.py --mode PlotPulls ${command}
python3 SignalExtraction_Estimation.py --mode Impact_doInitFit ${command}
python3 SignalExtraction_Estimation.py --mode Impact_doFits ${command}
python3 SignalExtraction_Estimation.py --mode SubmitFromEOS ${command}
#python3 SignalExtraction_Estimation.py --mode SubmitGOF ${command}
else
python3 SignalExtraction_Estimation.py --mode Plot_Impacts ${command}
fi
