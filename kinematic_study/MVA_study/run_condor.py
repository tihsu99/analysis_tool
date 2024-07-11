import os, sys
import optparse, argparse
import json
sys.path.insert(1, '../../python')
from common import *
import re
import util
from termcolor import cprint

if __name__ == "__main__":
    usage = 'usage: %prog [options]'
    parser = argparse.ArgumentParser(description = usage)
    parser.add_argument('--era', default = ["2017"], nargs = "+")
    parser.add_argument('--region', default = ["all"], nargs = "+")
    parser.add_argument('--channel', default = ["all"], nargs = "+")
    parser.add_argument('--sample_json', default = '../../data/sample.json', nargs = '+')
    parser.add_argument('--cut_json', default = '../../data/cut.json', nargs = '+')
    parser.add_argument('--MVA_json', default = '../../data/MVA.json')
    parser.add_argument('--JobFlavour', dest = 'JobFlavour', help='espresso/microcentury/longlunch/workday/tomorrow', type=str, default='testmatch')
    parser.add_argument('--universe',   dest = 'universe', help='vanilla/local', type=str, default='vanilla')
    parser.add_argument('--indir', type=str)
    parser.add_argument('--outdir', type=str, default='./')
    parser.add_argument('--n_epoch', type=int, default = 200)
    parser.add_argument('--k_fold',  type=int, default = 10)
    parser.add_argument('--bkg_cut', type=int, default = 99999)
    parser.add_argument('--MVA_Label', type=str, default = 'DNN_2b')
    parser.add_argument('--FarmDir', type=str, default = 'Farm')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--xgboost', action='store_true')
    parser.add_argument('--DNN', action='store_true')
    parser.add_argument('--preprocess', action='store_true')
    parser.add_argument('--check', action = 'store_true')
    parser.add_argument('--chunk_size', type = int, default = 500000)
    parser.add_argument('--hyperparameter_tuning', action='store_true')
    parser.add_argument('--GPU', action='store_true')
    args = parser.parse_args()

    farm_dir = os.path.join('./', args.FarmDir)
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
    condor.write('+JobFlavour = "%s"\n'%args.JobFlavour)
    condor.write('queue 1 cfgFile in ')

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

    if args.preprocess:
      Era_set = {'2016': ['2016apv', '2016postapv'], '2017n2018': ['2017', '2018']}
      Region_set = {'2bregion': ['SR_2b2j', 'SR_2b3j', 'SR_2b4j'], '3bregion': ['SR_3b3j', 'SR_3b4j']}
      channels = args.channel
      chunk_size = args.chunk_size

      for era in Era_set:
        for region in Region_set:
          Count_, Weight_ = util.Count_n_Weight(args.indir, Era_set[era], Region_set[region], args.channel, args.sample_json, bkg_max = 10)
          n_sig = 0
          for sig_ in Count_:
            if 'Background' == sig_: continue
            n_sig += Count_[sig_]

          background_maximum = n_sig
          Count_, Weight_ = util.Count_n_Weight(args.indir, args.era, Region_set[region], args.channel, args.sample_json, bkg_max = background_maximum)
          num_chunk = (Count_["Background"] // chunk_size) + 1

          era_str = ' '.join(Era_set[era])
          region_str = ' '.join(Region_set[region])
          channel_str = ' '.join(args.channel)
          indir_clean = args.indir[:-1] if args.indir.endswith('/') else args.indir
          outdir      = os.path.join(indir_clean + "_fullh5_{}".format(region), era)
          CheckGreenLight = True
          for chunk_ in range(num_chunk):
            shell_name = 'produce_h5_{era}_{region}_{chunk}.sh'.format(era = era, region = region, chunk = chunk_)
            command    = 'python preprocess_func.py --era {era} --region {region} --channel {channel} --indir {indir} --outdir {outdir} --chunk_idx {chunk} --total_chunk {total_chunk} --bkg_max {bkg_max}'.format(era = era_str, region = region_str, channel = channel_str, indir = args.indir, outdir = outdir, chunk = chunk_, total_chunk = num_chunk, bkg_max = background_maximum) 
            if args.check and os.path.exists(os.path.join(outdir, 'training_data_{}_raw.h5'.format(chunk_))): continue
            if args.check:
              CheckGreenLight = False
              cprint('reproduce {}'.format(os.path.join(outdir, 'training_data_{}_raw.h5'.format(chunk_))), 'yellow')
            prepare_shell(shell_name, command, condor, farm_dir)

          if args.check and CheckGreenLight:
            cprint('GreenLight for {era} {region}'.format(era = era, region = region), 'green')
            os.system(command + ' --merge')

    if args.xgboost:
      signal_list = Get_Sample(args.sample_json, ["MC", "Signal"], args.era[0], withTail = False)
      for signal_ in signal_list:
        if 'BG' in signal_: continue # TODO: add bg in training as well
        os.system('mkdir -p {}'.format(os.path.join(args.outdir, signal_).replace("root://eosuser.cern.ch//", "")))
        command = 'python Training_xgboost.py {} {} {} {} --sample_json {} --indir {} --outdir {} --postfix {} --signal {} {}'.format(era_command, region_command, channel_command, MVA_command, args.sample_json, args.indir, args.outdir, signal_, signal_, hyperparameter_command)
        prepare_shell('Training_{}_xgboost.sh'.format(signal_), command, condor, farm_dir)


    condor.close()
    if not args.test and not args.DNN:
        os.system('condor_submit %s/condor.sub'%farm_dir)


    if args.DNN:
      # Single Mass Training
      hyperparameter_command += ' --ray_silence '
      #Masses = [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]
      #for Mass in Masses:
      #  outdir_mass = os.path.join(args.outdir, 'M' + str(Mass))
      #  command = 'python Training_DNN.py {} --indir {} --outdir {} --Masses {} {} --n_epoch {} --bkg_cut {} --MVA_Label {} '.format(MVA_command, args.indir, outdir_mass, Mass, hyperparameter_command, args.n_epoch, args.bkg_cut, args.MVA_Label)
      #  prepare_shell('Training_{}_DNN.sh'.format(Mass), command, condor, farm_dir)
      # pNN Training
      Mass_dict = {#'Set1': [200, 400, 600, 800, 1000],
                   #'Set2': [200, 500, 800, 1000],
                   'Set3': [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]}

      dagman_file = open(os.path.join(farm_dir, 'workflow.dag'), 'w')
      for Mass in Mass_dict:
        Mass_dict[Mass] = [str(ele) for ele in Mass_dict[Mass]]
        outdir_mass = os.path.join(args.outdir, 'Mass' + Mass)
        for main_step in [1,2,3]:
          condor_step = open(os.path.join(farm_dir, 'condorMass{Mass}_step{step}.sub'.format(Mass = Mass, step = main_step)), 'w')
          condor_step.write('output = %s/job_common_$(cfgFile)_$(Process).out\n'%farm_dir)
          condor_step.write('error  = %s/job_common_$(cfgFile)_$(Process).err\n'%farm_dir)
          condor_step.write('log    = %s/job_common_$(cfgFile)_$(Process).log\n'%farm_dir)
          condor_step.write('executable = %s/$(cfgFile)\n'%farm_dir)
          condor_step.write('universe = %s\n'%args.universe)
          if args.GPU:
            condor_step.write('request_GPUs = 1\n')
          condor_step.write('+JobFlavour = "%s"\n'%args.JobFlavour)
          condor_step.write('queue 1 cfgFile in ')
     
          all_step = [main_step] if not (main_step == 2) else ['2_{fold}'.format(fold = fold) for fold in range(1, 1+args.k_fold)]

          for step_ in all_step:

            command = 'python Training_DNN.py {} --indir {} --outdir {} --Masses {} {} --n_epoch {} --bkg_cut {} --MVA_Label {} --pNN --k_fold {} --step {}'.format(MVA_command, args.indir, outdir_mass, ' '.join(Mass_dict[Mass]), hyperparameter_command, args.n_epoch, args.bkg_cut, args.MVA_Label, args.k_fold, step_)
            prepare_shell('Training_{}_DNN_{}.sh'.format(Mass, step_), command, condor_step, farm_dir)
          condor_step.close()
          dagman_file.write('JOB DNN{Mass}_step{step} {farm_dir}/condorMass{Mass}_step{step}.sub\n'.format(Mass = Mass, step = main_step, farm_dir = farm_dir))
        dagman_file.write('PARENT DNN{Mass}_step1 CHILD DNN{Mass}_step2\n'.format(Mass = Mass))
        dagman_file.write('PARENT DNN{Mass}_step2 CHILD DNN{Mass}_step3\n'.format(Mass = Mass))
        if not args.test:
          os.system('condor_submit_dag -f %s/workflow.dag'%farm_dir)
