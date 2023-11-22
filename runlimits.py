import os 
import numpy as np 
import sys, optparse,argparse
from LimitHelper import *
from Util.General_Tool import CheckFile
from collections import OrderedDict
import time

usage = "python runlimits.py -c em"
parser = argparse.ArgumentParser(description=usage)
parser.add_argument("-c", "--channel", dest="channel", default="ele")
parser.add_argument("-r", "--region", dest="region", default="SR")
parser.add_argument("-y", "--year", dest="year", default="2017")
parser.add_argument("--rtc", dest="rtc", default=0.4, type=float)
parser.add_argument("--rtt", dest="rtt", default=0.6, type=float)
parser.add_argument("--Masses",help='List of masses point. Default list=[200,300,350,400,500,600,700]',default=[200, 300, 350, 400, 500, 600, 700],nargs='+')
parser.add_argument("--plot_only",help='Plot Only',action="store_true")
parser.add_argument("--plot_y_max",help='Plot Only',default=1000,type=float)
parser.add_argument("--plot_y_min",help='Plot Only',default=0.1,type=float)
parser.add_argument("--datacarddir", help='datacard directory', default='datacards_test', type=str)
parser.add_argument("--outputdir",help='Create your favour outputdir. (If the directory is already existed, then the plots will simply stored under this directory, otherwise create one.)',default='./')
parser.add_argument("--reset_outputfiles",help='Reset the output files.',action="store_true")
parser.add_argument('--cminDefaultMinimizerStrategy', help='cminDefaultMinimizerStrategy: default = 0', default=0,type=int)
parser.add_argument('--cminDefaultMinimizerTolerance', help= 'default = 1.0', default=1.0, type=float)
parser.add_argument('--rAbsAcc', help='default = 0.001', default=0.001, type=float)
parser.add_argument('--unblind', help='for limit unbliding', action="store_true")
parser.add_argument('--verbose','-v', dest='verbose', help='for combine verbose', action="store_true")
parser.add_argument('--rMax',dest='rMax', default=5, type=float)
args = parser.parse_args()

year     = args.year
region   = args.region
channel  = args.channel
cat_str = region+"_"+channel


mass_points = args.Masses

###############################
##  Analysis Dependent Part  ##
###############################

signal_param = OrderedDict()
signal_param["rtt"] = str(args.rtt).replace('.','p')
signal_param["rtc"] = str(args.rtc).replace('.','p')
signal_name_template = "CGToBHpm_a_MASS_rtt{}_rtc{}".format(signal_param["rtt"].replace('p',''), signal_param["rtc"].replace('p',''))
analysis_name        = "bH"
Higgs_Mass_Name      = "MH"
##############################

print("datacards_{}_{}/log".format(year, analysis_name))
CheckDir("datacards_{}_{}/log".format(year, analysis_name),True)
start_time = time.time()

RL  = RunLimits(year=year, analysis= analysis_name, region=region, channel=channel, postfix="asimov", unblind=args.unblind, verbose=args.verbose, rMax=args.rMax, signal_param=signal_param)

if args.reset_outputfiles:
    CheckFile(RL.limitlog,True)
    CheckFile(RL.limit_root_file,True)
else:pass
#print ("self.limitlog: ",RL.limitlog)

if args.plot_only:

    RL.TextFileToRootGraphs(Masses=mass_points, Higgs=Higgs_Mass_Name)
    CheckDir(args.outputdir,True)
    RL.SaveLimitPdf1D(outputdir=args.outputdir,y_max=args.plot_y_max,y_min=args.plot_y_min)
else:
    counter=0
    template_card = "{dc_dir}/{year}/{signal}/{signal}_{year}_{region}_{channel}.txt".format(dc_dir=args.datacarddir, year=year, signal=signal_name_template, region=region, channel=channel)
    #datacards_2016apv_ttu/ttu_rtu04_datacard_2016apv_SR_em_em_MA1000.txt
    for imass in mass_points:
        mH = str(imass)
        card_name = template_card.replace("MASS", mH)
        logname = RL.getLimits(card_name,asimov=False, mass_point=Higgs_Mass_Name+str(imass),cminDefaultMinimizerStrategy=args.cminDefaultMinimizerStrategy, rAbsAcc=args.rAbsAcc, cminDefaultMinimizerTolerance=args.cminDefaultMinimizerTolerance, dc_dir=args.datacarddir, log_dir='datacard_log')
        
        mode_ = "w"
        
        if counter==0: mode_="w"
        
        param_list=(Higgs_Mass_Name,mH,RL.signal_str_) # e.g., (200,0.4)
        limitlogfile = RL.LogToLimitList(logname,param_list,mode_)
        counter=counter+1
## this is out of the for loop 

### scale the limits with cross-section 

# set to 1 not to have any additional scales (before it was 0.01 - see below)
#RL.getlimitScaled_1D(_value,1) ## 0.01 is the division factor as this is used in the datacards to make fit stable to avoid very small limit values specially the combination 

### convert text file to root file 


### save the .root file into a pdf file for presentations  

    
print("Run time for the current program is : {}".format(time.time()-start_time))
    
    
