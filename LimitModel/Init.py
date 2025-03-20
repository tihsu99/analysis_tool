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
from Util.General_Tool import CheckDir, python_version, read_json, CheckFile


parser = argparse.ArgumentParser()

parser.add_argument('-y','--year',help='Years of data.',default='all')
parser.add_argument('-r','--region', help='Region', default='all')
parser.add_argument('-c','--channel',help='Channels',default='all')
parser.add_argument('--breakdown', action = "store_true")
parser.add_argument('-b','--blacklist',help='Block certain nuisance.',default=[''],nargs='*')
parser.add_argument('--cut_json', default = '../data/cut.json')
parser.add_argument('--sample_json', default = '../data/sample.json')
parser.add_argument('--nuisance_json', default = '../data/nuisance.json')
parser.add_argument('--no_signal', action = 'store_true')
parser.add_argument('--ch_merge', action = 'store_true')
parser.add_argument('--era_merge', action = 'store_true')

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


##########################
## Write Nuisances List ##
##########################

regions = read_json(args.cut_json)

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

CheckDir("data_info/Sample_Names/",MakeDir=True)

for region in region_list:
  for channel in region_list[region]:
    for era in era_list:
      Bkg_MC_SAMPLE_NAME(year=era,outputdir="data_info/Sample_Names/", config=args, region = region, channel = channel)


nuisances_for_data_card = dict()
for era in era_list:
  nuisances_for_data_card[era] = dict()
  for region in region_list:
    nuisances_for_data_card[era][region] = dict()
    for channel in region_list[region]:
      nuisances_for_data_card[era][region][channel] = nui_producer(year=era, region=region, channel=channel\
                                                                  ,blacklist=args.blacklist,outputdir='./data_info/NuisanceList', breakdown = args.breakdown, config=args)
####################
## Datacard Input ##
####################
for era in era_list:
    CheckDir("data_info/Datacard_Input/{}/".format(era),MakeDir=True)
    for region in region_list:
      for channel in region_list[region]:
          print(nuisances_for_data_card[era][region][channel])
          with open('./data_info/Sample_Names/process_name_{}_{}_{}.json'.format(era, region, channel),'r') as f:
            NAME = json.load(f)
            process = NAME.keys()

          Datacard_Input_Producer(year=era, region=region, channel=channel,nuisances=nuisances_for_data_card[era][region][channel],process=process, config=args)

###################
## Channel merge ##
###################

if args.ch_merge:
    for era in era_list:
        for region in region_list:
          merged_input = None
          for channel in region_list[region]:
              channel_input_tmp = read_json(f"data_info/Datacard_Input/{era}/Datacard_Input_{region}_{channel}.json")
              channel_input = dict()
              for key_, input_ in channel_input_tmp.items():
                if isinstance(input_, dict):
                    channel_input[key_] = dict()
                    for sub_key in input_:
                        key_name = sub_key.replace("_CHANNEL", "")
                        channel_input[key_][key_name] = input_[sub_key]
                else:
                    channel_input[key_] = input_

              if merged_input is None:
                  merged_input = channel_input
              else:
                  for key_, input_ in channel_input.items():
                      if isinstance(input_, dict):
                          for sub_key in input_:
                              if sub_key not in merged_input[key_]:
                                  merged_input[key_][sub_key] = input_[sub_key]
          CheckFile('./data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json'.format(era, region, "merged_resolved"),True)
          with open('./data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json'.format(era, region, "merged_resolved"),'w') as f:
              json.dump(merged_input, f, indent=4)

###############
## Era merge ##
###############

if args.era_merge:
  for region in region_list:
    for channel in region_list[region]:
      merged_input = None
      for era in era_list:
          era_input_tmp = read_json(f"data_info/Datacard_Input/{era}/Datacard_Input_{region}_{channel}.json")
          era_input = dict()
          for key_, input_ in era_input_tmp.items():
            if isinstance(input_, dict):
                era_input[key_] = dict()
                for sub_key in input_:
                  year = '2016' if '2016' in era else era
                  key_name = sub_key.replace("ERA", era).replace("YEAR", year)
                  era_input[key_][key_name] = input_[sub_key]
            else:
                era_input[key_] = input_

          if merged_input is None:
              merged_input = era_input
          else:
              for key_, input_ in era_input.items():
                  if isinstance(input_, dict):
                      for sub_key in input_:
                          if sub_key not in merged_input[key_]:
                              merged_input[key_][sub_key] = input_[sub_key]
      CheckDir("./data_info/Datacard_Input/{}/".format('Merged_run2'),MakeDir=True)
      CheckFile('./data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json'.format('Merged_run2', region, channel),True)
      with open('./data_info/Datacard_Input/{}/Datacard_Input_{}_{}.json'.format('Merged_run2', region, channel),'w') as f:
        json.dump(merged_input, f, indent=4)
