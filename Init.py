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

args = parser.parse_args()
Bkg_MC_SAMPLE_NAME(year=args.year)
nui_producer(year=args.year,blacklist=args.blacklist)
