import json
from Util.General_Tool import CheckFile, python_version
from collections import OrderedDict
import os, sys
sys.path.append('../python')
from common import *

def Datacard_Input_Producer(year, region='', channel='', process=[] , nuisances=[], config = None):

    samples = read_json(config.sample_json)
    process_raw = list(process)
    Input = dict()    

    region_info = read_json(config.cut_json)

    print("process_raw", process_raw)
    process = []
    process_data_driven = []
    process_free_float  = []
    region_ABCD = dict() 
    if 'ABCDmethod' in region_info[region]:
      region_ABCD = region_info[region]['ABCDmethod']

    for process_ in process_raw:
      for sample in samples:
        if samples[sample]['Category'] == process_:
          if 'FreeFloat'  in samples[sample]['Label']: process_free_float.append(process_)
          if 'DataDriven' in samples[sample]['Label']: process_data_driven.append(process_)
          else: process.append(process_)
          break

    print("process", process)
    print("process(data driven)", process_data_driven)


    Input['bin']=dict()

    Input['Process'] = process_raw

    if not config.no_signal:
      if 'SIGNAL' in process:
        pass
      else:
        Input['Process'].insert(0,'SIGNAL')

    Input['bin'][region] = len(Input['Process'])
    Input['process1'] = list(range(len(Input['Process'])))
    Input['rate'] = [-1 for i in range(len(Input['Process']))]
    Input['NuisForProc'] = dict()
    Input['UnclnN'] = dict()
    Input['FreeFloat'] = list(process_free_float)
    Input['ABCDmethod'] = region_ABCD


    jsonfile = open(config.nuisance_json)
    if python_version == 2:
      nuisance_dict = json.load(jsonfile, encoding='utf-8', object_pairs_hook=OrderedDict)
    else:
      nuisance_dict = json.load(jsonfile, object_pairs_hook=OrderedDict)
    jsonfile.close()
  
    nuisance_list = []

    for nuisance in nuisances:
        nuisance='_'.join(str(nuisances[nuisance]).split('_')[1:]).strip()
        nuisance_list.append(nuisance)
        if nuisance not in nuisance_dict: continue # NormUnc will be defined specifically in next part 
        ############
        ## UnclnN ##
        ############
        if 'sub_cat' in nuisance_dict[nuisance]:
          sub_cat_list = nuisance_dict[nuisance]['sub_cat']
        else:
          sub_cat_list = ['']
        for sub_cat in sub_cat_list:
          nuisance_name_ = nuisance+sub_cat        
          print(nuisance_name_, "PROCESS" in nuisance_name_)
          if "PROCESS" in nuisance_name_:
            if "Process" not in nuisance_dict[nuisance]:
              nuisance_names = [nuisance_name_.replace("PROCESS", process_) for process_ in process] # All Background
              if("Signal" in nuisance_dict[nuisance]["Label"]) and not config.no_signal: nuisance_names.append(nuisance_name_.replace("PROCESS", "Signal"))
            else:
              nuisance_names = []
              for process_ in nuisance_dict[nuisance]["Process"]:
                if config.no_signal and "Signal" in process_: continue
                nuisance_names.append(nuisance_name_.replace("PROCESS", process_))

              print(nuisance_names)
          else:
            nuisance_names = [nuisance_name_]

          for nuisance_name in nuisance_names:
            if 'Shape' in nuisance_dict[nuisance]["Label"]:
              Input['UnclnN'][nuisance_name]='shape'
            else:
              if isinstance(nuisance_dict[nuisance]["value"], float):
                Input['UnclnN'][nuisance_name]=str(nuisance_dict[nuisance]["value"])
              if isinstance(nuisance_dict[nuisance]["value"], dict):
                label_list = []
                if "Era" in nuisance_dict[nuisance]["vary"]: label_list.append(year)
                if "Region" in nuisance_dict[nuisance]["vary"]: label_list.append(region)
                if "Channel" in nuisance_dict[nuisance]["vary"]: label_list.append(channel)
                label_search = '_'.join(label_list)
                Input['UnclnN'][nuisance_name]=str(nuisance_dict[nuisance]["value"][label_search])

            Input['NuisForProc'][nuisance_name] = []

            if "PROCESS" in nuisance_name_:
              blind_process_name = nuisance_name_.replace('PROCESS', '')
              process_name = nuisance_name.replace(blind_process_name, '')
              if "Signal" in process_name and config.no_signal: continue
              Input['NuisForProc'][nuisance_name] = [process_name.replace("Signal", "SIGNAL")]
 
            elif "Process" in nuisance_dict[nuisance]:
              nuisance_tmp = []
              for  process_ in nuisance_dict[nuisance]["Process"]:
                if "Signal" in process_ and config.no_signal: 
                    continue
                else:
                    nuisance_tmp.append(process_.replace("Signal", "SIGNAL"))
              Input['NuisForProc'][nuisance_name] = nuisance_tmp
            else:
              if "Background" in nuisance_dict[nuisance]["Label"]: 
                Input['NuisForProc'][nuisance_name] = process
              if "Signal" in nuisance_dict[nuisance]["Label"]:
                if "SIGNAL" not in Input['NuisForProc'][nuisance_name] and not config.no_signal:
                  Input['NuisForProc'][nuisance_name].insert(0,"SIGNAL")
            if config.add_data_driven_process:
              for process_ in process_data_driven:
                if process_ not in Input['NuisForProc'][nuisance_name] and ("Signal" not in nuisance_name):
                  Input['NuisForProc'][nuisance_name].append(process_)

   



    ######################
    ## Norm Uncertainty ##
    ######################

    jsonfile = open(config.sample_json)
    if python_version == 2:
      samples = json.load(jsonfile, encoding='utf-8', object_pairs_hook=OrderedDict)
    else:
      samples = json.load(jsonfile, object_pairs_hook=OrderedDict)
    jsonfile.close()
    xsec_err_dict = dict()
    for sample_ in samples:
      ## Current use conservative method to estimate the xsec_err
      if not "Background" in samples[sample_]["Label"]: continue
      if samples[sample_]["Category"] not in xsec_err_dict: xsec_err_dict[samples[sample_]["Category"]] = samples[sample_]["xsec_err"]
      else: xsec_err_dict[samples[sample_]["Category"]] = max(xsec_err_dict[samples[sample_]["Category"]], samples[sample_]["xsec_err"])  
    for category_ in xsec_err_dict:
      if 'norm' + category_ not in nuisance_list: continue
      Input['UnclnN']['norm' + category_] = str(1. + 0.01 * xsec_err_dict[category_])
      Input['NuisForProc']['norm' + category_] = [category_]

      if config.add_data_driven_process:
        for process_ in process_data_driven:
            if process_ not in Input['NuisForProc']['norm' + category_]:
                  Input['NuisForProc']['norm' + category_].append(process_)


    CheckFile('./data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json'.format(year, region, channel),True)
    print(Input)
    with open('./data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json'.format(year, region, channel),'w') as f:
        json.dump(Input,f,indent=4)
 
    print("Write Datacard_Input into ./data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json".format(year, region, channel))
    print("")
    return Input

