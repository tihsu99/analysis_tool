import os
import sys
import optparse, argparse
import subprocess
import json
import ROOT
from collections import OrderedDict
sys.path.insert(1, '../../python')
from common import *
import re

fileset = dict()
fileset['2017'] = {
        'Data': ['MET_{}.root'.format(subera) for subera in subera_list['2017']],
        'TT1L': ['TTTo1L_{}.root'.format(subfile_idx) for subfile_idx in range(1,11)],
        'TT2L': ['TTTo2L_{}.root'.format(subfile_idx) for subfile_idx in range(1,4)],
}
fileset['2018'] = {  
        'Data': [ 'MET_{}.root'.format(subera) for subera in subera_list['2018']],
        'TT1L': ['TTTo1L_{}.root'.format(subfile_idx) for subfile_idx in range(1,14)],
        'TT2L': ['TTTo2L_{}.root'.format(subfile_idx) for subfile_idx in range(1,6)]

}



if __name__ == "__main__":
  
  usage  = 'usage: %prog [options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('-e', '--era',    dest='era',    help='[all/2016apv/2016postapv/2017/2018]',default='all',type=str, choices=["all","2016apv","2016postapv","2017","2018"])
  parser.add_argument('--region',       dest='region', default='all', type=str, choices=['all', 'bh', 'boost'])
  parser.add_argument('--lepton',       dest='lepton', default='all', type=str, choices=['all', 'Electron', 'Muon'])
  parser.add_argument('--JobFlavour', dest = 'JobFlavour', help='espresso/microcentury/longlunch/workday/tomorrow', type=str, default='longlunch')
  parser.add_argument('--universe',   dest = 'universe', help='vanilla/local', type=str, default='vanilla')
  parser.add_argument('--outdir',     dest = 'outdir',     help='output directory',   type=str, default='./')
  parser.add_argument("--test",       action = "store_true")
  parser.add_argument("--check",       action = "store_true")
  parser.add_argument("--sample_json", dest = 'sample_json', type = str, default = "../../data/sample.json")
  parser.add_argument("--data", action='store_true')
  args = parser.parse_args()
  args_dict = vars(args)

  ############
  ##  Path  ##
  ############

  #cmsswBase = os.environ['CMSSW_BASE']
  farm_dir  = os.path.join('./', 'Farm')
  cwd       = os.getcwd()

  os.system('mkdir -p %s '%farm_dir)

  if not os.path.exists(args.outdir):
      os.system('mkdir -p %s'%args.outdir)

  if args.region == 'all':
      regions = ['bh', 'boost']
  else:
      regions = [args.region]

  if args.lepton == 'all':
      leptons = ['Electron', 'Muon']
  else:
      leptons = [args.lepton]
  
  samples        = read_json(args.sample_json)
  ####################
  ## Auto Gen Shell ##
  ####################
  check_text = "python runcondor.py --check "
  for arg in args_dict:
    if isinstance(args_dict[arg], list):
     if len(args_dict[arg]) > 0:
      check_text = check_text + " --" + arg + " " + ' '.join(args_dict[arg])
    elif isinstance(args_dict[arg], bool):
      pass
    else:
      check_text = check_text + " --" + arg + " " + str(args_dict[arg])
  clear_text = check_text + " --clear"
  with open('check.sh', 'w') as shell:
    shell.write(check_text)
  with open('clear.sh', 'w') as shell:
    shell.write(clear_text)
  
  #########
  ## Era ##
  #########

  Eras_List = ['2016apv', '2016postapv', '2017', '2018']
  Eras      = []
  for Era in Eras_List:
    if args.era == 'all' or args.era == Era:
      Eras.append(Era)

  
  ##############
  ##  Condor  ##
  ##############

  condor = open(os.path.join(farm_dir, 'condor.sub'), 'w')
  condor.write('output = %s/job_common_$(Process).out\n'%farm_dir)
  condor.write('error  = %s/job_common_$(Process).err\n'%farm_dir)
  condor.write('log    = %s/job_common_$(Process).log\n'%farm_dir)
  condor.write('executable = %s/$(cfgFile)\n'%farm_dir)
  condor.write('universe = %s\n'%args.universe)
  condor.write('requirements = (OpSysAndVer =?= "CentOS7")\n')
  condor.write('+JobFlavour = "%s"\n'%args.JobFlavour)
  #condor.write('+MaxRuntime = 7200\n')
  cwd = os.getcwd()

  ##############
  ##  Script  ##
  ##############

  Check_GreenLight = True

  for Era in Eras:
   for region in regions:
     for lepton in leptons:
      for variation in ['nominal', 'nPV_up', 'nPV_down', 'nJet_up', 'nJet_down']:
       Outdir   = os.path.join(args.outdir)
       os.system('mkdir -p script')
       os.system('cp %s/../../script/env.sh script/.'%cwd)

       file_dict = fileset[Era] 
       for dataset in file_dict:
         for iin in file_dict[dataset]:
           python_file   =  os.path.join(cwd, 'skim.py')
           fin_raw = iin.replace('.root','')
           sample_name = re.sub(r'_[0-9]+','',fin_raw) 
           ###########################
           ## MC Lumi x xSec / nDAS ##
           ###########################
           if dataset == 'Data': norm_factor = 1.0
           else:
             nDAS  = 0
             for file_ in file_dict[dataset]:
               if ((sample_name + "_") in file_) or ((sample_name + ".") in file_):
                 ftemp = ROOT.TFile.Open(os.path.join(inputFile_path[Era],file_).replace('v2','v3'), "READ")
                 nDAS += ftemp.Get('nEventsGenWeighted').GetBinContent(1)
                 ftemp.Close()
             norm_factor = Lumi[Era]*samples[sample_name]['xsec']/float(nDAS)

           if(args.check):
                fname = os.path.join(Outdir, variation, "{}_{}_".format(region, lepton) + iin)
                try:
                   h = ROOT.TFile.Open(fname,'READ').Get("num")
                   continue
                except Exception as e:
                   print(e)
                   Check_GreenLight=False
           shell_file = "slim_%s_%s_%s_%s_%s.sh"%(iin, Era, region, lepton, variation)
           command = 'python skim.py --era %s --iin %s --dataset %s --outdir %s --region %s --lepton %s --normfactor %f --variation %s'%(Era, iin, dataset, Outdir, region, lepton, norm_factor, variation)
           if args.data:
             if dataset == 'Data': prepare_shell(shell_file, command, condor, farm_dir)
           else:
             prepare_shell(shell_file, command, condor, farm_dir)

  ##################
  ##  Submit Job  ##
  ##################

  condor.close()
  if not args.test and not (args.check and Check_GreenLight):
    print("Submitting Jobs on Condor")
    os.system('condor_submit %s/condor.sub'%farm_dir)

