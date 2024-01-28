import ROOT
import time
import os, sys
import math
import json
import optparse, argparse
from collections import OrderedDict
from math import sqrt
from common import inputFile_path


def Slim_module(filein,
                era,
                output_dir,
                channel = "ele",
                Labels=["Normal"],
                Black_list=[],
                POIs=[],
                sample_labels = [],
                weight_def="puWeight*genWeight*L1PreFiringWeight_Nom/abs(genWeight)*Trigger_sf",
                scale = 1.0,
                sample_json = "../../data/sample.json",
                nuisance_json = "../../data/nuisance.json",
                variable_json = "../../data/variable.json",
                cut_json = "../../data/cut.json",
                trigger_json = "../../data/trigger.json",
                MET_filter_json = "../../data/MET_filter.json",
                histogram_json = "../../data/histogram.json",
                region="signal_region",
                Btag_WP="Medium",
                start = -1,
                end   = -1,
                index = -1):

  ###################
  ##  Sample type  ##
  ###################
  sample_type = "Data" if "Data" in sample_labels else "MC"

  ###################
  ## Load Function ##
  ###################

  ROOT.gSystem.Load("libGenVector.so")
  header_path = os.path.join("script/slim_" + era + ".h")
  ROOT.gInterpreter.Declare('#include "{}"'.format(header_path))

  #################
  ##  Load File  ##
  #################

  path    = str(inputFile_path[era])
  fin     = os.path.join(path, filein)
  if not index == -1:
    fileOut = os.path.join(output_dir, str(index) + "_" + filein)
  else:
    fileOut = os.path.join(output_dir, filein) 
  treeOut = "SlimTree"

  if not os.path.isdir(output_dir):
    os.system("mkdir -p " + output_dir)

  jsonfile = open(sample_json)
  samples = json.load(jsonfile, object_pairs_hook=OrderedDict)
  jsonfile.close()

  for sample in samples:
    if (((sample + ".") in filein) or ((sample + "_") in filein)):
      sample_name = sample

  ###########################
  ## Channel/Region filter ##
  ###########################
  if "Region" in samples[sample_name] and region not in samples[sample_name]["Region"]:
    print("Do not satisfied region criteria. sample_name: {}, region: {}".format(sample_name, region))
    return
  if "Channel" in samples[sample_name] and channel not in samples[sample_name]["Channel"]:
    print("Do not satisfied channel criteria. sample_name: {}, channel: {}".format(sample_name, channel))
    return
  #sample_name = filein.replace('.root', '').replace('-','')

  ##################
  ##  RDataFrame  ##
  ##################

  df_a   = ROOT.RDataFrame("Events", fin)
  if not start == -1:
    df = df_a.Range(start, end)
  else:
    df = df_a
  print(fin, start, end)
  BranchList = df.GetColumnNames()

  #######################
  ##  Define Nuisance  ##
  #######################

  jsonfile = open(nuisance_json)
  nuisances = json.load(jsonfile, object_pairs_hook=OrderedDict)
  jsonfile.close()
  nuisances_valid = dict()
  nuisance_list   = []
  for nuisance in nuisances:
    Flag = True
    for Label in sample_labels:
      if not(Label in nuisances[nuisance]["Label"]): Flag = False
    if not Flag: continue
    if nuisances[nuisance]["Nominal"][-1] not in nuisances_valid:
      nuisances_valid[nuisances[nuisance]["Nominal"][-1]] = [nuisance]
    else:
      nuisances_valid[nuisances[nuisance]["Nominal"][-1]].append(nuisance)

  #######################
  ##  Define Variable  ##
  #######################

  jsonfile  = open(variable_json)
  variables = json.load(jsonfile, object_pairs_hook=OrderedDict)
  jsonfile.close()
  
  print('nuisances_valid', nuisances_valid)
  for variable in variables:

    Flag = False
    for Label in Labels:
      if Label in variables[variable]["Label"]: Flag = True
    for Label in Black_list:
      if Label in variables[variable]["Label"]: Flag = False
    Flag = True
    if not Flag: continue
    if "Data" in sample_labels and "MC" in variables[variable]["Label"]: continue

    if not (variables[variable]["Def"] == "Defined"):
      if(variables[variable]["Def"] == "MC_Data_Dep"):
        df = df.Define(str(variable), str(variables[variable]["Category"][sample_type]))
      elif(variables[variable]["Def"] == "Channel_Dep"):
        df = df.Define(str(variable), str(variables[variable]["Category"][channel]))
      elif(variables[variable]["Def"] == "Btag_WP_Dep"):
        df = df.Define(str(variable), str(variables[variable]["Category"][Btag_WP]))
      else:
        df = df.Define(str(variable), str(variables[variable]["Def"]))
    if variable in nuisances_valid:
      for nuisance in nuisances_valid[variable]:
        if "Era" in nuisances[nuisance] and era not in nuisances[nuisance]["Era"]: continue
        if "Region" in nuisances[nuisance] and region not in nuisances[nuisance]["Region"]: continue
        if "Channel" in nuisances[nuisance] and channel not in nuisances[nuisance]["Channel"]: continue
        sub_category = [""]
        if "sub_cat" in nuisances[nuisance]: sub_category = nuisances[nuisance]["sub_cat"]
        for sub_cat in sub_category:
          nuisance_def =  nuisances[nuisance]["Def"].replace('SUB', sub_cat).replace('YEAR', era)
          nuisance_name = nuisance+sub_cat.replace('YEAR', era).replace('CHANNEL', channel)
          print(nuisances[nuisance]["Nominal"], nuisance_def, nuisance_name)
          df = df.Vary(nuisances[nuisance]["Nominal"], nuisance_def, {"Down", "Up"}, nuisance_name)
          nuisance_list.append(nuisance_name)
  ##############
  ##  Weight  ##
  ##############
  if "Data" in sample_labels:
    weight_def = 1       # Data weight is also to be 1
    nuisances_valid = [] # Nuisances only affect MC
  df = df.Define("weight", str(weight_def))

  #########
  ## Cut ##
  #########

  cutflow = OrderedDict()

  jsonfile = open(cut_json)
  cuts  = json.load(jsonfile, object_pairs_hook=OrderedDict)
  jsonfile.close()

  jsonfile = open(trigger_json)
  triggers = json.load(jsonfile, object_pairs_hook=OrderedDict)
  jsonfile.close()

  jsonfile = open(MET_filter_json)
  MET_filters = json.load(jsonfile, object_pairs_hook=OrderedDict)
  jsonfile.close()

  # channel cut
  for cut_name in cuts[region]["channel_cut"][channel]:
    df = df.Filter(str(cuts[region]["channel_cut"][channel][cut_name]), str(cut_name))
  cutflow["channel"] = df.Sum("weight").GetValue()
  # trigger cut
  for trigger_name in triggers:
    if not channel in triggers[trigger_name]["Channel"]: continue
    if "Data" in sample_labels and not sample_name in triggers[trigger_name]["Dataset"]: continue
    trigger_set = []
    for trigger_ in triggers[trigger_name]['Triggers'][era]:
        if trigger_ in BranchList:
            trigger_set.append(trigger_)
    df = df.Define(str(trigger_name), str('||'.join(trigger_set)))
    df = df.Filter(str(trigger_name), str(trigger_name))
    print(trigger_name, str('||'.join(trigger_set)))
  cutflow[trigger_name] = df.Sum("weight").GetValue() 
  # general cut
  for cut_name in cuts[region]["general_cut"]:
    df = df.Filter(str(cuts[region]["general_cut"][cut_name]), str(cut_name))
    cutflow[cut_name] = df.Sum("weight").GetValue()

  # METFilter cut
  MET_filter_cut = []
  for MET_filter in MET_filters["MET_Filter"]:
    if MET_filter in BranchList:
      MET_filter_cut.append(MET_filter)
  MET_filter_cut = ' && '.join(MET_filter_cut)
  print('MET filter',  MET_filter_cut)
  df = df.Filter(str(MET_filter_cut), 'MET_filter')
  cutflow['MET_filter'] = df.Sum("weight").GetValue()

  print(cutflow)

  #################
  ##  Histogram  ##
  #################

  Histos     = []
  jsonfile   = open(histogram_json)
  Histograms = json.load(jsonfile, object_pairs_hook=OrderedDict)
  jsonfile.close()

  for Histogram in Histograms:
    print("Generating", Histogram)
    Flag = False
    Label_trigger = ""
    for Label in Labels:
      if Label in Histograms[Histogram]["Label"]: Flag = True
    for Label in Black_list:
      if Label in Histograms[Histogram]["Label"]:
        Label_trigger = Label
        Flag = False
    if not Flag:
      print("Label do not satisfied the requirement. Black list label triggered:%s"%Label_trigger)
      continue

    Title  = str(Histograms[Histogram]["Title"])
    xlow   = Histograms[Histogram]["xlow"]
    xhigh  = Histograms[Histogram]["xhigh"]
    nbin   = Histograms[Histogram]["nbin"] * 600 # will be rebinned when plotting
    df_histo = df.Histo1D((str(Histogram), Title, nbin, xlow, xhigh), str(Histogram), "weight")
    Histos.append(df_histo.GetValue().Clone())

    ## Nuisance variation for POIs
    if Histogram in POIs:
      h_variation = ROOT.RDF.Experimental.VariationsFor(df_histo)
      print(h_variation.GetKeys())
      for nuisance in nuisance_list:
        if ("{}:Down".format(nuisance) not in h_variation.GetKeys()): continue
        h_variation_do = h_variation[nuisance + ":Down"].Clone()
        h_variation_do.SetName(str((Histogram + "_" + nuisance + "_down").replace("YEAR",era)))
        h_variation_up = h_variation[nuisance + ":Up"].Clone()
        h_variation_up.SetName(str((Histogram + "_" + nuisance + "_up").replace("YEAR", era)))
        Histos.append(h_variation_do)
        Histos.append(h_variation_up)

  # Cutflow Histogram
  histo_cutflow = ROOT.TH1D('cutflow', ';;nEvents', len(cutflow), 0, len(cutflow))
  for idx, cut_name in enumerate(cutflow):
    histo_cutflow.SetBinContent(idx+1, cutflow[cut_name])
    histo_cutflow.GetXaxis().SetBinLabel(idx + 1, str(cut_name))
  Histos.append(histo_cutflow.Clone())

  ######################
  ##  Store Variable  ##
  ######################

  columns = ROOT.std.vector("string")()

  for variable in variables:

    Flag = False
    for Label in Labels:
      if "Save" in variables[variable] and Label in variables[variable]["Save"]: Flag = True
    if not Flag: continue
    columns.push_back(str(variable))

  df.Snapshot(treeOut, fileOut, columns)

  #######################
  ##  Store Histogram  ##
  #######################
  
  FileOut = ROOT.TFile.Open(fileOut, "Update")
  FileOut.cd()
  for ij in range(0, len(Histos)):
    h = Histos[ij].Clone()
    if not "Data" in sample_labels:
      h.Scale(scale) # Lumi x xSec / nDAS (input from runCondor)
    h.Write()
  FileOut.Close()


