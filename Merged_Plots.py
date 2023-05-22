import argparse

import os 
import sys
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)
from collections import OrderedDict
 

parser = argparse.ArgumentParser()
channel_choices=['C','ee','em','mm']
year_choices=['2016apv','2016postapv','2017','2018','run2']

couplingvalue_choices = []
for coupling in ['rtc','rtu','rtt']:
    for value in ['0p1','0p4','0p8','1p0']:
        couplingvalue_choices.append(coupling+value)


parser.add_argument('-y','--year',help='Years of data.',default=['2017'],nargs='+')
parser.add_argument('-c','--channel',help='Years of data.',default=['ee'],choices=channel_choices,nargs='+')
parser.add_argument('--coupling_values',help='List of coupling values',default=['rtu01','rtu04'],nargs='+')

parser.add_argument("--plot_y_max",help='Plot Only',default=1000,type=float)
parser.add_argument("--plot_y_min",help='Plot Only',default=0.1,type=float)

parser.add_argument("--outputdir",help='Create your favour outputdir. (If the directory is already existed, then the plots will simply stored under this directory, otherwise create one.)',default='./')
parser.add_argument("--Masses",default=[200,300,350,400,500,600,700,800,900,1000],nargs='+')

parser.add_argument("--unblind",action="store_true")
parser.add_argument("--interference", action="store_true")
parser.add_argument("--paper", action="store_true")
parser.add_argument("--AN", action="store_true")
parser.add_argument("--interp", action="store_true")

args = parser.parse_args()

import Util.Plot_Tool 
from Util.General_Tool import CheckDir,CheckFile

#./bin/2018/C/limits_ttc_rtu0p8_asimov_extYukawa.txt

log_files_path_Dict = OrderedDict()


Mode = "Coupling"
if len(args.year) > 1:
  Mode = "Year"
elif len(args.channel) > 1:
  Mode = "Channel"
else:
  Mode = "Coupling"

if Mode == "Coupling":

  year    = args.year[0]
  channel = args.channel[0]

  for value in args.coupling_values:
    if value not in couplingvalue_choices: raise ValueError('No such coupling values: {}'.format(value))
    
    coupling_value = 'ttc_'+value

    log_files_path_per_value = './bin/{year}/{channel}/limits_{coupling_value}_asimov_extYukawa.root'.format(year=year,channel=channel,coupling_value=coupling_value)

    if args.interference:
      log_files_path_per_value = log_files_path_per_value.replace(".root","_interference.root")
    
    if CheckFile(log_files_path_per_value,quiet=True):pass
    else:
        raise ValueError("Check you have run runlimits.py for --plot_only for {value}".format(value=value))

    log_files_path_Dict[value] = log_files_path_per_value

elif Mode == "Year":

  value   = args.coupling_values[0]
  channel = args.channel[0]

  for year in args.year:
    
    coupling_value = 'ttc_'+value

    log_files_path_per_value = './bin/{year}/{channel}/limits_{coupling_value}_asimov_extYukawa.root'.format(year=year,channel=channel,coupling_value=coupling_value)
    if args.interference:
      log_files_path_per_value = log_files_path_per_value.replace(".root","_interference.root")
    
    if CheckFile(log_files_path_per_value,quiet=True):pass
    else:
        raise ValueError("Check you have run runlimits.py for --plot_only for {value}".format(value=value))
    log_files_path_Dict[year] = log_files_path_per_value

else:

  value = args.coupling_values[0]
  year  = args.year[0]

  for channel in args.channel:
    
    coupling_value = 'ttc_'+value

    log_files_path_per_value = './bin/{year}/{channel}/limits_{coupling_value}_asimov_extYukawa.root'.format(year=year,channel=channel,coupling_value=coupling_value)
    if args.interference:
      log_files_path_per_value = log_files_path_per_value.replace(".root","_interference.root")
    
    if CheckFile(log_files_path_per_value,quiet=True):pass
    else:
        raise ValueError("Check you have run runlimits.py for --plot_only for {value}".format(value=value))
    log_files_path_Dict[channel] = log_files_path_per_value

from Util.Plot_Tool import Plot_1D_Limit_For, Plot_2D_Limit_For
if not args.interp:
  Plot_1D_Limit_For(log_files_path_Dict,unblind=args.unblind,y_max=args.plot_y_max,y_min=args.plot_y_min,year=args.year,channel=args.channel,outputFolder=args.outputdir,Masses=args.Masses,interference=args.interference, paper=args.paper, AN=args.AN, Coupling_value = args.coupling_values, mode = Mode)
else:
  Plot_2D_Limit_For(log_files_path_Dict, args.unblind, args.year, args.channel, args.outputdir, args.Masses, args.interference, args.paper)
