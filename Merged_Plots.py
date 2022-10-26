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



parser.add_argument('-y','--year',help='Years of data.',default='2017',choices=year_choices)
parser.add_argument('-c','--channel',help='Years of data.',default='ee',choices=channel_choices)
parser.add_argument('--coupling_values',help='List of coupling values',default=['rtu01','rtu04'],nargs='+')

parser.add_argument("--plot_y_max",help='Plot Only',default=1000,type=float)
parser.add_argument("--plot_y_min",help='Plot Only',default=0.1,type=float)

parser.add_argument("--outputdir",help='Create your favour outputdir. (If the directory is already existed, then the plots will simply stored under this directory, otherwise create one.)',default='./')
parser.add_argument("--Masses",default=[200,300,350,400,500,600,700,800,900,1000],nargs='+')

parser.add_argument("--unblind",action="store_true")

args = parser.parse_args()

import Util.Plot_Tool 
from Util.General_Tool import CheckDir,CheckFile

#./bin/2018/C/limits_ttc_rtu0p8_asimov_extYukawa.txt

log_files_path_Dict = OrderedDict()


for value in args.coupling_values:
    if value not in couplingvalue_choices: raise ValueError('No such coupling values: {}'.format(value))
    
    if 'rtc' in value:
        coupling_value = 'ttc_'+value
    elif 'rtu' in value:
        coupling_value = 'ttc_'+value
    elif 'rtt' in value:
        coupling_value = 'ttc_'+value
    else:raise ValueError('No such coupling values: {}'.format(value))

    log_files_path_per_value = './bin/{year}/{channel}/limits_{coupling_value}_asimov_extYukawa.root'.format(year=args.year,channel=args.channel,coupling_value=coupling_value)
    
    if CheckFile(log_files_path_per_value,quiet=True):pass
    else:
        raise ValueError("Check you have run runlimits.py for --plot_only for {value}".format(value=value))


    log_files_path_Dict[value] = log_files_path_per_value
# python ./Merged_Plots.py --channel C --year run2 --coupling_values rtu01 rtu04 --plot_y_max 1000 --plot_y_min 0.001 --outputdir /eos/user/z/zhenggan/www/run2/merged_plot/ttu 
from Util.Plot_Tool import Plot_1D_Limit_For
Plot_1D_Limit_For(log_files_path_Dict,unblind=args.unblind,y_max=args.plot_y_max,y_min=args.plot_y_min,year=args.year,channel=args.channel,outputFolder=args.outputdir,Masses=args.Masses)