if __name__ == "__main__":

  usage  = 'usage: %prog [options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('-e', '--era',    dest='era', help='[2016apv/2016postapv/2017/2018]', default='2018', type=str)
  parser.add_argument('-i', '--iin',    dest='iin', help='input file name', default=None, type=str)
  parser.add_argument('-o', '--outdir', dest='out', help='ouput directory', default='./', type=str)
  parser.add_argument('--start',        dest='start', default=-1, type=int)
  parser.add_argument('--end',          dest='end',   default=-1, type=int)
  parser.add_argument('--index',        dest='index', default=-1, type=int)
  parser.add_argument('--sample_json',  dest='sample_json', default='../../data/sample.json', type=str)
  parser.add_argument('--cut_json',     dest='cut_json', default='../../data/cut.json', type=str)
  parser.add_argument('--variable_json',dest='variable_json', default='../../data/variable.json', type=str)
  parser.add_argument('--histogram_json', dest='histogram_json', default='../../data/histogram.json', type=str)
  parser.add_argument('--trigger_json', dest='trigger_json', default='../../data/trigger.json', type=str)
  parser.add_argument('--MET_filter_json', dest='MET_filter_json', default='../../data/MET_filter.json', type=str)
  parser.add_argument('--nuisance_json', dest='nuisance_json', default='../../data/nuisance.json', type=str)
  parser.add_argument('--channel',      dest='channel', default='ele', type=str)
  parser.add_argument('--region',       dest='region', default = 'signal_region', type = str)
  parser.add_argument("--Labels", dest = 'Labels', default = ['Normal'], nargs='+')
  parser.add_argument("--Black_list", dest = 'Black_list', default = [], nargs='+')
  parser.add_argument("--sample_labels", dest='sample_labels', default = ["MC", "Background"], nargs='+')
  parser.add_argument("--Btag_WP", default='Medium')
  parser.add_argument("--POIs",   dest = 'POIs',   default = [], nargs='+')
  parser.add_argument("--scale",  dest = 'scale',  default = 1.0, type=float) 
  args = parser.parse_args()
  if "DEFAULT" in args.POIs: args.POIs = []
  #start = time.clock()
  Slim_module(args.iin, args.era, args.out, start = args.start, end = args.end, index = args.index, channel = args.channel, \
              sample_json = args.sample_json,\
              cut_json = args.cut_json,\
              variable_json = args.variable_json,\
              histogram_json = args.histogram_json,\
              trigger_json = args.trigger_json,\
              MET_filter_json = args.MET_filter_json,\
              nuisance_json = args.nuisance_json,\
              Btag_WP = args.Btag_WP,\
              region = args.region, Labels = args.Labels,Black_list = args.Black_list, POIs = args.POIs, sample_labels = args.sample_labels, scale = args.scale)
  #end = time.clock()
  #print('process time', end - start)

