import os 
import numpy as np 
import sys, optparse,argparse
from LimitHelper import *
from Util.General_Tool import CheckFile
couplings_List = ['rtc','rtu','rtt']
cp_values_List = ['01','04','08','10']
coupling_value_choices=[]
for coupling in couplings_List:
    for value in cp_values_List:
        coupling_value_choices.append(coupling+value)

usage = "python runlimits.py -c em"
parser = argparse.ArgumentParser(description=usage)
parser.add_argument("-c", "--category", dest="category", default="em")
parser.add_argument("-y", "--year", dest="year", default="2017")

#parser.add_argument("-rtc", "--rtc", dest="rtc", default="rtc01")
parser.add_argument("-coupling_value", "--coupling_value", dest="coupling_value", default="rtc01",choices=coupling_value_choices)

parser.add_argument("--Masses",help='List of masses point. Default list=[200,300,350,400,500,600,700]',default=[200, 300, 350, 400, 500, 600, 700],nargs='+')
parser.add_argument("--plot_only",help='Plot Only',action="store_true")
parser.add_argument("--plot_y_max",help='Plot Only',default=1000,type=float)
parser.add_argument("--plot_y_min",help='Plot Only',default=0.1,type=float)

parser.add_argument("--outputdir",help='Create your favour outputdir. (If the directory is already existed, then the plots will simply stored under this directory, otherwise create one.)',default='./')
parser.add_argument("--reset_outputfiles",help='Reset the output files.',action="store_true")
args = parser.parse_args()

category = args.category # i.e., channel: ee, em, mm
coupling_value=args.coupling_value # e.g, rtc04
year     = args.year

print ("coupling: ",coupling_value)
cat_str = category+"_"+category


mass_points = args.Masses
#coupling    = "rtc01"



_coupling =''
_value = ''

for cpling in couplings_List:
    if cpling in coupling_value:
        _coupling = cpling  # Gives coupling : rtc, rtu, rtt
        _value=int(coupling_value.split(cpling)[-1])*0.1 # Gives coupling value in float: 0.1, 0.4, 0.8, 1.0
    else:pass
print(_coupling,_value)


if _coupling == 'rtc':
    signal_process_name = 'ttc'
elif _coupling == 'rtu':
    signal_process_name = 'ttu'
elif _coupling == 'rtt':
    signal_process_name = 'ttt'
else:raise ValueError("No such coupling:{coupling}".format(coupling=_coupling))
signal_process_name = 'ttc' #Keep the naming rule, suggested by Gouranga.

print("datacards_{}_{}/log".format(year,signal_process_name))
CheckDir("datacards_{}_{}/log".format(year,signal_process_name),True)

import time


start_time = time.time()
RL  = RunLimits(year=year,analysis="ttc",analysisbin=category,postfix="asimov", coupling=_coupling,coupling_value=_value) 
if args.reset_outputfiles:
    CheckFile(RL.limitlog,True)
    CheckFile(RL.limit_root_file,True)
else:pass



#print ("self.limitlog: ",RL.limitlog)

if args.plot_only:

    RL.TextFileToRootGraphs(Masses=mass_points)
    CheckDir(args.outputdir,True)
    RL.SaveLimitPdf1D(outputdir=args.outputdir,y_max=args.plot_y_max,y_min=args.plot_y_min)
else:
    counter=0
    template_card = "datacards_{year}_{signal_process_name}".format(year=year,signal_process_name=signal_process_name)+"/{signal_process_name}_{coupling_value}_datacard_".format(signal_process_name=signal_process_name,coupling_value=coupling_value)+year+"_SR_"+cat_str+"_template.txt"
    #datacards_2016apv_ttu/ttu_rtu04_datacard_2016apv_SR_em_em_MA1000.txt
    for imass in mass_points:
        mA = str(imass)
        rtc = coupling_value.split("rtc")[-1] # Gives coupling value in string with "." -> "p": 0p1, 0p4, 0p8, 1p0
        
        print ("{}: {}".format(_coupling,rtc))
        parameters = "MA"+str(imass) # MA200_rtc0p4, for example.
        card_name = template_card.replace("template",parameters)
        
        logname = RL.getLimits(card_name,asimov=True,mass_point="MA"+imass)
        
        mode_ = "a"
        
        if counter==0: mode_="w"
        Higgs = "MA"
        
        param_list=(Higgs,mA,_value) # e.g., (200,0.4)
        limitlogfile = RL.LogToLimitList(logname,param_list,mode_)
        counter=counter+1
## this is out of the for loop 

### scale the limits with cross-section 

# set to 1 not to have any additional scales (before it was 0.01 - see below)
#RL.getlimitScaled_1D(_value,1) ## 0.01 is the division factor as this is used in the datacards to make fit stable to avoid very small limit values specially the combination 

### convert text file to root file 


### save the .root file into a pdf file for presentations  

    
print("Run time for the current program is : {}".format(time.time()-start_time))
    
    
