import ROOT
import time
import os, sys
import math
import json
import optparse, argparse
from collections import OrderedDict
from math import sqrt
sys.path.insert(1, '../../python')
from common import *
from DNN_application import Build_DNN_Command, Build_EnsembleDNN_Command
import re
import copy
from termcolor import colored

cwd = os.getcwd()

def Slim_module(filein,
                era,
                output_dir,
                channel = "ele",
                Labels=["Normal"],
                Black_list=[],
                POIs=[],
                sample_labels = [],
                weight_def="puWeight*genWeight*L1PreFiringWeight_Nom/abs(genWeight)*Lepton_ID_SF*Lepton_RECO_SF*btag_DeepJet_SF*Trigger_sf*Pileupjetid_sf",
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
                multi_class_pNN=False,
                cutflow_store=False,
                SubProcess = None,
                toppt = False,
                not_ensemble = False):

  #############
  ##  Basic  ##
  #############

  year = era
  if '2016' in era: year = '2016'

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
  Mass_bin = [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]
  #################
  ##  Load File  ##
  #################


  jsonfile = open(sample_json)
  samples = json.load(jsonfile)
  jsonfile.close()
  samples = Extend_sample_dict(samples, key_word = 'MASS')

  if 'Signal' in sample_labels: sample_name = filein.replace('.root', '')
  else: sample_name = re.sub(r'((?:_(\d+|\w))|(?:_\w_\d)|(?:_\w\d))\.root','', filein).replace('.root','')

  # sample_category mainly used for nuisance def.
  sample_category = samples[sample_name]['Category'] 
  sample_category = 'Signal' if 'Signal' in sample_labels else sample_category

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

  if not SubProcess is None and ('SubProcess' in samples[sample_name]):
    fileOut = fileOut.replace(filein, SubProcess + '.root')
  treeOut = "Events"

  if not os.path.isdir(output_dir):
    os.system("mkdir -p " + output_dir)



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
  print(colored(fin,'green'), colored(start,'cyan'), colored(end,'cyan'))
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


  ##############
  ##  Weight  ##
  ##############
  if "Data" in sample_labels:
    weight_def = 1       # Data weight is also to be 1
    nuisances_valid = [] # Nuisances only affect MC
  if toppt:
    if "TTTo1L" in filein or "TTTo2L" in filein:
      print (colored('--> For ttbar apply toppt_weight','yellow'))
      weight_def="puWeight*genWeight*L1PreFiringWeight_Nom/abs(genWeight)*Lepton_ID_SF*Lepton_RECO_SF*btag_DeepJet_SF*Trigger_sf*Pileupjetid_sf*toppt_weight"


  #################################
  ##  Assign Train / Test Label  ##
  #################################
  df = df.Define(str("prob_2b"), str(samples[sample_name]["Train_ratio"]["2b"])) 
  df = df.Define(str("prob_3b"), str(samples[sample_name]["Train_ratio"]["3b"])) 

  #######################
  ##  Define Variable  ##
  #######################

  jsonfile  = open(variable_json)
  variables = json.load(jsonfile, object_pairs_hook=OrderedDict)
  jsonfile.close()

  variables['weight'] = {
    "Def": str('(float)({})'.format(weight_def)),
    'Label': ['Normal']
  }

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
    if (("Process_Forbid" in variables[variable]) and (sample_name in variables[variable]['Process_Forbid'])):continue


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
        if "Process" in nuisances[nuisance] and (sample_category not in nuisances[nuisance]["Process"]): continue
        sub_category = [""]
        if "sub_cat" in nuisances[nuisance]: sub_category = nuisances[nuisance]["sub_cat"]
        for sub_cat in sub_category:
          nuisance_def =  nuisances[nuisance]["Def"].replace('SUB', sub_cat).replace('ERA', era).replace('YEAR', year)
          if 'Name' in nuisances[nuisance]:
            if nuisances[nuisance]['Name']['Criteria'] == 'CHANNEL':
              nuisance_name = nuisances[nuisance]['Name'][channel]
            elif nuisances[nuisance]['Name']['Criteria'] == 'REGION':
              nuisance_name = nuisances[nuisance]['Name'][region]
            elif nuisances[nuisance]['Name']['Criteria'] == 'ERA':
              nuisance_name = nuisances[nuisance]['Name'][era]
          else:
              nuisance_name = nuisance

          nuisance_name = (nuisance_name+sub_cat).replace('ERA', era).replace('CHANNEL', channel).replace('YEAR', year).replace('PROCESS', sample_category)
          cprint(nuisance_name, 'yellow')
          print(nuisances[nuisance]["Nominal"], nuisance_def)
          df = df.Vary(nuisances[nuisance]["Nominal"], nuisance_def, ["Down", "Up"], nuisance_name)
          nuisance_list.append(nuisance_name)

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


  if pNN or multi_class_pNN:
    MVA_Label = cuts[region]["MVA_Label"]

  if cutflow_store:
    cutflow["total"] = df.Sum("weight").GetValue()

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

  # channel cut
  for cut_name in cuts[region]["channel_cut"][channel]:
    df = df.Filter(str(cuts[region]["channel_cut"][channel][cut_name]), str(cut_name))

  if cutflow_store:
    cutflow["channel"] = df.Sum("weight").GetValue()

  # general cut
  for cut_name in cuts[region]["general_cut"]:
    df = df.Filter(str(cuts[region]["general_cut"][cut_name]), str(cut_name))
    if cutflow_store:
      cutflow[cut_name] = df.Sum("weight").GetValue()

  if cutflow_store:
    print(cutflow)

  # signal cut
  if not (SubProcess is None) and ('SubProcess' in samples[sample_name]):
    df = df.Filter(str(samples[sample_name]['SubProcess'][SubProcess]))
    print('Sub Process cut: {}'.format(samples[sample_name]['SubProcess'][SubProcess]))

  # POIs setting
  if 'ASCUTJSON' in POIs:
     POIs = cuts[region]['POI']


  ####################
  ##  MVA Variable  ##
  ####################

  MVA_json_dict = read_json(MVA_json)
  BDT = dict()

  ## BDT Usage
  if MVA_weight_dir is not None:
    MVA_list = os.listdir(MVA_weight_dir)
    for MVA in MVA_list:
        ROOT.gInterpreter.ProcessLine('''
        TMVA::Experimental::RBDT<> %s ("XGB", "%s");
        computeModel_%s = TMVA::Experimental::Compute<%d, float> (%s);
        '''%(MVA, os.path.join(MVA_weight_dir, MVA, "XGB.root"), MVA, len(MVA_json_dict["xgboost"]), MVA))
        df = df.Define(str(MVA), eval("ROOT.computeModel_%s"%MVA), MVA_json_dict["xgboost"])
        POIs.append(MVA)


  ## parametric DNN usage
  if pNN:
    var = MVA_json_dict[MVA_Label]
    var.append('Mass')
    if not_ensemble:
      Build_DNN_Command(var, MVA_Label, 'pNN')
    else:
      Build_EnsembleDNN_Command(var, MVA_Label, os.path.join('pNN', era))
    for mass_ in Mass_bin:
      define_ = ('{}(' + ', '.join(var) + ')[0]').format(MVA_Label)
      define_ = define_.replace('Mass', str(mass_))
      print(define_)
      df = df.Define(str('DNN{}'.format(mass_)), str(define_))

  ## Multi-class parametric DNN usage
  if multi_class_pNN:
    var = MVA_json_dict[MVA_Label]
    var.append('Mass')
    Build_DNN_Command(var, MVA_Label, 'multiClassDNN')
    for mass_ in Mass_bin:
      define_ = ('{}(' + ', '.join(var) + ')').format(MVA_Label)
      define_ = define_.replace('Mass', str(mass_))
      print(define_)
      df = df.Define(str('DNN{}_v'.format(mass_)), str('SoftMax({})'.format(define_)))
      df = df.Define(str('DNN{}_class'.format(mass_)), str('ArgMax(DNN{}_v)'.format(mass_)))
      df = df.Define(str('DNN{}'.format(mass_)), str('DNN{}_v[DNN{}_class]'.format(mass_, mass_)))
      df = df.Define(str('DNNScore{}'.format(mass_)), str('DNN{}_v[DNN{}_class] / (DNN{}_v[DNN{}_class] + DNN{}_v[0])'.format(mass_, mass_, mass_, mass_, mass_)))
      df = df.Define(str('DNN{}_bkg'.format(mass_)), str('DNN{}_v[0]'.format(mass_)))
      df = df.Define(str('DNN{}_2b'.format(mass_)), str('DNN{}_v[1]'.format(mass_)))
      df = df.Define(str('DNN{}_3b'.format(mass_)), str('DNN{}_v[2]'.format(mass_)))

  #################
  ##  Histogram  ##
  #################

  Histos     = []
  jsonfile   = open(histogram_json)
  Histograms = json.load(jsonfile, object_pairs_hook=OrderedDict)
  jsonfile.close()


  # for BDT MVA case
  if MVA_weight_dir is not None:
    for MVA in MVA_list:
      Histograms[MVA] = {
        "Title": ";BDT;nEntries",
        "xlow":0,
        "xhigh":1,
        "nbin": 10,
        "Label": ["Reco","Normal", "BDT"]
      }

  # DNN score for different mass point
  if pNN or multi_class_pNN:
    for mass_ in Mass_bin:
      Histograms['DNN{}'.format(mass_)] = {
        "Title": ";DNN;nEntries",
        "xlow":0,
        "xhigh":1,
        "nbin": 10,
        "Label": ["Normal", "pNN"],
        "cut": cuts[region]["DNN_category"] if "DNN_category" in cuts[region] else None
      }
      Histograms['DNN{}'.format(mass_)]['cut'] = Histograms['DNN{}'.format(mass_)]['cut'].replace('MASS', str(mass_)) if Histograms['DNN{}'.format(mass_)]['cut'] is not None else None

      if multi_class_pNN:
        Histograms['DNNScore{}'.format(mass_)] = {
          "Title": ";DNNScore;nEntries",
          "xlow":0.5,
          "xhigh":1,
          "nbin": 10,
          "Label": ["Normal", "pNN"],
          "cut": cuts[region]["DNN_category"] if "DNN_category" in cuts[region] else None
        }
        Histograms['DNNScore{}'.format(mass_)]['cut'] = Histograms['DNNScore{}'.format(mass_)]['cut'].replace('MASS', str(mass_)) if Histograms['DNNScore{}'.format(mass_)]['cut'] is not None else None

  # Store each DNN output node (mainly for control region)
  if multi_class_pNN:
    if 'DNN_category' not in cuts[region]:
      for mass_ in Mass_bin:
        Histograms['DNN{}_bkg'.format(mass_)] = copy.deepcopy(Histograms['DNN{}'.format(mass_)])
        Histograms['DNN{}_2b'.format(mass_)] = copy.deepcopy(Histograms['DNN{}'.format(mass_)])
        Histograms['DNN{}_3b'.format(mass_)] = copy.deepcopy(Histograms['DNN{}'.format(mass_)])

  # POIs consider DNN for different mass
  POIs_after_consider_mass = []
  for POI_ in POIs:
    if (POI_ == 'DNN' or POI_ == 'DNNScore') and (pNN or multi_class_pNN): 
        for mass_ in Mass_bin:
          POIs_after_consider_mass.append('{}{}'.format(POI_, mass_))
    elif multi_class_pNN and ( "DNN_category" in cuts[region]):
      for mass_ in Mass_bin:
        Histograms['{}{}'.format(POI_, mass_)] = copy.deepcopy(Histograms[POI_])
        Histograms['{}{}'.format(POI_, mass_)]['cut'] =  cuts[region]["DNN_category"].replace('MASS', str(mass_)) if "DNN_category" in cuts[region] else None
        Histograms['{}{}'.format(POI_, mass_)]['definition'] = str(POI_)
        POIs_after_consider_mass.append('{}{}'.format(POI_, mass_))
    else:
      POIs_after_consider_mass.append(POI_)
  POIs = POIs_after_consider_mass

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

    # Add cut for DNN_Category (for pNN or multi_class_pNN)
    if 'cut' not in Histograms[Histogram]:
      Histograms[Histogram]["cut"] = cuts[region]["DNN_category"] if "DNN_category" in cuts[region] else None

    if Histogram in POIs: Flag = True
    if not Flag:
      print("Label do not satisfied the requirement. Black list label triggered:%s"%Label_trigger)
      continue

    Title  = str(Histograms[Histogram]["Title"])
    xlow   = Histograms[Histogram]["xlow"]
    xhigh  = Histograms[Histogram]["xhigh"]
    nbin   = Histograms[Histogram]["nbin"] * 600 # will be rebinned when plotting
    if (len(POIs) > 1): nbin = Histograms[Histogram]["nbin"] # When doing systematic variation, do not use large no. of bins to save memory

    if (not "cut" in Histograms[Histogram]): df_plot = df
    elif (Histograms[Histogram]["cut"] is None): df_plot = df
    else: df_plot = df.Filter(str(Histograms[Histogram]["cut"]))

 
    Histogram_definition = Histograms[Histogram]['definition'] if 'definition' in Histograms[Histogram] else str(Histogram)
    df_histo = df_plot.Histo1D((str(Histogram), Title, nbin, xlow, xhigh), Histogram_definition, "weight")
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
    print(Histogram)
    Histos.append(Histos_from_df[Histogram].GetValue().Clone())

  for Histogram in Histos_from_df_var:
    h_variation = Histos_from_df_var[Histogram]
    for nuisance in nuisance_list:
      if("{}:Down".format(nuisance) not in h_variation.GetKeys()): continue
      h_variation_do = h_variation[nuisance + ":Down"]
      h_variation_up = h_variation[nuisance + ":Up"]
      h_variation_do.SetName(str((Histogram + "_" + nuisance + "_down").replace("ERA",era).replace('YEAR',year).replace("PROCESS", sample_category)))
      h_variation_up.SetName(str((Histogram + "_" + nuisance + "_up").replace("ERA", era).replace('YEAR',year).replace("PROCESS", sample_category)))
      Histos.append(h_variation_do)
      Histos.append(h_variation_up)

  ######################
  ##  Store Variable  ##
  ######################

  print("start to store")

  columns = ROOT.std.vector("string")()

  for variable in variables:
    if "Data" in sample_labels and "MC" in variables[variable]["Label"]: continue
    if variable not in df.GetColumnNames(): continue
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
    columns.push_back('toppt_weight') #gkole
    columns.push_back('Pileupjetid_sf')
    
  if 'eos' in fileOut and 'root://eosuser.cern.ch//' not in fileOut:
    fileOut = 'root://eosuser.cern.ch//{}'.format(fileOut)

  print(columns)
  df.Snapshot(treeOut, fileOut, columns)
  print (colored('Output file: ','green'),colored('{}'.format(fileOut), 'cyan'))
  #######################
  ##  Store Histogram  ##
  #######################
  
  FileOut = ROOT.TFile.Open(fileOut, "Update")
  FileOut.cd()
  for ij in range(0, len(Histos)):
    h = Histos[ij].Clone()
    print(h.GetName())
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
  parser.add_argument("--multi_class_pNN", action='store_true')
  parser.add_argument("--cutflow", action='store_true')
  parser.add_argument("--SubProcess", type=str, default = None)
  parser.add_argument("--toppt",   action='store_true')
  parser.add_argument("--not_ensemble", action = 'store_true')

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
              cutflow_store = args.cutflow,\
              SubProcess = args.SubProcess,\
              multi_class_pNN = args.multi_class_pNN,\
              toppt = args.toppt,\
              not_ensemble = args.not_ensemble)
  end_time = time.time()
  print('process time', end_time - start_time)

