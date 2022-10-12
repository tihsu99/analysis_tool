import os 
import numpy as np 
import sys, optparse,argparse
from LimitHelper import *

couplings_List = ['rtc','rtu','rtt']
cp_values_List = ['01','04','08','09']
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

parser.add_argument("--outputdir",help='Create your favour outputdir. (If the directory is already existed, then the plots will simply stored under this directory, otherwise create one.)',default='./')

args = parser.parse_args()

category = args.category
coupling_value=args.coupling_value
year     = args.year

print ("coupling: ",coupling_value)
cat_str = category+"_"+category


mass_points = args.Masses
#coupling    = "rtc01"
template_card = "datacards_ttc_"+year+"/ttc_datacard_"+year+"_SR_"+cat_str+"_template.txt"
dc_tmplate=open(template_card).readlines()

if os.path.isdir("datacards_ttc_"+year+"/log"):pass
else:os.system("mkdir -p datacards_ttc_{}/log".format(year))


_coupling =''
_value = ''

for cpling in couplings_List:
    if cpling in coupling_value:
        _coupling = cpling
        _value=int(coupling_value.split(cpling)[-1])*0.1
    else:pass
print(_coupling,_value)
RL  = RunLimits(year,"ttc", category, "asimov", coupling=_coupling,coupling_value=_value) 

print ("self.limitlog: ",RL.limitlog)

counter=0
import time


start_time = time.time()

if not args.plot_only:
    for imass in mass_points:
        mA = str(imass)
        rtc = coupling_value.split("rtc")[-1]
        
        print ("{}: {}".format(_coupling,rtc))
        parameters = "MA"+str(imass)+"_"+coupling_value
        card_name = template_card.replace("template",parameters)
        print ("card_name: ", card_name)
        
        fout = open(card_name,'w')
        dc_out =  ([iline.replace("MASSPOINT",str(imass)) for iline in dc_tmplate] )
        dc_out =  ([iline.replace("COUPLINGVALUE",coupling_value) for iline in dc_out] ) ## mind that now it is dc_out
        dc_out =  ([iline.replace("../datacards_ttc_{}/".format(year),"") for iline in dc_out] )

        
        fout.writelines(dc_out)
        fout.close()
        
        logname = RL.getLimits(card_name)
        
        mode_ = "a"
        
        if counter==0: mode_="w"
        param_list=(mA,_value)
        limitlogfile = RL.LogToLimitList(logname,param_list,mode_)
        counter=counter+1
## this is out of the for loop 

### scale the limits with cross-section 

# set to 1 not to have any additional scales (before it was 0.01 - see below)
RL.getlimitScaled_1D(_value,1) ## 0.01 is the division factor as this is used in the datacards to make fit stable to avoid very small limit values specially the combination 

### convert text file to root file 
RL.TextFileToRootGraphs()


### save the .root file into a pdf file for presentations  
if os.path.isdir(args.outputdir):pass
else:os.system('mkdir -p {}'.format(args.outputdir))
RL.SaveLimitPdf1D(outputdir=args.outputdir,y_max=args.plot_y_max)
    
print("Run time for the current program is : {}".format(time.time()-start_time))
    
    
