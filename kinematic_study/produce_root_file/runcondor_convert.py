import os
import sys
import optparse, argparse
import ROOT
import re
sys.path.insert(1, '../../python')
from common import *


if __name__ == '__main__':
  usage = 'usage: %prog [options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument("--indir", type=str)
  parser.add_argument("--outdir", type=str)
  parser.add_argument('--JobFlavour', dest = 'JobFlavour', help='espresso/microcentury/longlunch/workday/tomorrow', type=str, default='microcentury')
  parser.add_argument('--universe',   dest = 'universe', help='vanilla/local', type=str, default='vanilla')
  parser.add_argument('-e', '--era',    dest='era',    help='[all/2016apv/2016postapv/2017/2018]',default='all',type=str, choices=["all","2016apv","2016postapv","2017","2018"])
  parser.add_argument("--sample_json", dest = 'sample_json', type = str, default = "../../data/sample.json")
  parser.add_argument("--cut_json", dest = 'cut_json', type = str, default = "../../data/cut.json")
  parser.add_argument('--histogram_json', dest='histogram_json', default='../../data/histogram.json', type=str)
  parser.add_argument("--region", dest='region', type=str, default=['all'], nargs='+')
  parser.add_argument("--channel", dest='channel', type=str, default=['all'], nargs='+')
  parser.add_argument("--Labels", dest = 'Labels', default = ['Normal'], nargs='+')
  args = parser.parse_args()
  args_dict = vars(args)


  farm_dir  = os.path.join('./', 'Farm_convert')
  cwd       = os.getcwd()

  os.system('mkdir -p %s '%farm_dir)
  os.system('cp %s/../../script/env.sh script/.'%cwd)


  condor = open(os.path.join(farm_dir, 'condor.sub'), 'w')
  condor.write('output = %s/job_common_$(cfgFile).out\n'%farm_dir)
  condor.write('error  = %s/job_common_$(cfgFile).err\n'%farm_dir)
  condor.write('log    = %s/job_common_$(cfgFile).log\n'%farm_dir)
  condor.write('executable = %s/$(cfgFile)\n'%farm_dir)
  condor.write('universe = %s\n'%args.universe)
  condor.write('+JobFlavour = "%s"\n'%args.JobFlavour)
  condor.write('on_exit_remove   = (ExitBySignal == False) && (ExitCode == 0)\n')
  condor.write('max_retries = 3\n')
  condor.write('requirements     = Machine =!= LastRemoteHost\n')
  condor.write('RequestCpus = 1\n')

  # List of regions
  region_channel_dict = dict()
  cut_regions = read_json(args.cut_json)
  if 'all' in args.region:
    for region_ in cut_regions:
      region_channel_dict[region_] = []
  else:
    for region_ in args.region:
      region_channel_dict[region_] = []

  # List of channels
  for region_ in region_channel_dict:
    if 'all' in args.channel:
      for channel_ in cut_regions[region_]["channel_cut"]:
        region_channel_dict[region_].append(channel_)
    else:
      region_channel_dict[region_] = args.channel

  # List of Era
  Eras_List = ['2016apv', '2016postapv', '2017', '2018']
  Eras      = []
  for Era in Eras_List:
    if args.era == 'all' or args.era == Era:
      Eras.append(Era)

  sample_label_list = [["MC", "Background"], ["MC", "Signal"], ["Data"]]

  Labels_text = ' '.join(args.Labels)
  for Era in Eras:
    for region in region_channel_dict:
      for channel in region_channel_dict[region]:
        Outdir   = os.path.join(args.outdir, Era, region, channel)
        Indir    = os.path.join(args.indir, Era, region, channel)
        for sample_label in sample_label_list:
          Sample_List = Get_Sample(args.sample_json, sample_label, Era, False)
          for sample_ in Sample_List:
            command = "python convert_tree_to_hist.py --indir {indir} --outdir {outdir} --histogram_json {histogram_json} --Labels {Labels} --fin_name {fin}.root --sample_Labels {sample_Labels}".format(indir = Indir, outdir = Outdir, histogram_json = args.histogram_json, Labels = " ".join(args.Labels), sample_Labels = ' '.join(sample_label), fin=sample_)
            prepare_shell('{}_{}_{}_{}.sh'.format(Era, region,channel,sample_), command, condor, farm_dir)
  condor.close()

