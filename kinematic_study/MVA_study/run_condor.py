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
    parser.add_argument('--xgboost', action='store_true')
    parser.add_argument('--DNN', action='store_true')
    parser.add_argument('--hyperparameter_tuning', action='store_true')
    parser.add_argument('--GPU', action='store_true')
    args = parser.parse_args()

    farm_dir = os.path.join('./', 'Farm')
    cwd      = os.getcwd()

    os.system('mkdir -p %s '%farm_dir)


#    os.system('mkdir -p script')
#    os.system('cp %s/../../script/env.sh script/.'%cwd)
    ##############
    ##  Condor  ##
    ##############

    condor = open(os.path.join(farm_dir, 'condor.sub'), 'w')
    condor.write('output = %s/job_common_$(cfgFile)_$(Process).out\n'%farm_dir)
    condor.write('error  = %s/job_common_$(cfgFile)_$(Process).err\n'%farm_dir)
    condor.write('log    = %s/job_common_$(cfgFile)_$(Process).log\n'%farm_dir)
    condor.write('executable = %s/$(cfgFile)\n'%farm_dir)
    condor.write('universe = %s\n'%args.universe)
    if args.GPU:
      condor.write('request_GPUs = 1\n')
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
    hyperparameter_command = '--hyperparameter_tuning' if args.hyperparameter_tuning else ' '


    if args.xgboost:
      signal_list = Get_Sample(args.sample_json, ["MC", "Signal"], args.era[0], withTail = False)
      for signal_ in signal_list:
        if 'BG' in signal_: continue # TODO: add bg in training as well
        os.system('mkdir -p {}'.format(os.path.join(args.outdir, signal_).replace("root://eosuser.cern.ch//", "")))
        command = 'python Training_xgboost.py {} {} {} {} --sample_json {} --indir {} --outdir {} --postfix {} --signal {} {}'.format(era_command, region_command, channel_command, MVA_command, args.sample_json, args.indir, args.outdir, signal_, signal_, hyperparameter_command)
        prepare_shell('Training_{}_xgboost.sh'.format(signal_), command, condor, farm_dir)

    if args.DNN:
      # Single Mass Training
      hyperparameter_command += ' --ray_silence '
      Masses = [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]
      for Mass in Masses:
        outdir_mass = os.path.join(args.outdir, 'M' + str(Mass))
        command = 'python Training_DNN.py {} --indir {} --outdir {} --Masses {} {} --n_epoch 100'.format(MVA_command, args.indir, outdir_mass, Mass, hyperparameter_command)
        prepare_shell('Training_{}_DNN.sh'.format(Mass), command, condor, farm_dir)
      # pNN Training
      Mass_dict = {'Set1': [200, 400, 600, 800, 1000],
                   'Set2': [200, 500, 800, 1000],
                   'Set3': [200, 300, 400, 500, 600, 700, 800, 900, 1000]}
      for Mass in Mass_dict:
        Mass_dict[Mass] = [str(ele) for ele in Mass_dict[Mass]]
        outdir_mass = os.path.join(args.outdir, 'Mass' + Mass)
        command = 'python Training_DNN.py {} --indir {} --outdir {} --Masses {} {} --n_epoch 100 --pNN '.format(MVA_command, args.indir, outdir_mass, ' '.join(Mass_dict[Mass]), hyperparameter_command)
        prepare_shell('Training_{}_DNN.sh'.format(Mass), command, condor, farm_dir)
    condor.close()
    if not args.test:
        os.system('condor_submit %s/condor.sub'%farm_dir)
