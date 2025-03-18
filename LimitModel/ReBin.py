'''
Algorithm: 
- get the file name
- get the histograms 
- create a new histogram, bkg_sum 
- use the fine binned histogram for this purpose, however during development, it is not availale, 
- loop over all the bins (from top to bottom). 
- if the event content is <7, sum its content with the neighbour (on left of the histogram), and increase the bin width by 1 unit
- check if the new integral is <7 or not, if <7 add the neighbouring bin on the left and increase the bin width by 1 unit
- keep repeating until the bin content is >=7 and save this bin width. 
- Use this new content and bin width to make the new shape and write it to a new file. 
- use them to get the limits, 
- repeat the whole process with 6, 7, 8, 9, 10 events and see what givess the best limits. 
'''

from ROOT import TH1F, TFile, TH1D 
import copy
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import json, array
from Util.General_Tool import MakeNuisance_Hist,MakePositive_Hist,CheckDir,CheckFile, python_version, read_json
import argparse
sys.path.append('../python')
from common import *
import numpy as np

def Make_Hist(prefix='', samples_list=[], nuis='', category='', indir='', q=False, bins='', era='2017', analysis_name="bH", channel='ele_resolved', region = 'CR_1b4j', scale = 1.0):

  ## New definition of MakeNuisance_Hist, but compatible with current data structure


  Init = True
  Nui_Exist = False
  h = None

  year = '2016' if '2016' in era else era

  for sample_ in samples_list:
    sample_nuis_name = str(prefix + nuis).replace('YEAR', year).replace('CHANNEL', channel).replace('ERA', era).replace('REGION', region)
    fin = os.path.join(indir, "{}.root".format(sample_))
    fin = TFile.Open(fin, "READ")
    if(type(fin.Get(sample_nuis_name)) is TH1F or type(fin.Get(sample_nuis_name)) is TH1D):
      if Init:
        h = copy.deepcopy(fin.Get(sample_nuis_name))
        Init = False
        Nui_Exist=True
      else:
        h.Add(fin.Get(sample_nuis_name))
    fin.Close()
  if Nui_Exist:
    h = h.Rebin(len(bins)-1, "h", bins)
    nuis = nuis.replace("_up", "Up").replace("_down", "Down").replace('YEAR',year).replace('CHANNEL', channel).replace("ERA", era).replace('REGION', region)
    h.SetNameTitle(analysis_name + era + "_" + category + nuis, era + "_" + category + nuis)
  else:
    if q: pass
    else: print("\033[0;32m Warning \033[0;m: {} doesn't exist".format(sample_nuis_name))

#  print('produce', analysis_name + era + "_" + category + nuis, era + "_" + category + nuis, indir, sample_)
  try:
    if h is None:
      print(f"Histogram not exisits. Category: {category}, sample: {sample_nuis_name}, {samples_list}, {indir}")
    h.Scale(scale)
  except:
    print(sample_nuis_name)
    raise

#  if category == 'QCD': 
#    Original_Yield = h.Integral()
#    h.Smooth(10) # QCD smooth
#    Smoothed_Yield = h.Integral()
#    norm = Original_Yield/Smoothed_Yield if Smoothed_Yield > 0 else 1.0
#    h.Scale(norm)
#    for bin_ in range(1, h.GetNbinsX() + 1):
#
#        # fix to 30% error
#        #new_error = 0.3*Histogram[sample_].GetBinContent(bin)
#        # fix to 50% error
#        new_error = 0.8*h.GetBinContent(bin_)
#        # Set the new error for the bin
#        h.SetBinError(bin_, new_error)

  return h

