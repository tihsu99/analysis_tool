import os
import sys
import optparse, argparse
import subprocess
import json
import ROOT
from collections import OrderedDict


def prepare_range(path, fin, step):

  try:
    f_read = ROOT.TFile.Open(os.path.join(path, fin))
    entries = (f_read.Get('Events')).GetEntriesFast()
    init = 0
    index = []
    while(init < entries):
      index.append(init)
      init += step
    index.append(int(entries))
    f_read.Close()
    return index

  except:
    print("%s%s fail to process."%(path,fin))
    return None  

if __name__ == "__main__":
  
  usage  = 'usage: %prog [options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('-m', '--method', dest='method', help='[data/slim_mc/slim_data/...]', default='all', type=str)
  parser.add_argument('-e', '--era',    dest='era',    help='[all/2016apv/2016postapv/2017/2018]',default='all',type=str, choices=["all","2016apv","2016postapv","2017","2018"])
  parser.add_argument('--JobFlavour', dest = 'JobFlavour', help='espresso/microcentury/longlunch/workday/tomorrow', type=str, default='workday')
  parser.add_argument('--universe',   dest = 'universe', help='vanilla/local', type=str, default='vanilla')
  parser.add_argument('--outdir',     dest = 'outdir',     help='output directory',   type=str, default='./')
  parser.add_argument("--test",       action = "store_true")
  parser.add_argument("--blocksize",   dest = 'blocksize',   help='segment size', type = int, default = 1000000)
  parser.add_argument("--check",       action = "store_true")
  parser.add_argument("--sample_json", dest = 'sample_json', type = str, default = "../../data/sample.json")
  parser.add_argument("--cut_json", dest = 'cut_json', type = str, default = "../../data/cut.json")
  parser.add_argument('--variable_json',dest='variable_json', default='../../data/variable.json', type=str)
  parser.add_argument('--histogram_json', dest='histogram_json', default='../../data/histogram.json', type=str)
  parser.add_argument('--trigger_json', dest='trigger_json', default='../../data/trigger.json', type=str)
  parser.add_argument('--MET_filter_json', dest='MET_filter_json', default='../../data/MET_filter.json', type=str)
  parser.add_argument('--MVA_json', dest = 'MVA_json', default = '../../data/MVA.json', type=str)
  parser.add_argument('--MVA_weight_dir', dest = 'MVA_weight_dir', default="None", type=str)
  parser.add_argument('--nuisance_json', dest='nuisance_json', default='../../data/nuisance.json', type=str)
  parser.add_argument("--region", dest='region', type=str, default=['all'], nargs='+')
  parser.add_argument("--channel", dest='channel', type=str, default=['all'], nargs='+')
  parser.add_argument("--Btag_WP", default='Medium')
  parser.add_argument("--Labels", dest = 'Labels', default = ['Normal'], nargs='+')
  parser.add_argument("--Black_list", dest = 'Black_list', default = ['Bug'], nargs='+')
  parser.add_argument("--POIs",   dest = 'POIs',   default = ["DEFAULT"], nargs='+')
  parser.add_argument("--clear",  dest = 'clear', action='store_true')
  parser.add_argument("--data",   dest = 'data',  action='store_true')
  args = parser.parse_args()
  args_dict = vars(args)

  ############
  ##  Path  ##
  ############

  #cmsswBase = os.environ['CMSSW_BASE']
  farm_dir  = os.path.join('./', 'Farm')
  cwd       = os.getcwd()

  os.system('mkdir -p %s '%farm_dir)
  os.system('cp %s/../../python/common.py .'%cwd)
  os.system('cp %s/../../python/haddnano.py .'%cwd)

  from common import prepare_shell, Get_Sample, cmsswBase, inputFile_path, read_json, Lumi, inputFile_path

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

  check_text = "python runcondor.py --check "
  for arg in args_dict:
    if isinstance(args_dict[arg], list):
     if len(args_dict[arg]) > 0:
      check_text = check_text + " --" + arg + " " + ' '.join(args_dict[arg])
    elif isinstance(args_dict[arg], bool):
      if args.data: check_text = check_text + "--data "
      else:
        pass
    else:
      check_text = check_text + " --" + arg + " " + str(args_dict[arg])
  clear_text = check_text + " --clear"
  with open('check.sh', 'w') as shell:
    shell.write(check_text)
  with open('clear.sh', 'w') as shell:
    shell.write(clear_text)
  ##################
  ## Sample Label ##
  ##################

  Labels_text = ' '.join(args.Labels)
  if len(args.Black_list) == 0: Black_list_text = ''
  else: 
    Black_list_text = '--Black_list ' + ' '.join(args.Black_list)
  POIs_text   = ' '.join(args.POIs)
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
#  condor.write('requirements = (OpSysAndVer =?= "CentOS7")\n')
  condor.write('+JobFlavour = "%s"\n'%args.JobFlavour)
