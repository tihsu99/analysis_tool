import os
import sys
import optparse, argparse
import json
import ROOT
from collections import OrderedDict
sys.path.insert(1, '../../python')
from common import *
import re



if __name__ == '__main__':
 
  usage = 'usage: %prog [options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('--era', type=str, default='2017')
  parser.add_argument('--outdir', type=str, default='./')
  parser.add_argument('--JobFlavour', dest = 'JobFlavour', help='espresso/microcentury/longlunch/workday/tomorrow', type=str, default='microcentury')
  parser.add_argument('--universe',   dest = 'universe', help='vanilla/local', type=str, default='vanilla')
  parser.add_argument('--test', action='store_true')
  args = parser.parse_args()
  args_dict = vars(args)

  farm_dir = os.path.join('./', 'Farm')
  cwd      = os.getcwd()
  os.system('mkdir -p %s '%farm_dir)

  if not os.path.exists(args.outdir):
    os.system('mkdir -p %s'%args.outdir)

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
  condor.write('+JobFlavour = "%s"\n'%args.JobFlavour)


  samples = read_json('../../data/sample.json')
  fileset = dict()
  for file_ in os.listdir(inputFile_path[args.era]):
    fin_raw = file_.replace('.root', '')
    if 'CGToBH' not in fin_raw and 'BGToTH' not in fin_raw:
      sample_name = re.sub(r'_[0-9]+','', fin_raw)
    else: sample_name = fin_raw

    if sample_name not in samples: continue
    if 'Data' in samples[sample_name]['Label']: continue 
    if sample_name not in fileset: fileset[sample_name] = [file_]
    else: fileset[sample_name].append(file_)

  print(fileset) 
  


  for dataset in fileset:
    for iin in fileset[dataset]:
      python_file = os.path.join(cwd, 'calculate_signal_efficiency.py')
      fin_raw = iin.replace('.root', '')
      if 'CGToBH' not in fin_raw and 'BGToTH' not in fin_raw:
        sample_name = re.sub(r'_[0-9]+','', fin_raw)
      else: sample_name = fin_raw
      nDAS = 0
      for file_ in fileset[dataset]:
        if((sample_name + "_") in file_) or ((sample_name + ".") in file_):
          ftemp = ROOT.TFile.Open(os.path.join(inputFile_path[args.era], file_), 'READ')
          nDAS += ftemp.Get('nEventsGenWeighted').GetBinContent(1)
          ftemp.Close()
      norm_factor = (Lumi['2016apv'] + Lumi['2017'] + Lumi['2018'] + Lumi['2016postapv']) * samples[sample_name]['xsec']/float(nDAS)
      for ele_pt in [32, 35]:
        for mu_pt in [27, 30]:
          final_output_dir = os.path.join(args.outdir, 'ele_{}_mu_{}'.format(ele_pt, mu_pt))
          os.system('mkdir -p {}'.format(final_output_dir))
          shell_file = 'slim_%s_elepT%d_mupT%d.sh'%(iin,ele_pt,mu_pt)
          command = 'python {} --dataset {} --iin {} --era {} --ele_pt {} --mu_pt {} --normfactor {} --outdir {}'.format(python_file, dataset, iin, args.era, ele_pt, mu_pt, norm_factor, final_output_dir)
          prepare_shell(shell_file, command, condor, farm_dir)

  condor.close()
  if not args.test:
    os.system('condor_submit {}/condor.sub'.format(farm_dir))
