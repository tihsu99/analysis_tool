import os 
import sys
CURRENT_WORKDIR = os.getcwd()
from Util.Tool_For_Integrate import Integrate_LimitPlots,Integrate_SignalExtraction,Integrate_LimitTables
import argparse

parser = argparse.ArgumentParser()
### Choices ###
coupling_choices = ['rtu','rtc']
coupling_values = ['0p1','0p4','0p8','1p0']
coupling_values_choices = []
for c in coupling_choices:
    for v in coupling_values:
        coupling_values_choices.append(c+v)

year_choices = ['2016apv','2016postapv','2017','2018','run2']
channel_choices = ['C','ee','em','mm']
mode_choices = ['LimitPlots','SignalExtraction','LimitTables']
###############


### Common Options ###
parser.add_argument('--coupling',help='Coupling_values',default='rtu',choices=coupling_choices)
parser.add_argument('--year',default='2016apv',choices=year_choices)
parser.add_argument('--channel',choices=channel_choices,default='ee')
parser.add_argument('--mode',choices=mode_choices)
parser.add_argument('--unblind', action="store_true")
######################

### Valid for LimitsPlots (only for merged plots) ###
parser.add_argument('--limit_original_dir')
#############################

### Valid for Impact etc. in SignalExtraction ###
parser.add_argument('--IncludeSignal',action="store_true")
parser.add_argument('--WalkAll',action="store_true")
parser.add_argument('--mass',type=str)
parser.add_argument('--coupling_value',help='Coupling',default='rtu0p4',choices=coupling_values_choices)
parser.add_argument('--interference',action="store_true")
#################################################



args = parser.parse_args()

exec_mode_string = 'Integrate_'+args.mode
MODE = eval(exec_mode_string)
MODE(args)



