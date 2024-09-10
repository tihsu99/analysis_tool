import os
import sys
import optparse, argparse
import subprocess
import json
import ROOT
from collections import OrderedDict
import glob
import re
sys.path.insert(1, '../../python')
from common import *
from aux import colors
from termcolor import cprint

def prepare_range(path, fin, step, half, isdata):

  try:
    f_read = ROOT.TFile.Open(os.path.join(path, fin))
    entries = (f_read.Get('Events')).GetEntriesFast()
    init = 0
    index = []
    if not isdata:
      if half == 'first':
        init = 0
        entries = int(entries/2)
      elif(half == 'second'):
        init = int(entries/2)
        entries = entries
      else:
        pass

    while(init < entries):
      index.append(init)
      init += step
    index.append(int(entries))
    f_read.Close()
    return index

  except:
    cprint("%s%s fail to process."%(path,fin), "red")
    return None

def check_file(fname, key_name=None):
  GreenLight = True
  try:
    f  = ROOT.TFile.Open(fname, "READ")
    if f.IsZombie():
      cprint(fname + " is zombie", "red")
      GreenLight = False
    elif (f.GetNkeys() == 0):
      cprint(fname + " has zero key", "red")
      GreenLight = False
    else:
      if (key_name is not None):
        key_list = []
        for e in f.GetListOfKeys():
          key_list.append(e.GetName())
        for key_ in key_name:
          if '_TT1L_' in key_ or '_Signal_' in key_: continue #TODO: Now hardcoded, need to be corrected to process dependent
          if key_ not in key_list:
            cprint(fname + " lost key: " + key_,"red")
            GreenLight = False

      for e in f.GetListOfKeys():
        name = e.GetName()
        obj = e.ReadObj()
        isTree = obj.IsA().InheritsFrom(ROOT.TTree.Class())
        isTH1  = obj.IsA().InheritsFrom(ROOT.TH1.Class())
        isTH2  = obj.IsA().InheritsFrom(ROOT.TH2.Class())
        if not (isTree or isTH1 or isTH2):
          GreenLight = False
          cprint(fname + "has invalid object: " + name, "red")
          break
    f.Close()
  except:
    GreenLight = False
    cprint(fname + " not exist", "red")
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
  parser.add_argument("--blocksize",   dest = 'blocksize',   help='segment size', type = int, default = 5000000)
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
  parser.add_argument("--signal", dest = 'signal', action = 'store_true')
  parser.add_argument("--pNN",    dest = 'pNN',   action='store_true')
  parser.add_argument("--multi_class_pNN", dest = 'multi_class_pNN', action='store_true')
  parser.add_argument("--cutflow", dest = 'cutflow', action='store_true')
  parser.add_argument("--half",   dest = 'half', type=str, default=None)
  parser.add_argument("--notoppt",   dest = 'notoppt',  action='store_true', default = 'False')
  parser.add_argument('--farm',    dest = 'farm',     help='farm_dir directory',   type=str, default='Farm')
  args = parser.parse_args()
  args_dict = vars(args)

  ############
  ##  Path  ##
  ############

  #cmsswBase = os.environ['CMSSW_BASE']
  farm_dir  = os.path.join('./', args.farm)
  cwd       = os.getcwd()

  os.system('mkdir -p %s '%farm_dir)
  os.system('cp %s/../../python/haddnano.py .'%cwd)


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

  argument_text = "python runcondor.py "

  for arg in args_dict:
    if isinstance(args_dict[arg], list):
     if len(args_dict[arg]) > 0:
      argument_text = argument_text + " --" + arg + " " + ' '.join(args_dict[arg])
    elif isinstance(args_dict[arg], bool):
      if args_dict[arg]:
        argument_text = argument_text + " --{} ".format(arg)
    else:
      argument_text = argument_text + " --" + arg + " " + str(args_dict[arg])

  check_text = argument_text + (" --check " if "--check" not in argument_text else "")
  clear_text = check_text.replace("--check", "--check --clear")

  with open(os.path.join(farm_dir, 'check.sh'), 'w') as shell:
    shell.write(check_text + "\n")

  with open(os.path.join(farm_dir, 'clear.sh'), 'w') as shell:
    shell.write(clear_text + "\n")
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
  sample_label_list = [["MC", "Signal"]] if args.signal else sample_label_list
  samples        = read_json(args.sample_json)
  samples        = Extend_sample_dict(samples, key_word = 'MASS')

  condor      = dict()
  merge_shell = dict()
  DAG_file    = open(os.path.join(farm_dir, 'workflow.dag'), 'w')
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

            process_list = []
            if "SubProcess" in samples[iin]:
              for subprocess in samples[iin]["SubProcess"]:
                process_list.append(subprocess)
            else:
              process_list.append(iin)
            Outdir   = os.path.join(args.outdir, Era, region, channel)

            for process_ in process_list:
              condor[Era][region][channel][process_] = open(os.path.join(farm_dir, 'condor_{}_{}_{}_{}.sub'.format(Era, region, channel, process_)), 'w')
              condor[Era][region][channel][process_].write('output = %s/job_common_$(cfgFile).out\n'%farm_dir)
              condor[Era][region][channel][process_].write('error  = %s/job_common_$(cfgFile).err\n'%farm_dir)
              condor[Era][region][channel][process_].write('log    = %s/job_common_$(cfgFile).log\n'%farm_dir)
              condor[Era][region][channel][process_].write('executable = %s/$(cfgFile)\n'%farm_dir)
              condor[Era][region][channel][process_].write('universe = %s\n'%args.universe)
              condor[Era][region][channel][process_].write('+JobFlavour = "%s"\n'%args.JobFlavour)
              condor[Era][region][channel][process_].write('on_exit_remove   = (ExitBySignal == False) && (ExitCode == 0)\n')
              condor[Era][region][channel][process_].write('max_retries = 3\n')
              condor[Era][region][channel][process_].write('requirements     = Machine =!= LastRemoteHost\n')
              condor[Era][region][channel][process_].write('RequestCpus = 1\n')
              condor[Era][region][channel][process_].write('queue 1 cfgFile in ')
              condor[Era][region][channel][process_].close()
              #condor[Era][region][channel][process_].write('transfer_input_files = {}/{}\n'.format(farm_dir, 'merge_{}_{}_{}_{}.sh'.format(Era, region, channel, process_)))
              #condor[Era][region][channel][process_].write('+PostCmd =  "merge_{}_{}_{}_{}.sh"\n'.format(Era, region, channel, process_))
              #condor[Era][region][channel][process_].write('+MaxRuntime = 7200\n')


              condor_merge = open(os.path.join(farm_dir, 'condor_merge_{}_{}_{}_{}.sub'.format(Era, region, channel, process_)), 'w')
              condor_merge.write('output = %s/job_common_$(cfgFile).out\n'%farm_dir)
              condor_merge.write('error  = %s/job_common_$(cfgFile).err\n'%farm_dir)
              condor_merge.write('log    = %s/job_common_$(cfgFile).log\n'%farm_dir)
              condor_merge.write('executable = %s/$(cfgFile)\n'%farm_dir)
              condor_merge.write('universe = %s\n'%args.universe)
              condor_merge.write('+JobFlavour = "microcentury"\n')
              condor_merge.write('on_exit_remove   = (ExitBySignal == False) && (ExitCode == 0)\n')
              condor_merge.write('max_retries = 3\n')
              condor_merge.write('requirements     = Machine =!= LastRemoteHost\n')
              condor_merge.write('cfgFile={}\nqueue 1\n'.format('merge_{}_{}_{}_{}.sh'.format(Era, region, channel, process_)))
              condor_merge.close()


              if 'eos' in Outdir and 'root://eosuser.cern.ch//' not in Outdir:
                Outdir_revised = 'root://eosuser.cern.ch//' + Outdir
              else:
                Outdir_revised = Outdir
              merge_shell[Era][region][channel][process_] = open(os.path.join(farm_dir, 'merge_{}_{}_{}_{}.sh'.format(Era, region, channel, process_)), 'w')
              merge_shell[Era][region][channel][process_].write('#!/bin/bash\n')
              merge_shell[Era][region][channel][process_].write('WORKDIR=%s\n'%cwd)
              merge_shell[Era][region][channel][process_].write('cd ${WORKDIR}\n')
              merge_shell[Era][region][channel][process_].write('source script/env.sh\n')