#  condor.write('+MaxRuntime = 7200\n')
  cwd = os.getcwd()

  ##############
  ##  Script  ##
  ##############

  Check_GreenLight = True

  for Era in Eras:
   for region in region_channel_dict:
     for channel in region_channel_dict[region]:
       Outdir   = os.path.join(args.outdir, Era, region, channel)
       template = "%s/../../script/slim.h"%cwd
       era_header = "script/slim_%s.h"%Era

       os.system('mkdir -p script')
       os.system('cat %s | sed "s/EraToBeReplaced/%s/g" > %s'%(template,Era,era_header))
       os.system('cp %s/../../script/env.sh script/.'%cwd)

       json_file_name = args.sample_json
       sample_label_list = [["Data"]] if args.data else [["MC", "Background"], ["MC", "Signal"], ["Data"]]
       for sample_Label in sample_label_list:

         print("Creating configuration for slim")
         python_file   =  os.path.join(cwd, 'slim.py')
      
         File_List      = Get_Sample(json_file_name, sample_Label, Era) # Use all the MC samples (List of files)
         Sample_List    = Get_Sample(json_file_name, sample_Label, Era, False) # List of process name
         samples        = read_json(json_file_name)
         print(File_List)

         sample_label_text = " ".join(sample_Label)
         print(File_List)
         for iin in File_List:

           ###########################
           ## MC Lumi x xSec / nDAS ##
           ###########################
           for sample_ in Sample_List:
             if ((sample_ + "_") in iin) or ((sample_ + ".") in iin):
               sample_name = sample_

           if "MC" in sample_Label:  # MC normalize with lumi x cross section
             # Find which samples this iin belongs to #TODO(well structure of File_List that contains sample info)
             nDAS  = 0
             for file_ in File_List:
               if ((sample_name + "_") in file_) or ((sample_name + ".") in file_):
                 ftemp = ROOT.TFile.Open(os.path.join(inputFile_path[Era], file_), "READ")
                 nDAS += ftemp.Get('nEventsGenWeighted').GetBinContent(1)
                 ftemp.Close()
             norm_factor = Lumi[Era]*samples[sample_name]['xsec']/float(nDAS)
           else: # data doesn't need to be normalized by lumi x cross section
             norm_factor = 1.0

           if "Region" in samples[sample_name] and region not in samples[sample_name]["Region"]:
             continue
           if "Channel" in samples[sample_name] and channel not in samples[sample_name]["Channel"]:
             continue


           json_command = " --sample_json {} --cut_json {} --variable_json {} --histogram_json {} --nuisance_json {} --trigger_json {} --MET_filter_json {} --MVA_json {}".format(args.sample_json, args.cut_json, args.variable_json, args.histogram_json, args.nuisance_json, args.trigger_json, args.MET_filter_json, args.MVA_json)

           if args.blocksize == -1:
             shell_file = "slim_%s_%s_%s_%s.sh"%(iin, Era, region, channel)
             command = 'python slim.py --era %s --iin %s --outdir %s --region %s --channel %s --Labels %s %s --sample_labels %s --POIs %s --scale %f --Btag_WP %s --MVA_weight_dir %s'%(Era, iin, Outdir, region, channel, Labels_text,Black_list_text, sample_label_text, POIs_text, norm_factor, args.Btag_WP, args.MVA_weight_dir)
             command += json_command
             prepare_shell(shell_file, command, condor, farm_dir)

           else:
             ranges = prepare_range(inputFile_path[Era], iin, args.blocksize)
             for idx, num in enumerate(ranges[:-1]):
               if args.check:
                 try:
                   f  = ROOT.TFile.Open(os.path.join(Outdir, str(idx) + "_" + iin), "READ")
                   if f.IsZombie():
                     print(os.path.join(Outdir, str(idx) + "_" + iin), "is zombie")
                     Check_GreenLight = False
                   elif (f.GetNkeys() == 0):
                     print(os.path.join(Outdir, str(idx) + "_" + iin), "has zero key")
                     Check_GreenLight = False
                   else:
                     f.Close()
                     continue
                   f.Close()
                 except:
                   Check_GreenLight = False
                   print(os.path.join(Outdir, str(idx) + "_" + iin), "not exist")
               start = ranges[idx]
               end   = ranges[idx+1]
               command = 'python slim.py --era %s --iin %s --outdir %s --start %d --end %d --index %d --region %s --channel %s --Labels %s %s --sample_labels %s --POIs %s --scale %f --Btag_WP %s --MVA_weight_dir %s'%(Era, iin, Outdir, start, end, idx, region, channel, Labels_text, Black_list_text, sample_label_text, POIs_text, norm_factor, args.Btag_WP, args.MVA_weight_dir)
               command += json_command
               shell_file = "slim_%s_%s_%s_%s_%d.sh"%(iin, Era, region, channel, idx)
               prepare_shell(shell_file,command, condor, farm_dir)
  #################
  ##  Merge ROOT ##
  #################

  
  if args.check and Check_GreenLight:
    print("All files are produced successfully. Start to merge the files.")

    for Era in Eras:
     for region in region_channel_dict:
       for channel in region_channel_dict[region]:
        for sample_Label in sample_label_list:
         Outdir = os.path.join(args.outdir, Era, region, channel)
         json_file_name = args.sample_json
         File_List      = Get_Sample(json_file_name, sample_Label, Era, withTail = False) # Use all the MC samples
         Final_List     = []
         for iin in File_List:

           if "Region" in samples[iin] and region not in samples[iin]["Region"]:
             continue
           if "Channel" in samples[iin] and channel not in samples[iin]["Channel"]:
             continue

           print("start merging %s"%os.path.join(Outdir, iin))
           merge_list = []
           for file_ in os.listdir(Outdir):
             if "_" + iin + "." in file_ or "_" + iin + "_" in file_:
               merge_list.append(os.path.join(Outdir,file_))
           if not args.clear:
             os.system("rm %s.root"%os.path.join(Outdir, iin))
             os.system("python haddnano.py %s.root %s"%(os.path.join(Outdir, iin), ' '.join(merge_list)))
           if os.path.exists(os.path.join(Outdir, iin + ".root")):
             f = ROOT.TFile.Open(os.path.join(Outdir, iin + ".root"), "READ")
             if f.IsZombie(): #Any other failing situation? TODO
                print(os.path.join(Outdir, iin), "merge failed. Please fixed by hand (at this stage)")
             elif args.clear:
               os.system("rm %s"%os.path.join(Outdir, "*_{}*.root".format(iin)))
  ##################
  ##  Submit Job  ##
  ##################

  condor.close()
  if not args.test and not (args.check and Check_GreenLight):
    print("Submitting Jobs on Condor")
    os.system('condor_submit %s/condor.sub'%farm_dir)

