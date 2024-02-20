import json
from Util.General_Tool import CheckFile, python_version
from collections import OrderedDict

def Datacard_Input_Producer(year, region='', channel='', process=[] , nuisances=[]):

    Input = dict()    

    Input['bin']=dict()

    Input['Process'] = process
    if 'SIGNAL' in process:
      pass
    else:
        Input['Process'].insert(0,'SIGNAL')

    process = Input['Process']
    Input['bin'][region] = len(Input['Process'])
    Input['process1'] =range(len(Input['Process']))
    Input['rate'] = [-1 for i in range(len(Input['Process']))]
    Input['NuisForProc'] = dict()
    Input['UnclnN'] = dict()

    jsonfile = open("../data/nuisance.json")
    if python_version == 2:
      nuisance_dict = json.load(jsonfile, encoding='utf-8', object_pairs_hook=OrderedDict)
    else:
      nuisance_dict = json.load(jsonfile, object_pairs_hook=OrderedDict)
    jsonfile.close()
   
    for nuisance in nuisances:
        nuisance='_'.join(str(nuisances[nuisance]).split('_')[1:]).strip()
        if nuisance not in nuisance_dict: continue # NormUnc will be defined specifically in next part 
        ############
        ## UnclnN ##
        ############
        if 'sub_cat' in nuisance_dict[nuisance]:
          sub_cat_list = nuisance_dict[nuisance]['sub_cat']
        else:
          sub_cat_list = ['']
        for sub_cat in sub_cat_list:
          nuisance_name = nuisance+sub_cat          
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
          if "Background" in nuisance_dict[nuisance]["Label"]: 
            Input['NuisForProc'][nuisance_name] = process[1:]
          if "Signal" in nuisance_dict[nuisance]["Label"]:
            Input['NuisForProc'][nuisance_name].insert(0,"SIGNAL")
 
    ######################
    ## Norm Uncertainty ##
    ######################

    jsonfile = open("../data/sample.json")
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
      Input['UnclnN']['norm' + category_] = str(1. + 0.01 * xsec_err_dict[category_])
      Input['NuisForProc']['norm' + category_] = [category_]


    CheckFile('./data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json'.format(year, region, channel),True)
    with open('./data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json'.format(year, region, channel),'w') as f:
        json.dump(Input,f,indent=4)
 
    print("Write Datacard_Input into ./data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json".format(year, region, channel))
    print("")
    return Input

