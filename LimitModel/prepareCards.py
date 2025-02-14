import CombineHarvester.CombineTools.ch as ch
import ROOT
import json
import sys, os
import argparse
from collections import OrderedDict
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)
from Util.General_Tool import CheckDir, python_version, read_json
sys.path.append('../python')
from common import *
import copy

def set_Rate(p, rate=-1):
  if rate==-1:
    p.set_rate(int(rate))
  else:
    p.set_rate(rate)

def compare_two_list(l1, l2):
  if not len(l1) == len(l2): return False
  for idx in range(len(l1)):
    if not l1[idx] in l2: return False
  return True

def create_datacards(years, regions, channels, signal, combined, outdir, analysis_name="bH", dataset_dir='', signal_process = [], PhysicsModel='g2HDM_2Bbased', cut_json = '../data/cut.json', create_WorkSpace = False, randomized_scan = False):


  # List of Years
  if 'all' in years:
    years = ['2016apv', '2016postapv', '2017', '2018']
  
  # List of regions
  region_channel_dict = dict()
  cut_regions = read_json(cut_json)
  if 'all' in regions:
    for region_ in cut_regions:
      region_channel_dict[region_] = []
  else:
    for region_ in regions:
      region_channel_dict[region_] = []

  # List of channels
  for region_ in region_channel_dict:
    if 'all' in channels:
      for channel_ in cut_regions[region_]["channel_cut"]:
        region_channel_dict[region_].append(channel_)
    else:
      region_channel_dict[region_] = copy.deepcopy(channels)

  # Check if all region shares same channels
  shared_channel = True
  ref_list = None
  for idx, region_ in enumerate(region_channel_dict):
    if idx == 0:
      ref_list = region_channel_dict[region_]
    elif shared_channel:
      shared_channel = compare_two_list(ref_list, region_channel_dict[region_])
  
  signal_directory_name = '_'.join(signal.split('_')[:3]) if randomized_scan else signal # Hard coded

  ####################
  ## Write datacard ##
  ####################

  for era in years:
    for region in region_channel_dict:
      for channel in region_channel_dict[region]:
        parameter_constraint = dict()
        year = '2016' if '2016' in era else era
        cb = ch.CombineHarvester()
        Datacards_Input = read_json("data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json".format(era, region, channel))
        # Add background
        bkg_list = []
        for process in Datacards_Input["Process"]:
          if process == "SIGNAL": continue
          bkg_list.append(str(process))
        sig_list = signal_process
        cb.AddProcesses(["*"], [analysis_name], [era], [str(channel)], bkg_list, [(1,str(region + "_" + channel))], False)
        # Add signal
        cb.AddProcesses(["*"], [analysis_name], [era], [str(channel)], sig_list, [(1,str(region + "_" + channel))], True)
        # Add observable
        cb.AddObservations(["*"], [analysis_name], [era], [str(channel)], [(1,str(region + "_" + channel))])
        # Add systematic
        for nuisance in Datacards_Input["UnclnN"]:
          process_list = []
          for process in Datacards_Input["NuisForProc"][nuisance]:
            if process == 'SIGNAL':
              for sig_ in sig_list:
                process_list.append(sig_)
            else:
              process_list.append(process)
          if Datacards_Input["UnclnN"][nuisance] == 'shape':
            cb.cp().process(process_list).AddSyst(cb, str(nuisance), "shape", ch.SystMap()(1.0))
          else:
            cb.cp().process(process_list).AddSyst(cb, str(nuisance), "lnN",  ch.SystMap()(float(Datacards_Input["UnclnN"][nuisance])))

        if "FreeFloat" in Datacards_Input:
            for ff_process in Datacards_Input["FreeFloat"]:
                cb.cp().bin([str(region + "_" + channel)]).process([ff_process]).AddSyst(cb, str("scale_" + ff_process + "_" + era + "_" + region + "_" + channel), "rateParam", ch.SystMap()(1.0))
                #cb.cp().bin([str(region + "_" + channel)]).process([ff_process]).AddSyst(cb, str("scale_" + ff_process), "rateParam", ch.SystMap()(1.0))
                parameter_constraint[str("scale_" + ff_process + "_" + era + "_" + region + "_" + channel)] = [0.0, 20.0]
                #parameter_constraint[str("scale_" + ff_process)] = [0.0, 20.0]
        # Set Rate
        cb.ForEachProc(set_Rate)
        cb.ForEachObs(set_Rate)
        # Set AutoMCStats
        cb.SetAutoMCStats(cb, 10.0, False, 1)
        # Output datacard
        outdir_ = os.path.join(outdir, era, signal)
        CheckDir(outdir_, True)
        output_datacard_txt = os.path.join(outdir_, '{}_{}_{}_{}'.format(signal, era, region, channel) + ".txt")
        cb.cp().WriteDatacard(str(output_datacard_txt))
        with open(output_datacard_txt, "r") as file:
            lines = file.readlines()
        with open(output_datacard_txt, "w") as file:
            for line in lines:
            # Check if the line defines a rateParam
              for param_ in parameter_constraint:
              # Add the bounds to the line
                if param_ in line:
                  line = line.strip() + f" [0,20]\n"
              file.write(line)
        # Specify systematic histogram naming rule
        dataset_dir_v = dataset_dir.replace('/','\/')
        os.system('sed -i "s/FAKE/%s\/FinalInputs\/%s\/%s\/TMVApp\_%s\_%s.root %s%s\_\$PROCESS %s%s\_\$PROCESS\_\$SYSTEMATIC/g"  %s'%(dataset_dir_v, era, signal_directory_name, region, channel, analysis_name, era, analysis_name, era, output_datacard_txt))
        # Replace template setting
        os.system('sed -i "s/ERA/%s/g" %s'%(era, output_datacard_txt))
        os.system('sed -i "s/YEAR/%s/g" %s'%(year, output_datacard_txt))
        os.system('sed -i "s/CHANNEL/%s/g" %s'%(channel, output_datacard_txt))
        os.system('sed -i "s/REGION/%s/g" %s'%(region, output_datacard_txt))
        os.system('sed -i "s/observation  -1.0/observation  -1/g" %s'%(output_datacard_txt)) #TODO 
        print("\033[0;32m info \033[0;m: create datacard: %s"%(output_datacard_txt)) 
        if create_WorkSpace:
          os.system('text2workspace.py -P HiggsAnalysis.CombinedLimit.g2HDM:{} {} -o {}'.format(PhysicsModel, output_datacard_txt, output_datacard_txt.replace('txt','root')))


  ##############
  ## Combined ##
  ##############

  if not combined: return 0
  else:
    region_tmp = None
    # Combine channel
    for era in years:
      for region in region_channel_dict:
        outdir_ = os.path.join(outdir, era, signal)
        CheckDir(outdir_)
        output_datacard_txt = '{}_{}_{}_C'.format(signal, era, region) + ".txt"
        merge_command = 'cd {}; combineCards.py '.format(outdir_)
        for channel in region_channel_dict[region]:
          merge_command += '{}={} '.format(channel, '{}_{}_{}_{}.txt'.format(signal, era, region, channel))
        merge_command += ' > {}'.format(output_datacard_txt)
        print("\033[0;32m info \033[0;m: create datacard: %s"%(os.path.join(outdir_, output_datacard_txt)))
        os.system(merge_command)
        if create_WorkSpace:
          os.system('cd {}; text2workspace.py -P HiggsAnalysis.CombinedLimit.g2HDM:{} {} -o {}'.format(outdir_, PhysicsModel, output_datacard_txt, output_datacard_txt.replace('txt','root')))
        region_tmp = region
      # Combine region
      if shared_channel:
        channel_list = copy.deepcopy(region_channel_dict[region_tmp])
        channel_list.append('C')
      else:
        channel_list = ['C']
      for channel in channel_list:
        outdir_ = os.path.join(outdir, era, signal)
        CheckDir(outdir_)
        output_datacard_txt = '{}_{}_C_{}'.format(signal, era, channel) + '.txt'
        merge_command = 'cd {}; combineCards.py '.format(outdir_)
        for region in region_channel_dict:
          merge_command += '{}={} '.format(region, '{}_{}_{}_{}.txt'.format(signal, era, region, channel))
        merge_command += ' > {}'.format(output_datacard_txt)
        print("\033[0;32m info \033[0;m: create datacard: %s"%(os.path.join(outdir_,output_datacard_txt)))
        os.system(merge_command)
        if create_WorkSpace:
          os.system('cd {}; text2workspace.py -P HiggsAnalysis.CombinedLimit.g2HDM:{} {} -o {}'.format(outdir_, PhysicsModel, output_datacard_txt, output_datacard_txt.replace('txt','root')))

    # Combine era
    for region in region_channel_dict:
      region_channel_dict[region].append('C')
    region_channel_dict['C'] = channel_list #TODO better coding

    outdir_ = os.path.join(outdir, 'run2', signal)
    CheckDir(outdir_)
    for region in region_channel_dict:
      for channel in region_channel_dict[region]:
        output_datacard_txt = '{}_run2_{}_{}'.format(signal, region, channel) + '.txt'
        merge_command = 'cd {}; '.format(outdir_)
        for era in years:
          merge_command += 'cp ../../{}/{}/{} {};'.format(era, signal, output_datacard_txt.replace('run2',era), output_datacard_txt.replace('run2',era))
        merge_command += 'combineCards.py '
        for era in years:
          merge_command += 'era{}={} '.format(era, '{}_{}_{}_{}.txt'.format(signal, era, region, channel))
        merge_command += ' >{};'.format(output_datacard_txt)
        for era in years:
          merge_command += 'rm {}; '.format(output_datacard_txt.replace('run2', era))
        print("\033[0;32m info \033[0;m: create datacard: %s"%(os.path.join(outdir_, output_datacard_txt)))
        print(merge_command)
        os.system(merge_command)
        if create_WorkSpace:
            os.system('cd {}; text2workspace.py -P HiggsAnalysis.CombinedLimit.g2HDM:{} {} -o {}'.format(outdir_, PhysicsModel, output_datacard_txt, output_datacard_txt.replace('txt','root')))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--year', help='List of years', default=['2017'], nargs='+')
  parser.add_argument('--region', help='List of regions', default = ['all'], nargs='+')
  parser.add_argument('--channel', help='List of channels', default = ['all'], nargs='+')
  parser.add_argument('--combined', action='store_true')
  parser.add_argument('--signal_template', default = 'CGToBHpm_a_MASS_RTT_RTC', type = str)
  parser.add_argument('--mass', help="List of mass", default=[200, 300, 350, 400, 500, 600, 700, 800, 900, 1000], nargs='+')
  parser.add_argument('--rtt',  help="List of rtt coupling values", default = ["rtt06"], nargs = '+')
  parser.add_argument('--rtc',  help="List of rtc coupling values", default = ["rtc04"], nargs = '+')
  parser.add_argument('--signal', help='List of signals', default=None, nargs='+')
  parser.add_argument('--dataset_dir', help='dataset_dir', default='.')
  parser.add_argument('--outdir', help='output directory', default='./')
  parser.add_argument('--analysis_name', help='analysis_name', default='bH')
  parser.add_argument('--PhysicsModel', help='Physics model name', default='g2HDM_3Bbased')
  parser.add_argument('--create_WorkSpace', action = 'store_true')
  parser.add_argument('--cut_json', default='../data/cut.json')
  parser.add_argument('--merge', action = 'store_true')
  parser.add_argument('--randomized_scan', action = 'store_true')
  args = parser.parse_args()
  CheckDir(args.outdir, True)


  if args.merge: 
      args.channel = ["merged_resolved"]

  args.outdir = os.path.join(args.outdir, 'datacards_{}'.format(args.PhysicsModel))

  jsonfile = open("../data/sample.json")
  if python_version == 2: samples = json.load(jsonfile, encoding='utf-8')
  else: samples = json.load(jsonfile)
  samples = Extend_sample_dict(samples, key_word = 'MASS')

  # Method 1: directly give signals
  if args.signal is not None: 
    if 'all' in args.signal:
      signal_list = []
      for sample_ in samples:
        if "Signal" in samples[sample_]["Label"]: signal_list.append(sample_)
      args.signal = signal_list
    for signal_ in args.signal:
      create_datacards(args.year, args.region, args.channel, signal_, args.combined, args.outdir, args.analysis_name, args.dataset_dir, PhysicsModel=args.PhysicsModel, cut_json = args.cut_json, create_WorkSpace = args.create_WorkSpace)

  # Method 2(specific to bHplus study): give lists of masses and coupling(TODO)
  else:
    for mass_ in args.mass:
      for rtt_ in args.rtt:
        for rtc_ in args.rtc:
          signal_name = args.signal_template.replace("MASS", mass_).replace("RTT", rtt_).replace("RTC", rtc_)
          subprocess = []
          if signal_name in samples:
            if "SubProcess" in samples[signal_name]:
              for subprocess_ in samples[signal_name]["SubProcess"]:
                subprocess.append(subprocess_)
            else:
              subprocess.append(signal_name)
          else:
            subprocess.append(signal_name)
          create_datacards(args.year, args.region, args.channel, signal_name, args.combined, args.outdir, args.analysis_name, args.dataset_dir, signal_process = subprocess, PhysicsModel=args.PhysicsModel, cut_json=args.cut_json, create_WorkSpace = args.create_WorkSpace, randomized_scan = args.randomized_scan)
