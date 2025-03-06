import os
import sys
import optparse, argparse
import subprocess
import json
import ROOT
from collections import OrderedDict
import glob
import re
sys.path.insert(1, '../python')
from common import *

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('-y','--year',help='List of Years of data. Default value=["2016postapv"].',default=['2016postapv'],nargs='*')
  parser.add_argument('--region', help='List of regions', default=['all'], nargs='+')
  parser.add_argument('--channel', help='List of channels', default=['all'], nargs='+')
  parser.add_argument('--signal', help='List of signals', default=['all'], nargs='+')
  parser.add_argument('--outputdir',help="Output directory, normally, you do not need to modfiy this value.",default='./')
  parser.add_argument('--inputdir',help="Input directory, normally, you don't need to modfiy this value.",default='/eos/cms/store/group/phys_top/ExtraYukawa/BDT/BDT_output')
  parser.add_argument('--cut_json', default = '../data/cut.json')
  parser.add_argument('--sample_json', default = '../data/sample.json')
  parser.add_argument('--analysis_name', default='bH')
  parser.add_argument('--unblind',action='store_true')
  parser.add_argument('-q','--quiet',action='store_true')
  parser.add_argument('--POI', default = 'BDT')
  parser.add_argument('--sig_norm', action = 'store_true')
  parser.add_argument('--test', action = 'store_true')
  parser.add_argument('--farm', default = 'Farm', type=str)
  parser.add_argument('--merge', action = 'store_true')
  parser.add_argument('--randomized_scan', action = 'store_true')
  args = parser.parse_args()


  year      = ' '.join(args.year)
  region    = ' '.join(args.region)
  channel   = ' '.join(args.channel)
  outputdir = args.outputdir
  inputdir  = args.inputdir
  analysis_name = args.analysis_name
  unblind   = '--unblind' if args.unblind else ''
  POI       = args.POI
  sig_norm  = '--sig_norm' if args.sig_norm else ''
  merge     = '--merge' if args.merge else ''

  farm_dir  = os.path.join('./', args.farm)
  cwd       = os.getcwd()

  if not os.path.exists(farm_dir):
    os.system('mkdir -p {}'.format(farm_dir))

  condor = open(os.path.join(farm_dir, 'condor.sub'), 'w')
  condor.write('output = %s/job_common_$(cfgFile).out\n'%farm_dir)
  condor.write('error  = %s/job_common_$(cfgFile).err\n'%farm_dir)
  condor.write('log    = %s/job_common_$(cfgFile).log\n'%farm_dir)
  condor.write('executable = %s/$(cfgFile)\n'%farm_dir)
  condor.write('universe = vanilla\n')
  condor.write('+JobFlavour = "workday"\n')
  condor.write('queue 1 cfgFile in ')


  jsonfile = open(args.sample_json)
  if python_version == 2: samples = json.load(jsonfile, encoding='utf-8')
  else: samples = json.load(jsonfile)
  samples = Extend_sample_dict(samples, key_word = 'MASS')

  signal_list = []
  if "all" in args.signal:
    for sample_ in samples:
       if "Signal" in samples[sample_]["Label"]:
            if args.randomized_scan:
                if "Randomized_Scan" in samples[sample_]["Label"]:
                      signal_list.append(sample_)
            else:
                signal_list.append(sample_)

  for sig_ in signal_list:
    command = 'python3 ReBin.py --sample_json {sample_json} --era {year} --region {region} --channel {channel} --signal {signal} --outputdir {outputdir} --inputdir {inputdir} --analysis_name {analysis_name} {unblind} --quiet --POI {POI} {sig_norm} --cut_json {cut_json} {merge}'.format(year=year, region=region, channel=channel, signal=sig_, outputdir=outputdir, inputdir=inputdir, analysis_name=analysis_name, unblind=unblind, POI=POI, sig_norm=sig_norm, cut_json = args.cut_json, sample_json = args.sample_json, merge = merge)
    prepare_shell('{}.sh'.format(sig_), command, condor, farm_dir, True)

  condor.close()
  if not args.test:
    os.system('condor_submit {}'.format(os.path.join(farm_dir, 'condor.sub')))
