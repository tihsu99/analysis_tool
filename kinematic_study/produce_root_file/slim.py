import ROOT
import time
import os, sys
import math
import json
import optparse, argparse
from collections import OrderedDict
from math import sqrt
sys.path.insert(1, '../../python')
from common import inputFile_path, read_json
from DNN_application import Build_DNN_Command
import ROOT

cwd = os.getcwd()

def Slim_module(filein,
                era,
                output_dir,
                channel = "ele",
                Labels=["Normal"],
                Black_list=[],
                POIs=[],
                sample_labels = [],
                weight_def="puWeight*genWeight*L1PreFiringWeight_Nom/abs(genWeight)*Lepton_ID_SF*Lepton_RECO_SF*btag_DeepJet_SF*Trigger_sf",
                scale = 1.0,
                sample_json = "../../data/sample.json",
                nuisance_json = "../../data/nuisance.json",
                variable_json = "../../data/variable.json",
                cut_json = "../../data/cut.json",
                trigger_json = "../../data/trigger.json",
                MET_filter_json = "../../data/MET_filter.json",
                histogram_json = "../../data/histogram.json",
                MVA_json = "../../data/MVA.json",
                MVA_weight_dir = "../MVA_study/MVA_Training_Weight/",
                region="signal_region",
                Btag_WP="Medium",
                start = -1,
                end   = -1,
                index = -1,
                pNN = False,
                cutflow_store=False):

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
  if 'eos' in fin and 'root://eosuser.cern.ch//' not in fin:
      fin = 'root://eosuser.cern.ch//' + fin

  if not index == -1:
    fileOut = os.path.join(output_dir, str(index) + "_" + filein)
    fileOut_alt = os.path.join(cwd, str(index) + "_" + filein)
  else:
    fileOut = os.path.join(output_dir, filein) 
    fileOut_alt = os.path.join(cwd, str(index) + "_" + filein)
  treeOut = "Events"

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
  fin = ROOT.TFile.Open(fin, "READ")
  tree = fin.Get("Events")
  if not start == -1:
    entry_list = ROOT.TEntryList()
    entry_list.EnterRange(start, end, tree)
    tree.SetEntryList(entry_list)
 
  df   = ROOT.RDataFrame(tree)
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
      if("Children" in variables[variable]):
          for child_no, child_name in enumerate(variables[variable]["Children"]):
              df = df.Define(str(child_name), str("{}[{}]".format(variable, child_no)))

    if variable in nuisances_valid:
      for nuisance in nuisances_valid[variable]:
        if "Era" in nuisances[nuisance] and era not in nuisances[nuisance]["Era"]: continue
        if "Region" in nuisances[nuisance] and region not in nuisances[nuisance]["Region"]: continue
        if "Channel" in nuisances[nuisance] and channel not in nuisances[nuisance]["Channel"]: continue
        sub_category = [""]
        if "sub_cat" in nuisances[nuisance]: sub_category = nuisances[nuisance]["sub_cat"]
        for sub_cat in sub_category:
          nuisance_def =  nuisances[nuisance]["Def"].replace('SUB', sub_cat).replace('YEAR', era)
          nuisance_name = (nuisance+sub_cat).replace('YEAR', era).replace('CHANNEL', channel)
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

  if cutflow_store:
    cutflow["channel"] = df.Sum("weight").GetValue()
  # trigger cut
  trigger_cut = None
  for trigger_name in triggers:
    if not channel in triggers[trigger_name]["Channel"]: continue
    if "Data" in sample_labels and not sample_name in triggers[trigger_name]["Dataset"]: continue
    if not "Data" in sample_labels: 
      trigger_cut = str(triggers[trigger_name]["Triggers"][era]["MC"])
    else:
      sub_era = filein.replace('.root', '').replace(sample_name + "_", '') 
      if sub_era in triggers[trigger_name]["Triggers"][era][sample_name]:
        trigger_cut = triggers[trigger_name]["Triggers"][era][sample_name][sub_era]
      else:
        trigger_cut = triggers[trigger_name]["Triggers"][era][sample_name]["Default"]


    df = df.Define(str(trigger_name), str(trigger_cut))
    df = df.Filter(str(trigger_name), str(trigger_name))
    print(trigger_name, str(trigger_cut))
    if cutflow_store:
      cutflow[trigger_name] = df.Sum("weight").GetValue() 
  # general cut
  for cut_name in cuts[region]["general_cut"]:
    df = df.Filter(str(cuts[region]["general_cut"][cut_name]), str(cut_name))
    if cutflow_store:
      cutflow[cut_name] = df.Sum("weight").GetValue()

  # METFilter cut
  MET_filter_cut = []
  for MET_filter in MET_filters["MET_Filter"]:
    if MET_filter in BranchList:
      MET_filter_cut.append(MET_filter)
  MET_filter_cut = ' && '.join(MET_filter_cut)
  print('MET filter',  MET_filter_cut)
  df = df.Filter(str(MET_filter_cut), 'MET_filter')
  if cutflow_store:
    cutflow['MET_filter'] = df.Sum("weight").GetValue()

  if cutflow_store:
    print(cutflow)

  ####################
  ##  MVA Variable  ##
  ####################

  MVA_json_dict = read_json(MVA_json)
  BDT = dict()
  if MVA_weight_dir is not None:
    MVA_list = os.listdir(MVA_weight_dir)
    for MVA in MVA_list:
        ROOT.gInterpreter.ProcessLine('''
        TMVA::Experimental::RBDT<> %s ("XGB", "%s");
        computeModel_%s = TMVA::Experimental::Compute<%d, float> (%s);
        '''%(MVA, os.path.join(MVA_weight_dir, MVA, "XGB.root"), MVA, len(MVA_json_dict["xgboost"]), MVA))
        df = df.Define(str(MVA), eval("ROOT.computeModel_%s"%MVA), MVA_json_dict["xgboost"])
        POIs.append(MVA)

  if pNN:
    var = MVA_json_dict['xgboost']
    var.append('Mass')
    Build_DNN_Command(var)
    for mass_ in [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]:
      define_ = 'DNN(' + ', '.join(var) + ')'
      define_ = define_.replace('Mass', str(mass_))
      print(define_)
      df = df.Define(str('DNN{}'.format(mass_)), str(define_))
      POIs.append('DNN{}'.format(mass_))


  #################
  ##  Histogram  ##
  #################

  Histos     = []
  jsonfile   = open(histogram_json)
  Histograms = json.load(jsonfile, object_pairs_hook=OrderedDict)
  jsonfile.close()


  if MVA_weight_dir is not None:
    for MVA in MVA_list:
      Histograms[MVA] = {
        "Title": ";BDT;nEntries",
        "xlow":0,
        "xhigh":1,
        "nbin": 10,
        "Label": ["Reco","Normal", "BDT"]
      }
  
  if pNN:
    for mass_ in [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]:
      Histograms['DNN{}'.format(mass_)] = {
        "Title": ";DNN;nEntries",
        "xlow":0,
        "xhigh":1,
        "nbin": 10,
        "Label": ["Normal", "pNN"]
      }


  Histos_from_df = dict()
  Histos_from_df_var = dict()


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

    if Histogram in POIs: Flag = True
    if not Flag:
      print("Label do not satisfied the requirement. Black list label triggered:%s"%Label_trigger)
      continue

    Title  = str(Histograms[Histogram]["Title"])
    xlow   = Histograms[Histogram]["xlow"]
    xhigh  = Histograms[Histogram]["xhigh"]
    nbin   = Histograms[Histogram]["nbin"] * 600 # will be rebinned when plotting
    df_histo = df.Histo1D((str(Histogram), Title, nbin, xlow, xhigh), str(Histogram), "weight")
    Histos_from_df[Histogram] = df_histo

    ## Nuisance variation for POIs
    if Histogram in POIs:
      Histos_from_df_var[Histogram] = ROOT.RDF.Experimental.VariationsFor(df_histo)
