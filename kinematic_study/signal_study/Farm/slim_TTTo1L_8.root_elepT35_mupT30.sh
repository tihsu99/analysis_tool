#!/bin/bash
WORKDIR=/afs/cern.ch/user/t/tihsu/bHplus/CMSSW_11_3_4/src/analysis_tool/kinematic_study/signal_study
cd /afs/cern.ch/user/t/tihsu/bHplus/CMSSW_11_3_4
cd ${WORKDIR}
source script/env.sh
python /afs/cern.ch/user/t/tihsu/bHplus/CMSSW_11_3_4/src/analysis_tool/kinematic_study/signal_study/calculate_signal_efficiency.py --dataset TTTo1L --iin TTTo1L_8.root --era 2017 --ele_pt 35 --mu_pt 30 --normfactor 0.1464946090963632 --outdir ./ele_35_mu_30