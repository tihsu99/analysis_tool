import os 
import numpy as np 
import sys, optparse,argparse
from LimitHelper import *


usage = "python runlimits.py -c em"
parser = argparse.ArgumentParser(description=usage)
parser.add_argument("-c", "--category", dest="category", default="em")
parser.add_argument("-y", "--year", dest="year", default="2017")

parser.add_argument("-rtc", "--rtc", dest="rtc", default="rtc01")


args = parser.parse_args()

category = args.category
coupling=args.rtc
year     = args.year

print ("coupling: ",coupling)
cat_str = category+"_"+category


mass_points = [200,300,350,400,500,600,700]
#coupling    = "rtc01"
template_card = "datacards_ttc_"+year+"/ttc_datacard_"+year+"_SR_"+cat_str+"_template.txt"
dc_tmplate=open(template_card).readlines()

rtc_=int(coupling.split("rtc")[-1])*0.1

RL  = RunLimits(year,"ttc", category, "asimov", rtc_) 

print ("self.limitlog: ",RL.limitlog)

counter=0
for imass in mass_points:
    mA = str(imass)
    rtc = coupling.split("rtc")[-1]
    print ("rtc: ",rtc)
    parameters = "MA"+str(imass)+"_"+coupling
    card_name = template_card.replace("template",parameters)
    print ("card_name: ", card_name)
    
    fout = open(card_name,'w')
    dc_out =  ([iline.replace("MASSPOINT",str(imass)) for iline in dc_tmplate] )
    dc_out =  ([iline.replace("COUPLINGVALUE",coupling) for iline in dc_out] ) ## mind that now it is dc_out
    dc_out =  ([iline.replace("../datacards_ttc_2016/","") for iline in dc_out] )
    dc_out =  ([iline.replace("../datacards_ttc_2017/","") for iline in dc_out] )
    dc_out =  ([iline.replace("../datacards_ttc_2018/","") for iline in dc_out] )
    dc_out =  ([iline.replace("../datacards_ttc_2016apv/","") for iline in dc_out] )

    
    fout.writelines(dc_out)
    fout.close()
    
    logname = RL.getLimits(card_name)
    
    mode_ = "a"
    if counter==0: mode_="w"
    param_list=(mA,rtc)
    limitlogfile = RL.LogToLimitList(logname,param_list,mode_)
    counter=counter+1
    
## this is out of the for loop 

### scale the limits with cross-section 

RL.getlimitScaled_1D(rtc_,0.01) ## 0.01 is the division factor as this is used in the datacards to make fit stable to avoid very small limit values specially the combination 

### convert text file to root file 
RL.TextFileToRootGraphs()


### save the .root file into a pdf file for presentations  
RL.SaveLimitPdf1D()
    
    
    
    
