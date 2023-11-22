import json, sys
from Util.General_Tool import CheckFile, python_version
from collections import OrderedDict

'''
You need to fill in the process name for MC sample in root file manually.

'''

def Bkg_MC_SAMPLE_NAME(year='',outputdir=''):

    jsonfile = open("data/sample_%s.json"%year)
    if python_version == 2:
      samples = json.load(jsonfile, encoding='utf-8', object_pairs_hook=OrderedDict).items()
    else:
      samples = json.load(jsonfile, object_pairs_hook=OrderedDict). items()
    jsonfile.close()

    SAMPLE=dict()
    for process, desc in samples:
      if (("Data" in desc["Label"]) or ("Signal" in desc["Label"])): continue
      if desc["Category"] not in SAMPLE:
        SAMPLE[desc["Category"]] = [process]
      else:
        SAMPLE[desc["Category"]].append(process)
    
    CheckFile('{}/process_name_{}.json'.format(outputdir,year),True)
    with open('{}/process_name_{}.json'.format(outputdir,year),'w') as f:
        json.dump(SAMPLE,f,indent=4)
