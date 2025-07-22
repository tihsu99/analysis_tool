command=$1
echo $1

# step 0: GoF
# step 1: Full chain
# step 3: PlotShape
# step 2/else: summary for impacts

ulimit -s unlimited
if [[ $2 == 0 ]]; then
python3 SignalExtraction_Estimation.py --mode datacard2workspace ${command}
#python3 SignalExtraction_Estimation.py --mode Impact_doInitFit ${command}
#python3 SignalExtraction_Estimation.py --mode Impact_doFits ${command}
#python3 SignalExtraction_Estimation.py --mode SubmitFromEOS ${command}
python3 SignalExtraction_Estimation.py --mode SubmitGOF ${command}
python3 SignalExtraction_Estimation.py --mode SubmitGOF ${command} --bonly_gof
elif [[ $2 == 1 ]]; then
python3 SignalExtraction_Estimation.py --mode datacard2workspace ${command}
python3 SignalExtraction_Estimation.py --mode FitDiagnostics     ${command}
python3 SignalExtraction_Estimation.py --mode FinalYieldComputation ${command}
python3 SignalExtraction_Estimation.py --mode PlotShape --shape_type preFit --plotRatio ${command} --logy --combined
python3 SignalExtraction_Estimation.py --mode PlotShape --shape_type postFit --plotRatio ${command} --logy --combined --pull
python3 SignalExtraction_Estimation.py --mode PlotShape --shape_type preFit --plotRatio ${command} --logy
python3 SignalExtraction_Estimation.py --mode PlotShape --shape_type postFit --plotRatio ${command} --logy --pull
python3 SignalExtraction_Estimation.py --mode diffNuisances ${command}
python3 SignalExtraction_Estimation.py --mode PlotPulls ${command}
python3 SignalExtraction_Estimation.py --mode DrawNLL ${command}
python3 SignalExtraction_Estimation.py --mode Impact_doInitFit ${command}
python3 SignalExtraction_Estimation.py --mode Impact_doFits ${command}
python3 SignalExtraction_Estimation.py --mode SubmitFromEOS ${command}
#python3 SignalExtraction_Estimation.py --mode SubmitGOF ${command}
elif [[ $2 == 3 ]]; then
python3 SignalExtraction_Estimation.py --mode PlotShape --shape_type preFit --plotRatio ${command} --logy --combined 
python3 SignalExtraction_Estimation.py --mode PlotShape --shape_type postFit --plotRatio ${command} --logy --combined --pull
python3 SignalExtraction_Estimation.py --mode PlotShape --shape_type preFit --plotRatio ${command} --logy
python3 SignalExtraction_Estimation.py --mode PlotShape --shape_type postFit --plotRatio ${command} --logy --pull
else
python3 SignalExtraction_Estimation.py --mode Plot_Impacts ${command}
python3 SignalExtraction_Estimation.py --mode GoFPlot ${command}
python3 SignalExtraction_Estimation.py --mode GoFPlot ${command} --bonly_gof
fi
