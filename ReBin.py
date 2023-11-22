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
from Util.General_Tool import MakeNuisance_Hist,MakePositive_Hist,CheckDir,CheckFile, binning, python_version
import argparse

def Make_Hist(prefix='', samples_list=[], nuis='', category='', indir='', q=False, bins='', year='2017', analysis_name="bH"):

  ## New definition of MakeNuisance_Hist, but compatible with current data structure

  Init = True
  Nui_Exist = False
  h = None

  for sample_ in samples_list:
    sample_nuis_name = str(prefix + nuis).replace('YEAR', year)
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
    nuis = nuis.replace("_up", "Up").replace("_down", "Down").replace('YEAR',year)
    h.SetNameTitle(analysis_name + year + "_" + category + nuis, year + "_" + category + nuis)
  else:
    if q: pass
    else: print("\033[0;32m Warning \033[0;m: {} doesn't exist".format(sample_nuis_name))
  return h

def ReBin(indir, fout_name, era, region, channel, unblind=False, POI='BDT', prefix_='', signal=None, quiet=False, analysis_name='bH'):

  fout = TFile.Open(fout_name, "RECREATE")

  ######################
  ##  Load json file  ##
  ######################

  sample_json = 'data_info/Sample_Names/process_name_{}.json'.format(era)
  datacard_json = 'data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json'.format(era,region,channel)

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
  samples["SIGNAL"] = [signal] # one signal for current stage
  for category in samples:
    # Nominal
    if category == "SIGNAL": category_name = signal
    else: category_name = category
    h = Make_Hist(prefix=POI, samples_list=samples[category], nuis='', category=category_name, indir=indir, bins=binning, year=era, q=quiet, analysis_name=analysis_name)
    Histograms.append(MakePositive_Hist(h))
    for nuisance in datacard_inputs["NuisForProc"]:
      if not datacard_inputs["UnclnN"][nuisance] == "shape": continue
      if not category in datacard_inputs["NuisForProc"][nuisance]: continue
      for variation in ["_up", "_down"]:
        h = Make_Hist(prefix=POI, samples_list=samples[category], nuis= str("_" + nuisance + variation), category=category_name, indir=indir, bins=binning, year = era, q=quiet, analysis_name=analysis_name)
        Histograms.append(MakePositive_Hist(h))

  ###############
  ##  unblind  ##
  ###############
  if unblind:
    jsonfile = open("data/sample_{}.json".format(era))
    if python_version == 2:
      samples_contain_datainfo = json.load(jsonfile, encoding='utf-8')
    else:
      samples_contain_datainfo = json.load(jsonfile)
    jsonfile.close()
    data_list = []
    for sample_ in samples_contain_datainfo:
      if not "Data" in samples_contain_datainfo[sample_]["Label"]: continue
      if "Region" in samples_contain_datainfo[sample_] and region not in samples_contain_datainfo[sample_]["Region"]: continue
      if "Channel" in samples_contain_datainfo[sample_] and channel not in samples_contain_datainfo[sample_]["Channel"]: continue
      data_list.append(sample_)
    print(data_list)
    h = Make_Hist(prefix=POI, samples_list=data_list, nuis='', category='data_obs', indir=indir, bins=binning, year=era, q=quiet, analysis_name=analysis_name)
    Histograms.append(h)

  fout.cd()
  for hist_ in Histograms:
    hist_.Write()
  fout.Close()
    


parser = argparse.ArgumentParser()

parser.add_argument('-y','--year',help='List of Years of data. Default value=["2016postapv"].',default=['2016postapv'],nargs='*')
parser.add_argument('--region', help='List of regions', default=['all'], nargs='+')
parser.add_argument('--channel', help='List of channels', default=['all'], nargs='+')
parser.add_argument('--signal', help='List of signals', default=['all'], nargs='+')
parser.add_argument('--outputdir',help="Output directory, normally, you do not need to modfiy this value.",default='./FinalInputs')
parser.add_argument('--inputdir',help="Input directory, normally, you don't need to modfiy this value.",default='/eos/cms/store/group/phys_top/ExtraYukawa/BDT/BDT_output')
parser.add_argument('--analysis_name', default='bH')
parser.add_argument('--unblind',action='store_true')
parser.add_argument('-q','--quiet',action='store_true')
parser.add_argument('--POI', default = 'BDT')
args = parser.parse_args()


if "all" in args.year:
  eras = ["2016postapv", "2016apv", "2017", "2018"]
else:
  eras = args.year

region_channel_dict = dict()
jsonfile = open("data/cut.json")
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

for era_ in eras:
  for region_ in region_channel_dict:
    for channel_ in region_channel_dict[region_]:
      signal_list = []
      if "all" in args.signal:
        jsonfile = open("data/sample_{}.json".format(era_))
        if python_version == 2: samples = json.load(jsonfile, encoding='utf-8')
        else: samples = json.load(jsonfile)
        for sample_ in samples:
          if "Signal" in samples[sample_]["Label"]: signal_list.append(sample_)
      else:
        signal_list = args.signal
      for signal_ in signal_list:
        inputdir = os.path.join(args.inputdir, era_, region_, channel_) # Rule for input directory
        fname = os.path.join(args.outputdir, era_, signal_, 'TMVApp_{}_{}.root'.format(region_, channel_))
        CheckDir(os.path.join(args.outputdir, era_, signal_), MakeDir=True)
        ReBin(inputdir, fname, era_, region_, channel_, unblind=args.unblind, POI=args.POI, signal=signal_, quiet=args.quiet, analysis_name=args.analysis_name)
                                        