#      print(h_variation.GetKeys())
#      for nuisance in nuisance_list:
#        if ("{}:Down".format(nuisance) not in h_variation.GetKeys()): continue
#        h_variation_do = h_variation[nuisance + ":Down"]
#        h_variation_up = h_variation[nuisance + ":Up"]
#        h_variation_do.SetName(str((Histogram + "_" + nuisance + "_down").replace("YEAR",era)))
#        h_variation_up.SetName(str((Histogram + "_" + nuisance + "_up").replace("YEAR", era)))
#        Histos.append(h_variation_do)
#        Histos.append(h_variation_up)

  # Cutflow Histogram
  if cutflow_store:
    histo_cutflow = ROOT.TH1D('cutflow', ';;nEvents', len(cutflow), 0, len(cutflow))
    for idx, cut_name in enumerate(cutflow):
      histo_cutflow.SetBinContent(idx+1, cutflow[cut_name])
      histo_cutflow.GetXaxis().SetBinLabel(idx + 1, str(cut_name))
    Histos.append(histo_cutflow.Clone())

  for Histogram in Histos_from_df:
    Histos.append(Histos_from_df[Histogram].GetValue().Clone())

  for Histogram in Histos_from_df_var:
    h_variation = Histos_from_df_var[Histogram]
    for nuisance in nuisance_list:
      if("{}:Down".format(nuisance) not in h_variation.GetKeys()): continue
      h_variation_do = h_variation[nuisance + ":Down"]
      h_variation_up = h_variation[nuisance + ":Up"]
      h_variation_do.SetName(str((Histogram + "_" + nuisance + "_down").replace("YEAR",era)))
      h_variation_up.SetName(str((Histogram + "_" + nuisance + "_up").replace("YEAR", era)))
      Histos.append(h_variation_do)
      Histos.append(h_variation_up)

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
    if "Children" in variables[variable]:
        for child_ in variables[variable]["Children"]:
            columns.push_back(str(child_))
   
  if not "Data" in sample_labels:
    columns.push_back('weight')
    df = df.Define("weight_n_Norm", "weight * %f"%(scale))
    columns.push_back('weight_n_Norm')
  
  if 'eos' in fileOut and 'root://eosuser.cern.ch//' not in fileOut:
    fileOut = 'root://eosuser.cern.ch//{}'.format(fileOut)
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

  print('Total events loop for RDataFrame: ', df.GetNRuns())
  FileOut.Close()
  fin.Close()



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
  parser.add_argument("--MVA_json", default = "../../data/MVA.json", type=str)
  parser.add_argument("--MVA_weight_dir", default = None, type=str)
  parser.add_argument("--pNN", action='store_true')
  parser.add_argument("--cutflow", action='store_true')
  args = parser.parse_args()
  if "DEFAULT" in args.POIs: args.POIs = []
  if args.MVA_weight_dir == "None": args.MVA_weight_dir = None
  start_time = time.time()

#  ROOT.ROOT.EnableImplicitMT()
  poolSize = ROOT.GetThreadPoolSize()
  print ("Pool size =",poolSize)
  Slim_module(args.iin, args.era, args.out, start = args.start, end = args.end, index = args.index, channel = args.channel, \
              sample_json = args.sample_json,\
              cut_json = args.cut_json,\
              variable_json = args.variable_json,\
              histogram_json = args.histogram_json,\
              trigger_json = args.trigger_json,\
              MET_filter_json = args.MET_filter_json,\
              nuisance_json = args.nuisance_json,\
              Btag_WP = args.Btag_WP,\
              MVA_json = args.MVA_json,\
              MVA_weight_dir = args.MVA_weight_dir, \
              region = args.region, Labels = args.Labels,Black_list = args.Black_list, POIs = args.POIs, sample_labels = args.sample_labels, scale = args.scale,\
              pNN = args.pNN,\
              cutflow_store = args.cutflow)
  end_time = time.time()
  print('process time', end_time - start_time)

