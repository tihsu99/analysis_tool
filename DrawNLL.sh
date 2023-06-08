#!/bin/bash
#usage: ./DrawNLL.sh run2 C rtc04 200 pure unblind -0.5 3.5
YEAR=$1
CHANNEL=$2
COUPLING=$3
MASS=$4

CURRENT_WORKSPACE=$(pwd)


if [[ $6 == "sig_bkg" ]];then
    UNBLIND=""
    expectSignal="s_plus_b"
elif [[ $6 == 'unblind' ]];then
    UNBLIND="--unblind"
    expectSignal="Unblind"
else
    UNBLIND=""
    expectSignal="b_only"

fi
if [[ $5 == "interference" ]];then
    type_signal="A_interfered_with_S0"
    Interference="--interference"
    MS0="$((MASS-50))"
    workspace_root=ttc_${COUPLING}_datacard_${YEAR}_SR_${CHANNEL}_${CHANNEL}_MA${MASS}_MS${MS0}.root
else
    type_signal="A"
    workspace_root=ttc_${COUPLING}_datacard_${YEAR}_SR_${CHANNEL}_${CHANNEL}_MA${MASS}.root
    Interference=""
fi

OUTDIR=./SignalExtraction/${YEAR}/${CHANNEL}/${COUPLING}/${type_signal}/${MASS}/${expectSignal}

MultiDimFit_root=higgsCombine.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.MultiDimFit.mH${MASS}.root



rMin=${7:-0}
rMax=${8:-10}
npoints=100



echo "datacard-workspace File: ${workspace_root}"
echo "Start to do likelihood Scan"
echo "SingleScan"
SingleScanMultiDimFit_root=higgsCombine.singlescan.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.MultiDimFit.mH${MASS}.root


### Single Fit ####

cd ${OUTDIR}

combine -M MultiDimFit ${workspace_root} -n .singlescan.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal} -m ${MASS} --rMin $rMin --rMax $rMax --algo grid --points $npoints
python plot1DScan.py ${SingleScanMultiDimFit_root} -o Likelihood.singlescan.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.mH${MASS}
###################

### snapshot #####
combine -M MultiDimFit ${workspace_root} -n .snapshot.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal} -m ${MASS} --rMin $rMin --rMax $rMax --saveWorkspace
##################
workspace_root_copy=higgsCombine.snapshot.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.MultiDimFit.mH${MASS}.root

echo "Start to do breakdown profile scan"
combine -M MultiDimFit ${workspace_root_copy} -n .${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal} -m ${MASS} --rMin $rMin --rMax $rMax --algo grid --points $npoints --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit

FreezeExp_MultiDimFit_root=higgsCombine.freeze.exp.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.MultiDimFit.mH${MASS}.root
FreezeExpTheory_MultiDimFit_root=higgsCombine.freeze.exp_theory.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.MultiDimFit.mH${MASS}.root
FreezeExpTheoryCtag_MultiDimFit_root=higgsCombine.freeze.exp_theory_ctag.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.MultiDimFit.mH${MASS}.root
FreezeExpTheoryCtagFake_MultiDimFit_root=higgsCombine.freeze.exp_theory_ctag_fake.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.MultiDimFit.mH${MASS}.root
FreezeAll_MultiDimFit_root=higgsCombine.freeze.All.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.MultiDimFit.mH${MASS}.root

combine -M MultiDimFit ${workspace_root_copy} -n .freeze.exp.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal} -m ${MASS} --rMin $rMin --rMax $rMax --algo grid --points $npoints --freezeNuisanceGroups Exp --snapshotName MultiDimFit

combine -M MultiDimFit ${workspace_root_copy} -n .freeze.exp_theory.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal} -m ${MASS} --rMin $rMin --rMax $rMax --algo grid --points $npoints --freezeNuisanceGroups Exp,Theory --snapshotName MultiDimFit
combine -M MultiDimFit ${workspace_root_copy} -n .freeze.exp_theory_ctag.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal} -m ${MASS} --rMin $rMin --rMax $rMax --algo grid --points $npoints --freezeNuisanceGroups Exp,Theory,c-tagging --snapshotName MultiDimFit
combine -M MultiDimFit ${workspace_root_copy} -n .freeze.exp_theory_ctag_fake.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal} -m ${MASS} --rMin $rMin --rMax $rMax --algo grid --points $npoints --freezeNuisanceGroups Exp,Theory,c-tagging,nonprompt --snapshotName MultiDimFit
combine -M MultiDimFit ${workspace_root_copy} -n .freeze.All.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal} -m ${MASS} --rMin $rMin --rMax $rMax --algo grid --points $npoints --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit

python plot1DScan.py ${SingleScanMultiDimFit_root} --main-label "Total Uncert." -o Likelihood.breakdown.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.mH${MASS}  --others ${FreezeExp_MultiDimFit_root}:"Freeze Exp.":4  ${FreezeExpTheory_MultiDimFit_root}:"Freeze Exp.+Theory":2 ${FreezeExpTheoryCtag_MultiDimFit_root}:"Freeze Exp.+Theory+c-tag":3 ${FreezeExpTheoryCtagFake_MultiDimFit_root}:"Freeze Exp.+Theory+c-tag+Nonprompt":5 ${FreezeAll_MultiDimFit_root}:"Stat. Only":6 --breakdown "Exp, Theory, c-tagging, nonprompt, NormttW, Stat"
python plot1DScan.py ${SingleScanMultiDimFit_root} --main-label "Total Uncert." -o Likelihood.breakdown.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.mH${MASS}  --others ${FreezeExp_MultiDimFit_root}:"Freeze Exp.":4  ${FreezeAll_MultiDimFit_root}:"Stat. Only":6 --breakdown "Exp, Theory, Stat"

combineTool.py -M FastScan -w ${workspace_root}:w

mv Likelihood.singlescan.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.mH${MASS}* ./results
mv Likelihood.breakdown.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.mH${MASS}* ./results
mv nll.pdf ${OUTPUT_DIR}/nll.${YEAR}.${CHANNEL}.${COUPLING}.${type_signal}.${expectSignal}.mH${MASS}.pdf ./results
cd ${CURRENT_WORKSPACE}
