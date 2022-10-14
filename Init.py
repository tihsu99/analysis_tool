import json
import argparse



import os 
import sys
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)

from Init_Tool.Sample_Name_Producer import Bkg_MC_SAMPLE_NAME
from Init_Tool.Nuisance_Producer import nui_producer
from Init_Tool.Datacards_Input import Datacard_Input_Producer
from Util.General_Tool import CheckDir 


parser = argparse.ArgumentParser()
channel_choices=['all','ee','em','mm']

parser.add_argument('-y','--year',help='Years of data.',default='2017')
parser.add_argument('-c','--channel',help='Years of data.',default='ee',choices=channel_choices)

parser.add_argument('-b','--blacklist',help='Block certain nuisance.',default=[''],nargs='*')

#if os.path.isdir('')
if os.path.isdir(os.path.join(CURRENT_WORKDIR,'data_info')):pass
else:
    print("You don't have directory: `{}` under {}".format('data_info', CURRENT_WORKDIR))
    os.system('mkdir -p {}'.format(os.path.join(CURRENT_WORKDIR,'data_info')))
    print("Dir: data_info is made now.")

args = parser.parse_args()
### Write MC samples name ########################
CheckDir("data_info/Sample_Names/",MakeDir=True)
Bkg_MC_SAMPLE_NAME(year=args.year,outputdir="data_info/Sample_Names/")
####Write Nuisances List #########################
CheckDir("./data_info/NuisanceList",MakeDir=True)

if args.channel =='all':
    nuisances_for_data_card = dict()
    for channel in channel_choices:
        if channel=='all':continue
        nuisances_for_data_card[channel] = nui_producer(year=args.year,blacklist=args.blacklist,outputdir='./data_info/NuisanceList',channel=channel)
else:
    nuisances_for_data_card = nui_producer(year=args.year,blacklist=args.blacklist,outputdir='./data_info/NuisanceList',channel=args.channel)

####Datacard Input #################################
CheckDir("data_info/Datacard_Input/{}/".format(args.year),MakeDir=True)



with open('./data_info/Sample_Names/process_name_{}.json'.format(args.year),'r') as f:
    NAME = json.load(f)

process = NAME.keys()

if args.channel=='all':
    for channel in ['ee','mm','em']:
        print(nuisances_for_data_card[channel])
        Datacard_Input_Producer(year=args.year,channel=channel,nuisances=nuisances_for_data_card[channel],process=process)
else:
    Datacard_Input_Producer(year=args.year,channel=args.channel,nuisances=nuisances_for_data_card,process=process)
############################

