import os
import sys
import optparse, argparse
import subprocess
import json
import ROOT
from collections import OrderedDict
import glob

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

def check_file(fname, key_name=None):
  GreenLight = True
  try:
    f  = ROOT.TFile.Open(fname, "READ")
    if f.IsZombie():
      print(fname, "is zombie")
      GreenLight = False
    elif (f.GetNkeys() == 0):
      print(fname, "has zero key")
      GreenLight = False
    else:
      if (key_name is not None):
        key_list = []
        for e in f.GetListOfKeys():
          key_list.append(e.GetName())
        for key_ in key_name:
          if key_ not in key_list:
            print(fname, "lost key", key_)
            GreenLight = False

      for e in f.GetListOfKeys():
        name = e.GetName()
        obj = e.ReadObj()
        isTree = obj.IsA().InheritsFrom(ROOT.TTree.Class())
        isTH1  = obj.IsA().InheritsFrom(ROOT.TH1.Class())
        isTH2  = obj.IsA().InheritsFrom(ROOT.TH2.Class())
        if not (isTree or isTH1 or isTH2):
          GreenLight = False
          print(fname, "has invalid object:", name)
          break
    f.Close()
  except:
    GreenLight = False
    print(fname, "not exist")
  return GreenLight

def Get_List_Union(fname_list):
  key_name = []
  for fname in fname_list:
    f = ROOT.TFile.Open(fname, "READ")
    for e in f.GetListOfKeys():
      if e.GetName() not in key_name:
        key_name.append(e.GetName())
    f.Close()
  return key_name

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
  parser.add_argument("--pNN",    dest = 'pNN',   action='store_true')
  parser.add_argument("--cutflow", dest = 'cutflow', action='store_true')
  args = parser.parse_args()
  args_dict = vars(args)

  ############
  ##  Path  ##
  ############

  #cmsswBase = os.environ['CMSSW_BASE']
  farm_dir  = os.path.join('./', 'Farm')
  farm_dir_mirror = os.path.join(args.outdir, 'Farm')
  cwd       = os.getcwd()

  os.system('mkdir -p %s '%farm_dir)
  os.system('mkdir -p %s '%farm_dir_mirror)
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
      if args_dict[arg]:
        check_text = check_text + " --{} ".format(arg)
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
  sample_label_list = [["Data"]] if args.data else [["MC", "Background"], ["MC", "Signal"], ["Data"]]
  samples        = read_json(args.sample_json)

  condor      = dict()
  merge_shell = dict()
  DAG_file    = open(os.path.join(farm_dir, 'workflow.dag'), 'w')
  if args.check:
    DAG_resubmit_file = open(os.path.join(farm_dir, 'resubmit.dag'), 'w')

  for Era in Eras:
    condor[Era]      = dict()
    merge_shell[Era] = dict()
    for region in region_channel_dict:
      condor[Era][region]      = dict()
      merge_shell[Era][region] = dict()
      for channel in region_channel_dict[region]:
        condor[Era][region][channel]      = dict()
        merge_shell[Era][region][channel] = dict()
        for sample_Label in sample_label_list:
          json_file_name = args.sample_json
          File_List      = Get_Sample(json_file_name, sample_Label, Era, withTail = False) # Use all the MC samples
          Final_List     = []
          for iin in File_List:
            if "Region" in samples[iin] and region not in samples[iin]["Region"]:
              continue
            if "Channel" in samples[iin] and channel not in samples[iin]["Channel"]:
              continue

            Outdir   = os.path.join(args.outdir, Era, region, channel)
            condor[Era][region][channel][iin] = open(os.path.join(farm_dir, 'condor_{}_{}_{}_{}.sub'.format(Era, region, channel, iin)), 'w')
            condor[Era][region][channel][iin].write('output = %s/job_common_$(cfgFile).out\n'%farm_dir)
            condor[Era][region][channel][iin].write('error  = %s/job_common_$(cfgFile).err\n'%farm_dir)
            condor[Era][region][channel][iin].write('log    = %s/job_common_$(cfgFile).log\n'%farm_dir)
            condor[Era][region][channel][iin].write('executable = %s/$(cfgFile)\n'%farm_dir)
            condor[Era][region][channel][iin].write('universe = %s\n'%args.universe)
            condor[Era][region][channel][iin].write('+JobFlavour = "%s"\n'%args.JobFlavour)
            condor[Era][region][channel][iin].write('on_exit_remove   = (ExitBySignal == False) && (ExitCode == 0)\n')
            condor[Era][region][channel][iin].write('max_retries = 3\n')
            condor[Era][region][channel][iin].write('requirements     = Machine =!= LastRemoteHost\n')
            condor[Era][region][channel][iin].write('RequestCpus = 1\n')
            condor[Era][region][channel][iin].close()
            #condor[Era][region][channel][iin].write('transfer_input_files = {}/{}\n'.format(farm_dir, 'merge_{}_{}_{}_{}.sh'.format(Era, region, channel, iin)))
            #condor[Era][region][channel][iin].write('+PostCmd =  "merge_{}_{}_{}_{}.sh"\n'.format(Era, region, channel, iin))
            #condor[Era][region][channel][iin].write('+MaxRuntime = 7200\n')


            condor_merge = open(os.path.join(farm_dir, 'condor_merge_{}_{}_{}_{}.sub'.format(Era, region, channel, iin)), 'w')
            condor_merge.write('output = %s/job_common_$(cfgFile).out\n'%farm_dir)
            condor_merge.write('error  = %s/job_common_$(cfgFile).err\n'%farm_dir)
            condor_merge.write('log    = %s/job_common_$(cfgFile).log\n'%farm_dir)
            condor_merge.write('executable = %s/$(cfgFile)\n'%farm_dir)
            condor_merge.write('universe = %s\n'%args.universe)
            condor_merge.write('+JobFlavour = "microcentury"\n')
            condor_merge.write('on_exit_remove   = (ExitBySignal == False) && (ExitCode == 0)\n')
            condor_merge.write('max_retries = 3\n')
            condor_merge.write('requirements     = Machine =!= LastRemoteHost\n')
            condor_merge.write('cfgFile={}\nqueue 1\n'.format('merge_{}_{}_{}_{}.sh'.format(Era, region, channel, iin)))
            condor_merge.close()


            if 'eos' in Outdir and 'root://eosuser.cern.ch//' not in Outdir:
              Outdir_revised = 'root://eosuser.cern.ch//' + Outdir
            else:
              Outdir_revised = Outdir
            merge_shell[Era][region][channel][iin] = open(os.path.join(farm_dir, 'merge_{}_{}_{}_{}.sh'.format(Era, region, channel, iin)), 'w')
            merge_shell[Era][region][channel][iin].write('#!/bin/bash\n')
            merge_shell[Era][region][channel][iin].write('WORKDIR=%s\n'%cwd)
            merge_shell[Era][region][channel][iin].write('cd ${WORKDIR}\n')
            merge_shell[Era][region][channel][iin].write('source script/env.sh\n')