#             merge_shell[Era][region][channel][process_].write('mv {}/job*err {}/.\n'.format(farm_dir, farm_dir_mirror))
#             merge_shell[Era][region][channel][process_].write('mv {}/job*out {}/.\n'.format(farm_dir, farm_dir_mirror))
              merge_shell[Era][region][channel][process_].write('rm %s/.sys*\n'%(Outdir))
              merge_shell[Era][region][channel][process_].write("rm %s.root\n"%os.path.join(Outdir, process_))
              merge_shell[Era][region][channel][process_].write("python %s/haddnano.py %s.root"%(cwd, os.path.join(Outdir_revised, process_)))
              merge_shell[Era][region][channel][process_].close()

              job_name = "{}_{}_{}_{}".format(Era, region, channel, process_)
              DAG_file.write('JOB {} {}/condor_{}.sub\n'.format(job_name, farm_dir, job_name))
              DAG_file.write('JOB merge_{} {}/condor_merge_{}.sub\n'.format(job_name, farm_dir, job_name))
              DAG_file.write('PARENT {} CHILD merge_{}\n'.format(job_name, job_name))

  DAG_file.close()

  #############
  ##  Check  ##
  #############

  Check_GreenLight = True

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
            process_list = []
            if "SubProcess" in samples[sample]:
              for process in samples[sample]["SubProcess"]:
                process_list.append(process)
            else:
              process_list.append(sample)
            for process_ in process_list:
              job_name = "{}_{}_{}_{}".format(Era, region, channel, process_)
              if args.check and not check_file(os.path.join(Outdir, '{}.root'.format(process_))):
                condor[Era][region][channel][process_] = open(os.path.join(farm_dir, 'condor_{}_{}_{}_{}.sub'.format(Era, region, channel, process_)), 'a')
                Failed_Sample[Era][region][channel]['sample'].append(process_)
                matched_files = glob.glob(os.path.join(Outdir, '*{}*.root'.format(process_)))
                Failed_Sample[Era][region][channel]['key'] = Get_List_Union(matched_files)
                DAG_resubmit_file.write('JOB {} {}/condor_{}.sub\n'.format(job_name, farm_dir, job_name))
                DAG_resubmit_file.write('JOB merge_{} {}/condor_merge_{}.sub\n'.format(job_name, farm_dir, job_name))
                DAG_resubmit_file.write('PARENT {} CHILD merge_{}\n'.format(job_name, job_name))
                prepare_shell('dummy.sh'.format(job_name), 'echo pass', condor[Era][region][channel][process_], farm_dir)
                condor[Era][region][channel][process_].close()
                Check_GreenLight = False

  print(Failed_Sample)
  DAG_resubmit_file.close()


  ############
  ##  Data  ##
  ############
  os.system('mkdir -p script')

  os.system('mkdir -p data')
