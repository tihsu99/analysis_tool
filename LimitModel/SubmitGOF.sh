#!/bin/bash
#./SubmitGOF.sh saturated [year] [region] [channel] [coupling:rtu04] [Higgs] [mass] [unblind/blind] [datacard_dir] [datacard_name] 
ALGO=$1
YEAR=$2
REGION=$3
CHANNEL=$4
COUPLING=$5
MASS=$7
DATACARD_DIR=$9
DATACARD=${10}
Higgs=$6
if [[ $8 == "unblind" ]];then
    UNBLIND="--unblind"
    expectSignal=""
    subFolder_POSTFIX="Unblind"
elif [[ $8 == "sig_bkg" ]];then
    UNBLIND=""
    expectSignal="--expectSignal"
    subFolder_POSTFIX="s_plus_b"
elif [[ $8 == "bkg" ]];then
    UNBLIND=""
    expectSignal=""
    subFolder_POSTFIX="b_only"
else
    exit 1;
fi


if [ "${1}" != "saturated" ] && [ "${1}" != "KS" ]  && [ "${1}" != "AD" ]
then
    echo "===== Invalid algorithm \"${1}\". Please select between \"saturated\", \"KS\", and \"AD\"."
    exit 1;
fi

CWD=$(pwd)
nToys=1000
nJobs=20
toysPerJob=$((nToys/nJobs))
datacards=${DATACARD}
jobMode=condor
subOpts="+JobFlavour=\"workday\"\nRequestCpus=2" 
echo "=======Current GoodnessofFit information======="
echo "Algo: \"${ALGO}\""
echo "Data taking-year: \"${YEAR}\""
echo "Data taking-region: \"${REGION}\""
echo "Data taking-channel: \"${CHANNEL}\""
echo "Mass of H: \"${MASS}\"GeV"
echo "Coupling of sample: \"${COUPLING}\""

dirname=SignalExtraction/${YEAR}/${REGION}/${CHANNEL}/${COUPLING}/${Higgs}/${MASS}/${subFolder_POSTFIX}/results/
echo "Start to check whether \"${dirname}\" exist or not. If not then make it."

if [ -d ${dirname} ];then
    cd ${dirname}
    rm ${dirname}/higgsCombine*.${COUPLING}.${YEAR}.${REGION}.${CHANNEL}.${MASS}.${ALGO}.GoodnessOfFit.mH${MASS}.*.root
    cp ${CWD}/${DATACARD_DIR}/$datacards $datacards

    sed -i "s|FinalInputs|${CWD}/FinalInputs|g" $datacards
else
    mkdir -p ${dirname} 
    cd ${dirname} 
    cp ${CWD}/${DATACARD_DIR}/$datacards $datacards
    sed -i "s|FinalInputs|${CWD}/FinalInputs|g" $datacards
fi

echo "=== Submit job for toys (`pwd`)"
for (( t=1; t<=nJobs; t++ ))
do
    echo "=== Submit Jobs for toys $t/$nJobs ==="
    combineTool.py -m ${MASS} -M GoodnessOfFit $datacards --algo=${ALGO}  -t $toysPerJob --job-mode $jobMode --sub-opts=${subOpts} --task-name $t  --seed "$((123456*$t))" -n toys${t}.${COUPLING}.${YEAR}.${REGION}.${CHANNEL}.${MASS}.${ALGO} > SubmitGoF_${t}.log
done

if [[ $7 == "unblind" ]];then
    echo "=== Run job on data:(`pwd`) ==="
    combineTool.py -m ${MASS} -M GoodnessOfFit ${datacards} --algorithm ${ALGO}  -n Data.${COUPLING}.${YEAR}.${REGION}.${CHANNEL}.${MASS}.${ALGO}
fi
cd ${CWD}

#combine -M GoodnessOfFit $datacards --algo=saturated > ~/public/ExtraYukawa/goodness_of_fit_saturate.${NAME}.${COUPLING}.${YEAR}.${CHANNEL}.${MASS}.txt