def ReBin(indir, fout_name, era, region, channel, unblind=False, POI='BDT', prefix_='', signal=None, quiet=False, analysis_name='bH', sig_scale=1.0, subprocess=[], binning = None, args=None, merge_channel = None, merge_era = None):

  fout = TFile.Open(fout_name, "RECREATE")
  ######################
  ##  Load json file  ##
  ######################
  #binning = [0.2 * i for i in range(6)] if binning is None else binning
  binning = [100 * i for i in range(11)] if binning is None else binning
  binning = array.array('d', binning)
  print(POI, binning)
  sample_json = 'data_info/Sample_Names/process_name_{}.json'.format(era)
  print(merge_era)
  if merge_era:
    sample_json = 'data_info/Sample_Names/process_name_{}.json'.format('2017')
  datacard_json = 'data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json'.format(era,region,channel)

  if merge_channel is not None:
      datacard_json_dict = dict()
      for channel_ in merge_channel:
          datacard_json_dict[channel_] =  read_json('data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json'.format(era,region,channel_))
  elif merge_era is not None:
      datacard_json_dict = dict()
      for era_ in era_list:
        datacard_json_dict[era_] =  read_json('data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json'.format(era_,region,channel))
  print(sample_json)
  jsonfile = open(sample_json)
  if python_version == 2:
    samples = json.load(jsonfile, encoding='utf-8')
  else:
    samples = json.load(jsonfile)
  jsonfile.close()


  jsonfile = open(datacard_json)
  if python_version == 2:
    datacard_inputs = json.load(jsonfile, encoding='utf-8')
  else:
    datacard_inputs = json.load(jsonfile)
  jsonfile.close()

  #############################
  ##  Merge Histogram (bkg)  ##
  #############################

  Histograms = []
  if (len(subprocess) == 0):
    samples["SIGNAL"] = [signal] # one signal, no subprocess
  else:
    for idx, subprocess_ in enumerate(subprocess):
      samples["SIGNAL{}".format(idx)] = [subprocess_]
  for category in samples:
    # Nominal
    scale = 1.0
    if "SIGNAL" in category:
      category_name = samples[category][0]
      scale = sig_scale[category_name] 
    else: category_name = category

    if merge_channel is not None:
        h_merge = None
        for channel_ in merge_channel:
             indir_tmp = os.path.join(indir, channel_)
             h = MakePositive_Hist(Make_Hist(prefix=POI, samples_list=samples[category], nuis='', category=category_name, indir=indir_tmp, bins=binning, era=era, q=quiet, analysis_name=analysis_name, channel=channel_, region=region, scale=scale))
             if h_merge is None: 
                 h_merge = h.Clone()
             else:
                 h_merge.Add(h.Clone())
        Histograms.append(h_merge)

        for nuisance in datacard_inputs["NuisForProc"]:
            if not datacard_inputs["UnclnN"][nuisance] == "shape": continue
            category_replace_signal = category
            if "SIGNAL" in category:
                category_replace_signal = "SIGNAL"
            if not category_replace_signal in datacard_inputs["NuisForProc"][nuisance]: continue
            for variation in ["_up", "_down"]:
                h_merge = None
                for channel_ in merge_channel:
                    indir_tmp = os.path.join(indir, channel_)
                    if nuisance not in datacard_json_dict[channel_]["UnclnN"]:
                        h = MakePositive_Hist(Make_Hist(prefix=POI, samples_list=samples[category], nuis='', category=category_name, indir=indir_tmp, bins=binning, era=era, q=quiet, analysis_name=analysis_name, channel=channel_, region=region, scale=scale))
                    else:
                        h = MakePositive_Hist(Make_Hist(prefix=POI, samples_list=samples[category], nuis= str("_" + nuisance + variation), category=category_name, indir=indir_tmp, bins=binning, era = era, q=quiet, analysis_name=analysis_name, channel=channel_, region = region, scale=scale))
                    if h_merge is None:
                        h_merge = h.Clone()
                    else:
                        h_merge.Add(h.Clone())
                 
                nuis = str("_" + nuisance + variation)
                year = '2016' if '2016' in era else era
                nuis = nuis.replace("_up", "Up").replace("_down", "Down").replace('YEAR',year).replace("ERA", era).replace('REGION', region)
                h_merge.SetNameTitle(analysis_name + era + "_" + category_name + nuis, era + "_" + category_name + nuis)
                Histograms.append(h_merge)
    elif merge_era is not None:
        print(era)
        h_merge = None
        for era_ in era_list:
             print(indir)
             indir_tmp = indir.replace('Merged_run2', era_)
             h = MakePositive_Hist(Make_Hist(prefix=POI, samples_list=samples[category], nuis='', category=category_name, indir=indir_tmp, bins=binning, era=era_, q=quiet, analysis_name=analysis_name, channel=channel, region=region, scale=scale))
             if h_merge is None: 
                 h_merge = h.Clone()
             else:
                 h_merge.Add(h.Clone())
        Histograms.append(h_merge)
        for nuisance in datacard_inputs["NuisForProc"]:
            if not datacard_inputs["UnclnN"][nuisance] == "shape": continue
            category_replace_signal = category
            if "SIGNAL" in category:
                category_replace_signal = "SIGNAL"
            if not category_replace_signal in datacard_inputs["NuisForProc"][nuisance]: continue
            for variation in ["_up", "_down"]:
                h_merge = None
                for era_ in era_list:
                    indir_tmp = indir.replace('Merged_run2', era_)
                    if nuisance not in datacard_json_dict[era_]["UnclnN"]:
                        h = MakePositive_Hist(Make_Hist(prefix=POI, samples_list=samples[category], nuis='', category=category_name, indir=indir_tmp, bins=binning, era=era_, q=quiet, analysis_name=analysis_name, channel=channel, region=region, scale=scale))
                    else:
                        h = MakePositive_Hist(Make_Hist(prefix=POI, samples_list=samples[category], nuis= str("_" + nuisance + variation), category=category_name, indir=indir_tmp, bins=binning, era = era_, q=quiet, analysis_name=analysis_name, channel=channel, region = region, scale=scale))
                    if h_merge is None:
                        h_merge = h.Clone()
                    else:
                        h_merge.Add(h.Clone())
                nuis = str("_" + nuisance + variation)
                year = '2016' if '2016' in era else era
                nuis = nuis.replace("_up", "Up").replace("_down", "Down").replace('YEAR',year).replace("ERA", era).replace('REGION', region)
                h_merge.SetNameTitle(analysis_name + era + "_" + category_name + nuis, era + "_" + category_name + nuis)
                Histograms.append(h_merge)
       
    else:
        h = Make_Hist(prefix=POI, samples_list=samples[category], nuis='', category=category_name, indir=indir, bins=binning, era=era, q=quiet, analysis_name=analysis_name, channel=channel, region=region, scale=scale)
        #    Histograms.append(over_flowbin(MakePositive_Hist(h)))
        Histograms.append(MakePositive_Hist(h))
        for nuisance in datacard_inputs["NuisForProc"]:
            if not datacard_inputs["UnclnN"][nuisance] == "shape": continue
            category_replace_signal = category
            if "SIGNAL" in category:
                category_replace_signal = "SIGNAL"
            if not category_replace_signal in datacard_inputs["NuisForProc"][nuisance]: continue
            for variation in ["_up", "_down"]:
                h = Make_Hist(prefix=POI, samples_list=samples[category], nuis= str("_" + nuisance + variation), category=category_name, indir=indir, bins=binning, era = era, q=quiet, analysis_name=analysis_name, channel=channel, region = region, scale=scale)
        #        Histograms.append(over_flowbin(MakePositive_Hist(h)))
                Histograms.append(MakePositive_Hist(h))

  ###############
  ##  unblind  ##
  ###############
  if unblind:
    jsonfile = open(args.sample_json)
    if python_version == 2:
      samples_contain_datainfo = json.load(jsonfile, encoding='utf-8')
    else:
      samples_contain_datainfo = json.load(jsonfile)
    jsonfile.close()


    if merge_channel is not None:

        h_merge = None
        for channel_ in merge_channel:
            data_list = []
            indir_tmp = os.path.join(indir, channel_)
            for sample_ in samples_contain_datainfo:
                if not "Data" in samples_contain_datainfo[sample_]["Label"]: continue
                if "Region" in samples_contain_datainfo[sample_] and region not in samples_contain_datainfo[sample_]["Region"]: continue
                if "Channel" in samples_contain_datainfo[sample_] and channel_ not in samples_contain_datainfo[sample_]["Channel"]: continue
                if "Era" in samples_contain_datainfo[sample_] and era not in samples_contain_datainfo[sample_]["Era"]: continue
                data_list.append(sample_)

            h = Make_Hist(prefix=POI, samples_list=data_list, nuis='', category='data_obs', indir=indir_tmp, bins=binning, era=era, q=quiet, analysis_name=analysis_name, channel=channel_, region = region)
            if h_merge is None:
                h_merge = h.Clone()
            else:
                h_merge.Add(h.Clone())
        Histograms.append(h_merge)
    elif merge_era is not None:
        h_merge = None
        for era_ in era_list:
            data_list = []
            indir_tmp = indir.replace('Merged_run2', era_)
            for sample_ in samples_contain_datainfo:
                if not "Data" in samples_contain_datainfo[sample_]["Label"]: continue
                if "Region" in samples_contain_datainfo[sample_] and region not in samples_contain_datainfo[sample_]["Region"]: continue
                if "Channel" in samples_contain_datainfo[sample_] and channel not in samples_contain_datainfo[sample_]["Channel"]: continue
                if "Era" in samples_contain_datainfo[sample_] and era_ not in samples_contain_datainfo[sample_]["Era"]: continue
                data_list.append(sample_)

            h = Make_Hist(prefix=POI, samples_list=data_list, nuis='', category='data_obs', indir=indir_tmp, bins=binning, era=era_, q=quiet, analysis_name=analysis_name, channel=channel, region = region)
            if h_merge is None:
                h_merge = h.Clone()
            else:
                h_merge.Add(h.Clone())
        Histograms.append(h_merge)   
    else:
        data_list = []
        for sample_ in samples_contain_datainfo:
            if not "Data" in samples_contain_datainfo[sample_]["Label"]: continue
            if "Region" in samples_contain_datainfo[sample_] and region not in samples_contain_datainfo[sample_]["Region"]: continue
            if "Channel" in samples_contain_datainfo[sample_] and channel not in samples_contain_datainfo[sample_]["Channel"]: continue
            if "Era" in samples_contain_datainfo[sample_] and era not in samples_contain_datainfo[sample_]["Era"]: continue
            data_list.append(sample_)

        h = Make_Hist(prefix=POI, samples_list=data_list, nuis='', category='data_obs', indir=indir, bins=binning, era=era, q=quiet, analysis_name=analysis_name, channel=channel, region = region)
        Histograms.append(h)

  fout.cd()
  for hist_ in Histograms:
    hist_.Write()
  fout.Close()
    


