import json, sys
from Util.General_Tool import CheckFile, python_version, read_json
from collections import OrderedDict

'''
You need to fill in the process name for MC sample in root file manually.

'''

def Bkg_MC_SAMPLE_NAME(year='',outputdir='', region='', channel='', config=None):


    samples = read_json(config.sample_json)

    SAMPLE=dict()
    for process, desc in samples.items():
      if (("Data" in desc["Label"]) or ("Signal" in desc["Label"])): continue
      if "Region" in desc and region not in desc["Region"]: continue
      if "Channel" in desc and channel not in desc["Channel"]: continue
      if desc["Category"] not in SAMPLE:
        SAMPLE[desc["Category"]] = [process]
      else:
        SAMPLE[desc["Category"]].append(process)
    
    CheckFile('{}/process_name_{}_{}_{}.json'.format(outputdir,year, region, channel),True)
    with open('{}/process_name_{}_{}_{}.json'.format(outputdir,year, region, channel),'w') as f:
        json.dump(SAMPLE,f,indent=4)
