import os, sys
import optparse, argparse
import json
sys.path.insert(1, '../../python')
from common import *
import re

if __name__ == "__main__":
    usage = 'usage: %prog [options]'
    parser = argparse.ArgumentParser(description = usage)
    parser.add_argument('--era', default = ["2017"], nargs = "+")
    parser.add_argument('--region', default = ["all"], nargs = "+")
    parser.add_argument('--channel', default = ["all"], nargs = "+")
    parser.add_argument('--sample_json', default = '../../data/sample.json', nargs = '+')
    parser.add_argument('--cut_json', default = '../../data/cut.json', nargs = '+')
    parser.add_argument('--MVA_json', default = '../../data/MVA.json')
    parser.add_argument('--JobFlavour', dest = 'JobFlavour', help='espresso/microcentury/longlunch/workday/tomorrow', type=str, default='workday')
    parser.add_argument('--universe',   dest = 'universe', help='vanilla/local', type=str, default='vanilla')
    parser.add_argument('--indir', type=str)
    parser.add_argument('--outdir', type=str, default='./')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    farm_dir = os.path.join('./', 'Farm')
    cwd      = os.getcwd()

    os.system('mkdir -p %s '%farm_dir)


    os.system('mkdir -p script')
    os.system('cp %s/../../script/env.sh script/.'%cwd)
    ##############
    ##  Condor  ##
    ##############

    condor = open(os.path.join(farm_dir, 'condor.sub'), 'w')
    condor.write('output = %s/job_common_$(Process).out\n'%farm_dir)
    condor.write('error  = %s/job_common_$(Process).err\n'%farm_dir)
    condor.write('log    = %s/job_common_$(Process).log\n'%farm_dir)
    condor.write('executable = %s/$(cfgFile)\n'%farm_dir)
    condor.write('universe = %s\n'%args.universe)
    #condor.write('requirements = (OpSysAndVer =?= "CentOS7")\n')
    condor.write('+JobFlavour = "%s"\n'%args.JobFlavour)
    #condor.write('+MaxRuntime = 7200\n')


#    if 'eos' in args.indir and 'root://' not in args.indir:
#      args.indir = "root://eosuser.cern.ch//" + args.indir

#    if 'eos' in args.outdir and 'root://' not in args.outdir:
#      args.outdir = "root://eosuser.cern.ch//" + args.outdir


    cut_json = read_json(args.cut_json)
    if "all" in args.region:
        region_list = list(cut_json.keys())
        args.region = []
        for region_ in region_list:
            if 'SR' in region_:
                args.region.append(region_)
    if "all" in args.channel:
        args.channel = list(cut_json[args.region[0]]['channel_cut'].keys())

    region_command  = '--region ' + ' '.join(args.region) + ' '
    channel_command = '--channel '  + ' '.join(args.channel) + ' '
    era_command     = '--era ' + ' '.join(args.era) + ' '
    MVA_command     = '--MVA_json {}'.format(args.MVA_json)

    signal_list = Get_Sample(args.sample_json, ["MC", "Signal"], args.era[0], withTail = False)
    for signal_ in signal_list:
      if 'BG' in signal_: continue # TODO: add bg in training as well
      os.system('mkdir -p {}'.format(os.path.join(args.outdir, signal_).replace("root://eosuser.cern.ch//", "")))
      command = 'python Training.py {} {} {} {} --sample_json {} --indir {} --outdir {} --postfix {} --signal {}'.format(era_command, region_command, channel_command, MVA_command, args.sample_json, args.indir, args.outdir, signal_, signal_)
      prepare_shell('Training_{}.sh'.format(signal_), command, condor, farm_dir)

    condor.close()
    if not args.test:
        os.system('condor_submit %s/condor.sub'%farm_dir)