parser = argparse.ArgumentParser()

parser.add_argument('-y','--era',help='List of Years of data. Default value=["2016postapv"].',default=['2016postapv'],nargs='*')
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
parser.add_argument('--ch_merge',  action = 'store_true')
parser.add_argument('--era_merge',  action = 'store_true')
parser.add_argument('--randomized_scan', action = 'store_true')
args = parser.parse_args()

args.outputdir = os.path.join(args.outputdir, 'FinalInputs')

if "all" in args.era and not args.era_merge:
  eras = ["2016postapv", "2016apv", "2017", "2018"]
elif args.era_merge:
  eras = ['Merged_run2']
  era_list = ["2016postapv", "2016apv", "2017", "2018"]
else:
  eras = args.era

region_channel_dict = dict()
jsonfile = open(args.cut_json)
if python_version == 2:
  regions = json.load(jsonfile, encoding='utf-8')
else:
  regions = json.load(jsonfile)

if "all" in args.region:
  for region_ in regions:
    region_channel_dict[region_] = []
else:
  for region_ in args.region:
    region_channel_dict[region_] = []

if "all" in args.channel:
  for region_ in region_channel_dict:
    for channel_ in regions[region_]["channel_cut"]:
      region_channel_dict[region_].append(channel_)
else:
  for region_ in region_channel_dict:
    region_channel_dict[region_] = args.channel

