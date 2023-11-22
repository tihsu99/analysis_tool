import json
from collections import OrderedDict
from Util.General_Tool import CheckFile, python_version
from Init_Tool.Nuisance_Group import DefineGroup

def nui_producer(year,blacklist=[],whitelist=[],outputdir='./data_info',channel=None, region=None, breakdown = False):

    nuis_List = dict()
    nuis_idx  = 0
    jsonfile = open("../data/nuisance.json")
    if python_version == 2:
      nuisances = json.load(jsonfile, encoding='utf-8', object_pairs_hook=OrderedDict).items()
    else:
      nuisances = json.load(jsonfile, object_pairs_hook=OrderedDict).items()
    jsonfile.close()

    for nui,desc in nuisances:
      if "Era" in desc and not year in desc["Era"]: continue
      if "Region" in desc and not region in desc["Region"]: continue
      if "Channel" in desc and not channel in desc["Channel"]: continue
      if nui in blacklist: continue
      nuis_List[nuis_idx] = "_" + nui
      nuis_idx += 1

    #################
    ## Add NormUnc ##
    #################

    jsonfile = open("../data/sample.json")
    if python_version == 2:
      samples = json.load(jsonfile, encoding='utf-8', object_pairs_hook=OrderedDict)
    else:
      samples = json.load(jsonfile, object_pairs_hook=OrderedDict)
    jsonfile.close()

    xsec_err_dict = dict()
    for sample_ in samples:
      if not "Background" in samples[sample_]["Label"]: continue
      if samples[sample_]["Category"] not in xsec_err_dict: xsec_err_dict[samples[sample_]["Category"]] = samples[sample_]["xsec_err"]
    for category_ in xsec_err_dict:
      nuis_List[nuis_idx] = '_norm' + category_
      nuis_idx += 1

    # TODO: breakdown function 

    CheckFile('{}/nuisance_list_{}_{}_{}.json'.format(outputdir,year,region,channel),True)    
    with open('{}/nuisance_list_{}_{}_{}.json'.format(outputdir,year,region,channel),'w') as f:
        json.dump(nuis_List,f,indent=4)
    return nuis_List
