#!/bin/bash
WORKDIR=/afs/cern.ch/user/t/tihsu/bHplus/CMSSW_11_3_4/src/analysis_tool/kinematic_study/signal_study
cd /afs/cern.ch/user/t/tihsu/bHplus/CMSSW_11_3_4
cd ${WORKDIR}
source script/env.sh
python /afs/cern.ch/user/t/tihsu/bHplus/CMSSW_11_3_4/src/analysis_tool/kinematic_study/signal_study/calculate_signal_efficiency.py --dataset CGToBHpm_a_700_rtt06_rtc04 --iin CGToBHpm_a_700_rtt06_rtc04.root --era 2017 --ele_pt 32 --mu_pt 30 --normfactor 0.012080990811617367 --outdir ./ele_32_mu_30