#  os.system('cp ../../data/*.pkl data/.')
#  os.system('cp ../../data/*.dat data/.')
#  os.system('cp ../../data/*.hxx data/.')

  ##############
  ##  Script  ##
  ##############


  for Era in Eras:
   for region in region_channel_dict:
     for channel in region_channel_dict[region]:
       Outdir   = os.path.join(args.outdir, Era, region, channel)
       template = "%s/../../script/slim.h"%cwd
       era_header = "script/slim_%s.h"%Era

       os.system('cat %s | sed "s/EraToBeReplaced/%s/g" > %s'%(template,Era,era_header))

       print ("Replacing SpecialEra on", era_header)
       if (Era == "2016apv"):
         os.system(r'sed -i "s/SpecialEra/%s/g" %s' %('2016APV',era_header))
       elif (Era == "2016postapv"):
         os.system(r'sed -i "s/SpecialEra/%s/g" %s' %('2016',era_header))
       else:
         os.system(r'sed -i "s/SpecialEra/%s/g" %s' %(Era,era_header))

       os.system('cp %s/../../script/env.sh script/.'%cwd)

       json_file_name = args.sample_json
       for sample_Label in sample_label_list:

         cprint("Creating configuration for slim (Era: {}, Region: {}, Channel: {})".format(Era, region, channel), "yellow")
         python_file   =  os.path.join(cwd, 'slim.py')

         File_List      = Get_Sample(json_file_name, sample_Label, Era) # Use all the MC samples (List of files)
         Sample_List    = Get_Sample(json_file_name, sample_Label, Era, False) # List of process name
         sample_label_text = " ".join(sample_Label)
         print(File_List)
         for iin in File_List:

           ###########################
           ## MC Lumi x xSec / nDAS ##
           ###########################
           if 'Signal' in sample_Label: sample_name = iin.replace('.root', '')
           elif 'Data' in sample_Label: sample_name = iin.split('_')[0]
           else: sample_name = re.sub(r'((?:_(\d+|\w))|(?:_\w_\d)|(?:_\w\d))\.root','', iin).replace('.root','')
           if "MC" in sample_Label:  # MC normalize with lumi x cross section
             # Find which samples this iin belongs to #TODO(well structure of File_List that contains sample info)
             nDAS  = 0
             for file_ in File_List:
               if 'Signal' in sample_Label:  sample_name_file = file_.replace('.root', '') # Special rule for signal
               else: sample_name_file = re.sub(r'((?:_(\d+|\w))|(?:_\w_\d)|(?:_\w\d))\.root','', file_).replace('.root','')
               if (sample_name == sample_name_file):
                 ftemp = ROOT.TFile.Open(os.path.join(inputFile_path[Era], file_), "READ")
                 nDAS += ftemp.Get('nEventsGenWeighted').GetBinContent(1)
                 ftemp.Close()
             norm_factor = Lumi[Era]*samples[sample_name]['xsec']/float(nDAS)
             if args.half in ['first', 'second']:  norm_factor = norm_factor*2
           else: # data doesn't need to be normalized by lumi x cross section
             norm_factor = 1.0

           if "Region" in samples[sample_name] and region not in samples[sample_name]["Region"]:
             continue
           if "Channel" in samples[sample_name] and channel not in samples[sample_name]["Channel"]:
             continue

           process_list = []
           if "SubProcess" in samples[sample_name]:
             for subprocess in samples[sample_name]["SubProcess"]:
               process_list.append(subprocess)
           else:
             process_list.append(sample_name)

           json_command = " --sample_json {} --cut_json {} --variable_json {} --histogram_json {} --nuisance_json {} --trigger_json {} --MET_filter_json {} --MVA_json {}".format(args.sample_json, args.cut_json, args.variable_json, args.histogram_json, args.nuisance_json, args.trigger_json, args.MET_filter_json, args.MVA_json)
           json_command += ' --pNN ' if args.pNN else ''
           json_command += ' --multi_class_pNN ' if args.multi_class_pNN else ''
           json_command += ' --cutflow ' if args.cutflow else ''
           json_command += ' --notoppt ' if args.notoppt else ''

           for process_ in process_list:
             if args.clear:
               if process_ == 'TTTo1L' or process_ == 'TTTo2L':
                 os.system('rm {outdir}/*_{process}_*.root'.format(outdir=Outdir, process=process_))
               else:
                 os.system('rm {outdir}/*_{process}.root'.format(outdir=Outdir, process=process_))
               continue
             condor[Era][region][channel][process_] = open(os.path.join(farm_dir, 'condor_{}_{}_{}_{}.sub'.format(Era, region, channel, process_)), 'a')
             merge_shell[Era][region][channel][process_] = open(os.path.join(farm_dir, 'merge_{}_{}_{}_{}.sh'.format(Era, region, channel, process_)), 'a')
             # Clear the files except the merged one

             if args.blocksize == -1:
               shell_file = "slim_%s_%s_%s_%s_%s.sh"%(iin, Era, region, channel,process_)
               command = 'python slim.py --era %s --iin %s --outdir %s --region %s --channel %s --Labels %s %s --sample_labels %s --POIs %s --scale %f --Btag_WP %s --MVA_weight_dir %s --SubProcess %s'%(Era, iin, Outdir, region, channel, Labels_text,Black_list_text, sample_label_text, POIs_text, norm_factor, args.Btag_WP, args.MVA_weight_dir, process_)
               command += json_command
               prepare_shell(shell_file, command, condor[Era][region][channel][process_], farm_dir)

             else:
               ranges = prepare_range(inputFile_path[Era], iin, args.blocksize, half=args.half, isdata=("Data" in sample_Label))
               for idx, num in enumerate(ranges[:-1]):
                 start = ranges[idx]
                 end   = ranges[idx+1]
                 command = 'python slim.py --era %s --iin %s --outdir %s --start %d --end %d --index %d --region %s --channel %s --Labels %s %s --sample_labels %s --POIs %s --scale %f --Btag_WP %s --MVA_weight_dir %s --SubProcess %s'%(Era, iin, Outdir, start, end, idx, region, channel, Labels_text, Black_list_text, sample_label_text, POIs_text, norm_factor, args.Btag_WP, args.MVA_weight_dir, process_)
                 command += json_command
                 shell_file = "slim_%s_%s_%s_%s_%d_%s.sh"%(iin, Era, region, channel, idx, process_)
                 outputfile_name = '{}_{}.root'.format(idx, process_) if "SubProcess" in samples[sample_name] else '{}_{}'.format(idx, iin)

                 if not args.check:
                     prepare_shell(shell_file,command, condor[Era][region][channel][process_], farm_dir)
                 elif args.check and process_ in Failed_Sample[Era][region][channel]['sample']:
                   if not check_file(os.path.join(Outdir, outputfile_name), Failed_Sample[Era][region][channel]['key']):
                     prepare_shell(shell_file,command, condor[Era][region][channel][process_], farm_dir)

                 if 'eos' in Outdir and 'root://eosuser.cern.ch//' not in Outdir:
                   Outdir_revised = 'root://eosuser.cern.ch//' + Outdir
                 else:
                   Outdir_revised = Outdir

                 merge_shell[Era][region][channel][process_].write(" %s"%(os.path.join(Outdir_revised, outputfile_name)))
             condor[Era][region][channel][process_].close()
             merge_shell[Era][region][channel][process_].close()


  #################
  # clear individual root files
  #################
  if args.check and Check_GreenLight:
    cprint("All files are produced successfully and merged as well.", "green")
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

           print(colors.colordict['ORANGE'] + "start deleting %s individuals"%os.path.join(Outdir, iin)+ colors.colordict['CEND']) #gkole
           if os.path.exists(os.path.join(Outdir, iin + ".root")):
             if args.clear:
               # print ("rm %s"%os.path.join(Outdir, "*_{}*.root".format(iin)))
               os.system("rm %s"%os.path.join(Outdir, "*_{}*.root".format(iin)))

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
            process_list = []
            if "SubProcess" in samples[iin]:
              for process in samples[iin]['SubProcess']:
                process_list.append(process)
            else:
              process_list.append(iin)


            for process in process_list:
              os.system('chmod +x {}/{}.sh'.format(farm_dir, 'merge_{}_{}_{}_{}'.format(Era, region, channel, process)))
              merge_shell[Era][region][channel][process] = open(os.path.join(farm_dir, 'merge_{}_{}_{}_{}.sh'.format(Era, region, channel, process)), 'a')
              merge_shell[Era][region][channel][process].write('\n')
              merge_shell[Era][region][channel][process].write('rm {}/*slim_*_{}_{}_{}_*_{}*.out\n'.format(farm_dir, Era, region, channel, process))
              merge_shell[Era][region][channel][process].write('rm {}/*slim_*_{}_{}_{}_*_{}*.err\n'.format(farm_dir, Era, region, channel, process))
              merge_shell[Era][region][channel][process].close()

  if not args.test:
    if args.check:
      if not Check_GreenLight:
        os.system('rm %s/resubmit.dag.*'%farm_dir)
        os.system('condor_submit_dag -f %s/resubmit.dag'%farm_dir)
    else:
      cprint("Submitting Jobs on Condor", "green")
      os.system('rm %s/workflow.dag.*'%farm_dir)
      os.system('condor_submit_dag -f %s/workflow.dag'%farm_dir)
