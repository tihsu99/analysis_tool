#!/bin/bash
WORKDIR=/afs/cern.ch/user/t/tihsu/bHplus/CMSSW_11_3_4/src/analysis_tool/kinematic_study/signal_study
cd /afs/cern.ch/user/t/tihsu/bHplus/CMSSW_11_3_4
cd ${WORKDIR}
source script/env.sh
python /afs/cern.ch/user/t/tihsu/bHplus/CMSSW_11_3_4/src/analysis_tool/kinematic_study/signal_study/calculate_signal_efficiency.py --dataset BGToTHpm_a_1000_rtt06_rtc04 --iin BGToTHpm_a_1000_rtt06_rtc04.root --era 2017 --ele_pt 35 --mu_pt 27 --normfactor 9.185298333036974e-05 --outdir ./ele_35_mu_27