#!/bin/bash
WORKDIR=/afs/cern.ch/user/t/tihsu/bHplus/CMSSW_11_3_4/src/analysis_tool/kinematic_study/signal_study
cd /afs/cern.ch/user/t/tihsu/bHplus/CMSSW_11_3_4
cd ${WORKDIR}
source script/env.sh
python /afs/cern.ch/user/t/tihsu/bHplus/CMSSW_11_3_4/src/analysis_tool/kinematic_study/signal_study/calculate_signal_efficiency.py --dataset DYnlo --iin DYnlo.root --era 2017 --ele_pt 35 --mu_pt 27 --normfactor 6.357474800918436 --outdir ./ele_35_mu_27