#            merge_shell[Era][region][channel][iin].write('mv {}/job*err {}/.\n'.format(farm_dir, farm_dir_mirror))
#            merge_shell[Era][region][channel][iin].write('mv {}/job*out {}/.\n'.format(farm_dir, farm_dir_mirror))
            merge_shell[Era][region][channel][iin].write('rm %s/.sys*\n'%(Outdir))
            merge_shell[Era][region][channel][iin].write("rm %s.root\n"%os.path.join(Outdir, iin))
            merge_shell[Era][region][channel][iin].write("python %s/haddnano.py %s.root"%(cwd, os.path.join(Outdir_revised, iin)))
            merge_shell[Era][region][channel][iin].close()

            job_name = "{}_{}_{}_{}".format(Era, region, channel, iin)
            DAG_file.write('JOB {} {}/condor_{}.sub\n'.format(job_name, farm_dir, job_name))
            DAG_file.write('JOB merge_{} {}/condor_merge_{}.sub\n'.format(job_name, farm_dir, job_name))
            DAG_file.write('PARENT {} CHILD merge_{}\n'.format(job_name, job_name))

  DAG_file.close()

  #############
  ##  Check  ##
  #############
  Failed_Sample = dict()
  for Era in Eras:
    Failed_Sample[Era] = dict()
    for region in region_channel_dict:
      Failed_Sample[Era][region] = dict()
      for channel in region_channel_dict[region]:
        Failed_Sample[Era][region][channel] = dict()
        Failed_Sample[Era][region][channel]['sample'] = []
        Failed_Sample[Era][region][channel]['key'] = []
        Outdir = os.path.join(args.outdir, Era, region, channel)
        for sample_label in sample_label_list:
          File_List = Get_Sample(args.sample_json, sample_label, Era)
          Sample_List = Get_Sample(args.sample_json, sample_label, Era, False)
          for sample in Sample_List:
            if "Region" in samples[sample] and region not in samples[sample]["Region"]:
              continue
            if "Channel" in samples[sample] and channel not in samples[sample]["Channel"]:
              continue
            job_name = "{}_{}_{}_{}".format(Era, region, channel, sample)
            if not check_file(os.path.join(Outdir, '{}.root'.format(sample))):
              condor[Era][region][channel][sample] = open(os.path.join(farm_dir, 'condor_{}_{}_{}_{}.sub'.format(Era, region, channel, sample)), 'a')
              Failed_Sample[Era][region][channel]['sample'].append(sample)
              matched_files = glob.glob(os.path.join(Outdir, '*{}*.root'.format(sample)))
              Failed_Sample[Era][region][channel]['key'] = Get_List_Union(matched_files)
              DAG_resubmit_file.write('JOB {} {}/condor_{}.sub\n'.format(job_name, farm_dir, job_name))
              DAG_resubmit_file.write('JOB merge_{} {}/condor_merge_{}.sub\n'.format(job_name, farm_dir, job_name))
              DAG_resubmit_file.write('PARENT {} CHILD merge_{}\n'.format(job_name, job_name))
              prepare_shell('dummy.sh'.format(job_name), 'echo pass', condor[Era][region][channel][sample], farm_dir)
              condor[Era][region][channel][sample].close()

  print(Failed_Sample)
  DAG_resubmit_file.close()
  

  ############
  ##  Data  ##
  ############
  os.system('mkdir -p script')
  os.system('cp ../../data/DNN.dat script/.')
  os.system('cp ../../data/DNN.hxx script/.')

  os.system('mkdir -p data')
  os.system('cp ../../data/preprocessor.pkl data/.')

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

       os.system('cat %s | sed "s/EraToBeReplaced/%s/g" > %s'%(template,Era,era_header))
       os.system('cp %s/../../script/env.sh script/.'%cwd)

       json_file_name = args.sample_json
       for sample_Label in sample_label_list:

         print("Creating configuration for slim")
         python_file   =  os.path.join(cwd, 'slim.py')
      
         File_List      = Get_Sample(json_file_name, sample_Label, Era) # Use all the MC samples (List of files)
         Sample_List    = Get_Sample(json_file_name, sample_Label, Era, False) # List of process name
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
           json_command += ' --pNN ' if args.pNN else ''
           json_command += ' --cutflow ' if args.cutflow else ''
            
           condor[Era][region][channel][sample_name] = open(os.path.join(farm_dir, 'condor_{}_{}_{}_{}.sub'.format(Era, region, channel, sample_name)), 'a')
           merge_shell[Era][region][channel][sample_name] = open(os.path.join(farm_dir, 'merge_{}_{}_{}_{}.sh'.format(Era, region, channel, sample_name)), 'a')

           if args.blocksize == -1:
             shell_file = "slim_%s_%s_%s_%s.sh"%(iin, Era, region, channel)
             command = 'python slim.py --era %s --iin %s --outdir %s --region %s --channel %s --Labels %s %s --sample_labels %s --POIs %s --scale %f --Btag_WP %s --MVA_weight_dir %s'%(Era, iin, Outdir, region, channel, Labels_text,Black_list_text, sample_label_text, POIs_text, norm_factor, args.Btag_WP, args.MVA_weight_dir)
             command += json_command
             prepare_shell(shell_file, command, condor[Era][region][channel][sample_name], farm_dir)

           else:
             ranges = prepare_range(inputFile_path[Era], iin, args.blocksize)
             for idx, num in enumerate(ranges[:-1]):
               start = ranges[idx]
               end   = ranges[idx+1]
               command = 'python slim.py --era %s --iin %s --outdir %s --start %d --end %d --index %d --region %s --channel %s --Labels %s %s --sample_labels %s --POIs %s --scale %f --Btag_WP %s --MVA_weight_dir %s'%(Era, iin, Outdir, start, end, idx, region, channel, Labels_text, Black_list_text, sample_label_text, POIs_text, norm_factor, args.Btag_WP, args.MVA_weight_dir)
               command += json_command
               shell_file = "slim_%s_%s_%s_%s_%d.sh"%(iin, Era, region, channel, idx)
               if args.check and sample_name in Failed_Sample[Era][region][channel]['sample']:
                 if not check_file(os.path.join(Outdir, '{}_{}'.format(idx, iin)), Failed_Sample[Era][region][channel]['key']):
                   prepare_shell(shell_file,command, condor[Era][region][channel][sample_name], farm_dir)
               if 'eos' in Outdir and 'root://eosuser.cern.ch//' not in Outdir:
                 Outdir_revised = 'root://eosuser.cern.ch//' + Outdir
               else:
                 Outdir_revised = Outdir
               merge_shell[Era][region][channel][sample_name].write(" %s"%(os.path.join(Outdir_revised, '{}_{}'.format(idx, iin)))) 
           condor[Era][region][channel][sample_name].close()
           merge_shell[Era][region][channel][sample_name].close()



  #################
  ##  Merge ROOT ##
  #################

  
