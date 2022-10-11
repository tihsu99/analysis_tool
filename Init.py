import json
import argparse



import os 
import sys
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)

from Init_Tool.Sample_Name_Producer import Bkg_MC_SAMPLE_NAME
from Init_Tool.Nuisance_Producer import nui_producer


parser = argparse.ArgumentParser()

parser.add_argument('-y','--year',help='Years of data.',default='2017')

parser.add_argument('-b','--blacklist',help='Block certain nuisance.',default=[''],nargs='*')

#if os.path.isdir('')
if os.path.isdir(os.path.join(CURRENT_WORKDIR,'data_info')):pass
else:
    print("You don't have directory: `{}` under {}".format('data_info', CURRENT_WORKDIR))
    os.system('mkdir -p {}'.format(os.path.join(CURRENT_WORKDIR,'data_info')))
    print("Dir: data_info is made now.")

args = parser.parse_args()
Bkg_MC_SAMPLE_NAME(year=args.year)
nui_producer(year=args.year,blacklist=args.blacklist)
