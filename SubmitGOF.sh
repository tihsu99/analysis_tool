#!/bin/bash
#./SubmitGOF.sh saturated [year] [channel] [coupling:rtu04] [mass] [unblind/blind] [interference/pure] 
ALGO=$1
YEAR=$2
CHANNEL=$3
COUPLING=$4
MASS=$5


if [[ $6 == "unblind" ]];then
    UNBLIND="--unblind"
    expectSignal=""
    subFolder_POSTFIX="Unblind"
elif [[ $6 == "sig_bkg" ]];then
    UNBLIND=""
    expectSignal="--expectSignal"
    subFolder_POSTFIX="s_plus_b"
elif [[ $6 == "bkg" ]];then
    UNBLIND=""
    expectSignal=""
    subFolder_POSTFIX="b_only"
else
    exit 1;
fi

if [[ $7 == "interference" ]];then
    type_signal="--$7"
    Higgs="A_interfered_with_S0"
elif [[ $7 == "pure" ]];then
    Higgs="A"
    type_signal=""
else
    echo "please specify Higgs are interefered or pure by interference/pure"
    exit 1;
fi



if [ "${1}" != "saturated" ] && [ "${1}" != "KS" ]  && [ "${1}" != "AD" ]
then
    echo "===== Invalid algorithm \"${1}\". Please select between \"saturated\", \"KS\", and \"AD\"."
    exit 1;
fi

CWD=$(pwd)
nToys=10000
nJobs=20
toysPerJob=$((nToys/nJobs))
datacards=ttc_${COUPLING}_datacard_${YEAR}_SR_${CHANNEL}_${CHANNEL}_MA${MASS}.txt
jobMode=condor
subOpts="+JobFlavour=\"workday\"\nRequestCpus=2" 
echo "=======Current GoodnessofFit information======="
echo "Algo: \"${ALGO}\""
echo "Data taking-year: \"${YEAR}\""
echo "Data taking-channel: \"${CHANNEL}\""
echo "Mass of H: \"${MASS}\"GeV"
echo "Coupling of sample: \"${COUPLING}\""

dirname=SignalExtraction/${YEAR}/${CHANNEL}/${COUPLING}/${Higgs}/${MASS}/${subFolder_POSTFIX}/results/
echo "Start to check whether \"${dirname}\" exist or not. If not then make it."

if [ -d ${dirname} ];then
    cd ${dirname}
    rm ${dirname}/higgsCombine*.${COUPLING}.${YEAR}.${CHANNEL}.${MASS}.${ALGO}.GoodnessOfFit.mH${MASS}.*.root
    cp ${CWD}/datacards_${YEAR}_ttc/$datacards $datacards

    sed -i "s|FinalInputs|${CWD}/FinalInputs|g" $datacards
else
    mkdir -p ${dirname} 
    cd ${dirname} 
    cp ${CWD}/datacards_${YEAR}_ttc/$datacards $datacards
    sed -i "s|FinalInputs|${CWD}/FinalInputs|g" $datacards
fi

echo "=== Submit job for toys (`pwd`)"
for (( t=1; t<=nJobs; t++ ))
do
    echo "=== Submit Jobs for toys $t/$nJobs ==="
    combineTool.py -m ${MASS} -M GoodnessOfFit $datacards --algo=${ALGO}  -t $toysPerJob --job-mode $jobMode --sub-opts=${subOpts} --task-name $t  --seed "$((123456*$t))" -n toys${t}.${COUPLING}.${YEAR}.${CHANNEL}.${MASS}.${ALGO} > dirname=SignalExtraction/${YEAR}/${CHANNEL}/${COUPLING}/${Higgs}/${MASS}/${subFolder_POSTFIX}/SubmitGoF.log 
done

if [[ $6 == "unblind" ]];then
    echo "=== Run job on data:(`pwd`) ==="
    combineTool.py -m ${MASS} -M GoodnessOfFit ${datacards} --algorithm ${ALGO}  -n Data.${COUPLING}.${YEAR}.${CHANNEL}.${MASS}.${ALGO}
fi
cd ${CWD}

#combine -M GoodnessOfFit $datacards --algo=saturated > ~/public/ExtraYukawa/goodness_of_fit_saturate.${NAME}.${COUPLING}.${YEAR}.${CHANNEL}.${MASS}.txt