jsonfile = open(args.sample_json)
if python_version == 2: samples = json.load(jsonfile, encoding='utf-8')
else: samples = json.load(jsonfile)
samples = Extend_sample_dict(samples, key_word = 'MASS')


for era_ in eras:
  for region_ in region_channel_dict:
      signal_list = []
      all_signal_list = []
      for sample_ in samples:
        if "Signal" in samples[sample_]["Label"]:
            if args.randomized_scan:
                if "Randomized_Scan" in samples[sample_]["Label"]:
                    signal_list.append(sample_)
                    all_signal_list.append(sample_)
            else:
                signal_list.append(sample_)
                all_signal_list.append(sample_)
      if not "all" in args.signal:
        signal_list = args.signal
      for signal_ in signal_list:
        CheckDir(os.path.join(args.outputdir, era_, signal_), True)
        #########  Specific Rule ###########
#        if('BGToTH' in signal_): continue


        POI_binning = None
        if args.POI == "ASCUTJSON":
          POI_name = regions[region_]["POI"][0]
          if "POI_bin" in regions[region_]:
              POI_binning_min, POI_binning_max, POI_binning_nbin = regions[region_]["POI_bin"]["Normal"]
              POI_binning = np.linspace(POI_binning_min, POI_binning_max, POI_binning_nbin+1)
          else:
              POI_binning = np.array(regions[region_]["POI_binnings"]["Normal"])
        else:
          POI_name = args.POI


        POI_in = POI_name
        if POI_name == 'BDT':
            POI_in = signal_.replace('BGToTH', 'CGToBH') # Case by case naming rule
        if POI_name == 'DNN':
            if 'CGToBH' in signal_:
                mass = signal_.split('_')[2]
            else:
                mass = signal_.replace('BGToTHpm_a_', '').replace('CGToBHpm_a_','').replace('_rtt06_rtc04','').replace('WprimeTotb_leptonicDecays_M_','').replace('HplusToTB_M_','')
            POI_in = 'DNN{}'.format(mass)
        if POI_name == 'DNNScore':
            mass     = signal_.replace('BGToTHpm_a_', '').replace('CGToBHpm_a_','').replace('_rtt06_rtc04','').replace('WprimeTotb_leptonicDecays_M_','').replace('HplusToTB_M_','')
            POI_in = 'DNNScore{}'.format(mass)

        #### Special Case ######
        if "POI_binnings" in regions[region_] and POI_in in regions[region_]["POI_binnings"]:
           POI_binning = np.array(regions[region_]["POI_binnings"][POI_in])


        sig_scale = dict()
        for signal_in_loop in all_signal_list:
            if args.sig_norm:
              sig_scale[signal_in_loop] = 1./samples[signal_in_loop]["xsec"]
            else:
              sig_scale[signal_in_loop] = 1.0
        subprocess = []
        print(all_signal_list)
        for signal_in_loop in all_signal_list:
          if "SubProcess" in samples[signal_in_loop]:
            for process in samples[signal_in_loop]["SubProcess"]:
              subprocess.append(process)
              if args.sig_norm:
                  sig_scale[process] =  1./samples[signal_in_loop]["xsec"]
              else:
                  sig_scale[process] = 1.0
        print(subprocess)
        print(era_)
        if not args.ch_merge:
          for channel_ in region_channel_dict[region_]:
            inputdir = os.path.join(args.inputdir, era_, region_, channel_) # Rule for input directory
            fname = os.path.join(args.outputdir, era_, signal_, 'TMVApp_{}_{}.root'.format(region_, channel_))
            ReBin(inputdir, fname, era_, region_, channel_, unblind=args.unblind, POI=POI_in, signal=signal_, quiet=args.quiet, analysis_name=args.analysis_name, sig_scale=sig_scale, subprocess=subprocess, binning = POI_binning, args=args, merge_era=args.era_merge)
        else:
            inputdir = os.path.join(args.inputdir, era_, region_)
            fname = os.path.join(args.outputdir, era_, signal_, 'TMVApp_{}_{}.root'.format(region_, 'ch_merged_resolved'))
            ReBin(inputdir, fname, era_, region_, "ch_merged_resolved", unblind=args.unblind, POI=POI_in, signal=signal_, quiet=args.quiet, analysis_name=args.analysis_name, sig_scale=sig_scale, subprocess=subprocess, binning = POI_binning, args=args, merge_channel = region_channel_dict[region_])
                                        