#  if args.check and Check_GreenLight:
#    print("All files are produced successfully. Start to merge the files.")
#
#    for Era in Eras:
#     for region in region_channel_dict:
#       for channel in region_channel_dict[region]:
#        for sample_Label in sample_label_list:
#         Outdir = os.path.join(args.outdir, Era, region, channel)
#         json_file_name = args.sample_json
#         File_List      = Get_Sample(json_file_name, sample_Label, Era, withTail = False) # Use all the MC samples
#         Final_List     = []
#         for iin in File_List:
#
#           if "Region" in samples[iin] and region not in samples[iin]["Region"]:
#             continue
#           if "Channel" in samples[iin] and channel not in samples[iin]["Channel"]:
#             continue
#
#           print("start merging %s"%os.path.join(Outdir, iin))
#           merge_list = []
#           for file_ in os.listdir(Outdir):
#             if "_" + iin + "." in file_ or "_" + iin + "_" in file_:
#               merge_list.append(os.path.join(Outdir,file_))
#           if not args.clear:
#             os.system("rm %s.root"%os.path.join(Outdir, iin))
#             os.system("python haddnano.py %s.root %s"%(os.path.join(Outdir, iin), ' '.join(merge_list)))
#           if os.path.exists(os.path.join(Outdir, iin + ".root")):
#             f = ROOT.TFile.Open(os.path.join(Outdir, iin + ".root"), "READ")
#             if f.IsZombie(): #Any other failing situation? TODO
#                print(os.path.join(Outdir, iin), "merge failed. Please fixed by hand (at this stage)")
#             elif args.clear:
#               os.system("rm %s"%os.path.join(Outdir, "*_{}*.root".format(iin)))
  ##################
  ##  Submit Job  ##
  ##################

  os.system('chmod +x haddnano.py')
  for Era in Eras:
    for region in region_channel_dict:
      for channel in region_channel_dict[region]:
        for sample_Label in sample_label_list:
          json_file_name = args.sample_json
          File_List      = Get_Sample(json_file_name, sample_Label, Era, withTail = False) # Use all the MC samples
          for iin in File_List: 
            if "Region" in samples[iin] and region not in samples[iin]["Region"]:
              continue
            if "Channel" in samples[iin] and channel not in samples[iin]["Channel"]:
              continue
            #condor[Era][region][channel][iin].close()
            #merge_shell[Era][region][channel][iin].close()
            os.system('chmod +x {}/{}.sh'.format(farm_dir, 'merge_{}_{}_{}_{}'.format(Era, region, channel, iin)))
            if not args.test and not (args.check and Check_GreenLight):
              print("Submitting Jobs on Condor")
              os.system('rm {}/workflow.dag.*'%farm_dir)
              os.system('condor_submit_dag %s/workflow.dag'%farm_dir)

