import json
import argparse
import os 
import sys
from collections import OrderedDict
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)

from Init_Tool.Sample_Name_Producer import Bkg_MC_SAMPLE_NAME
from Init_Tool.Nuisance_Producer import nui_producer
from Init_Tool.Datacards_Input import Datacard_Input_Producer
from Util.General_Tool import CheckDir, python_version


parser = argparse.ArgumentParser()

parser.add_argument('-y','--year',help='Years of data.',default='2017')
parser.add_argument('-r','--region', help='Region', default='all')
parser.add_argument('-c','--channel',help='Channels',default='all')
parser.add_argument('--breakdown', action = "store_true")
parser.add_argument('-b','--blacklist',help='Block certain nuisance.',default=[''],nargs='*')


#####################
## mkdir data_info ##
#####################

if os.path.isdir(os.path.join(CURRENT_WORKDIR,'data_info')):pass
else:
    print("You don't have directory: `{}` under {}".format('data_info', CURRENT_WORKDIR))
    os.system('mkdir -p {}'.format(os.path.join(CURRENT_WORKDIR,'data_info')))
    print("Dir: data_info is made now.")

args = parser.parse_args()

############################
### Write MC samples name ##
############################

if args.year == 'all':
  era_list = ['2016postapv', '2016apv', '2017', '2018']
else:
  era_list = [args.year]

CheckDir("data_info/Sample_Names/",MakeDir=True)
for era in era_list:
  Bkg_MC_SAMPLE_NAME(year=era,outputdir="data_info/Sample_Names/")

##########################
## Write Nuisances List ##
##########################

jsonfile = open("data/cut.json")
if python_version == 2:
    regions = json.load(jsonfile, encoding='utf-8', object_pairs_hook=OrderedDict)
else:
    regions = json.load(jsonfile, object_pairs_hook=OrderedDict)
jsonfile.close()

CheckDir("./data_info/NuisanceList",MakeDir=True)

region_list = dict()
if args.region == 'all':
  for region in regions:
    region_list[region] = []
else:
  region_list[args.region] = []

if args.channel == 'all':
  for region in region_list:
    for channel in regions[region]["channel_cut"]:
      region_list[region].append(channel)
else:
  for region in region_list:
    region_list[region].append(args.channel)

nuisances_for_data_card = dict()
for era in era_list:
  nuisances_for_data_card[era] = dict()
  for region in region_list:
    nuisances_for_data_card[era][region] = dict()
    for channel in region_list[region]:
      nuisances_for_data_card[era][region][channel] = nui_producer(year=era, region=region, channel=channel\
                                                                  ,blacklist=args.blacklist,outputdir='./data_info/NuisanceList', breakdown = args.breakdown)
####################
## Datacard Input ##
####################

for era in era_list:
  CheckDir("data_info/Datacard_Input/{}/".format(era),MakeDir=True)
  with open('./data_info/Sample_Names/process_name_{}.json'.format(era),'r') as f:
    NAME = json.load(f)
    process = NAME.keys()
  for region in region_list:
    for channel in region_list[region]:
        print(nuisances_for_data_card[era][region][channel])
        Datacard_Input_Producer(year=era, region=region, channel=channel,nuisances=nuisances_for_data_card[era][region][channel],process=process)

