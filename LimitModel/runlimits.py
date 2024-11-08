import os
import numpy as np
import sys, optparse,argparse
from LimitHelper import *
from Util.General_Tool import CheckFile
from collections import OrderedDict
import time
sys.path.append('../python')
from common import *
from array import array
import ROOT
from Util.Plot_Tool import Plot_1D_Limit_For, Plot_2D_Limit_For

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
parser.add_argument("--plot_y_min",help='Plot Only',default=0.01,type=float)
parser.add_argument("--datacard_dir", help='datacard directory', default='datacards_test', type=str)
parser.add_argument("--outputdir",help='Create your favour outputdir. (If the directory is already existed, then the plots will simply stored under this directory, otherwise create one.)',default='./')
parser.add_argument("--reset_outputfiles",help='Reset the output files.',action="store_true")
parser.add_argument('--cminDefaultMinimizerStrategy', help='cminDefaultMinimizerStrategy: default = 0', default=0,type=int)
parser.add_argument('--cminDefaultMinimizerTolerance', help= 'default = 1.0', default=1.0, type=float)
parser.add_argument('--rAbsAcc', help='default = 0.001', default=0.001, type=float)
parser.add_argument('--unblind', help='for limit unbliding', action="store_true")
parser.add_argument('--verbose','-v', dest='verbose', help='for combine verbose', action="store_true")
parser.add_argument('--rMax',dest='rMax', default=5, type=float)
parser.add_argument('--signal_template', type=str, default = 'CGToBHpm_a_MASS_rttRTT_rtcRTC')
parser.add_argument('--analysis_name', type=str, default = 'bH')
parser.add_argument('--signal_xsec', action='store_true')
parser.add_argument('--sample_json', type=str, default='../data/sample.json')
parser.add_argument('--Scan2D', action='store_true')
parser.add_argument('--Scan2DNLL', action = 'store_true')
parser.add_argument('--POI_name', type=str, default='r_3b')
parser.add_argument('--model_name', type=str, default='g2HDM_3Bbased')
parser.add_argument('--ratio_file', type=str, default=None)
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
signal_name_template = args.signal_template.replace('RTT', signal_param["rtt"].replace('p','')).replace('RTC', signal_param["rtc"].replace('p',''))
analysis_name        = args.analysis_name
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


  signal_xsec_TGraph = None
  if args.signal_xsec:
    signal_xsec = array('d')
    signal_xsec_up = array('d')
    signal_xsec_do = array('d')
    mass_bin    = array('d')
    errx = array('d')
    samples = Extend_sample_dict(read_json(args.sample_json), key_word='MASS')
    for imass in mass_points:
        mH = str(imass)
        signal = signal_name_template.replace('MASS', mH)
        xsec = samples[signal]['xsec'] if signal in samples else 0.0
        xsec_err = samples[signal]['xsec_err'] if (signal in samples and 'xsec_err' in samples[signal]) else 10.0 #TODO: should be corrected
        signal_xsec.append(xsec)
        signal_xsec_up.append(xsec*xsec_err/100.)
        signal_xsec_do.append(xsec*xsec_err/100.)
        mass_bin.append(float(mH))
        errx.append(0.0)
    print(mass_bin)
    print(signal_xsec)
    signal_xsec_TGraph = ROOT.TGraphAsymmErrors(len(mass_bin), mass_bin, signal_xsec, errx, errx, signal_xsec_up, signal_xsec_do)


  if args.Scan2DNLL:
      for imass in mass_points:
          mH = str(imass)
          RL.Save2DNLL(outputdir = args.outputdir,mass_point=Higgs_Mass_Name+str(imass), POI_name = args.POI_name, model_name = args.model_name, ratio_file = args.ratio_file)

 

  elif args.Scan2D:
    limitlog = RL.limitlog
    TGraph_File_dict = dict()
    Rb_list = []
    for Rb in [0.1*i for i in range(11)]:
      RL.SetLimitLog(limitlog.replace('.txt', '_%s_Rb%.1f.txt'%(args.POI_name, Rb)))
      print(RL.limitlog)
      TGraph_File = RL.TextFileToRootGraphs(Masses=mass_points, Higgs=Higgs_Mass_Name)
      TGraph_File_dict[Rb] = TGraph_File
      Rb_list.append(Rb)
      RL.limit_pdf_file = "limits_" + RL.analysis_ + "_"+ RL.signal_str_ + "_" + RL.postfix_+"_"+RL.model_ + "_" + RL.region_ + "_" + RL.channel_ + "_Rb%.1f.pdf"%(Rb)
      print("saving")
      RL.SaveLimitPdf1D(outputdir=args.outputdir, y_max=args.plot_y_max, y_min=args.plot_y_min, signal_xsec_TGraph=signal_xsec_TGraph)

    print(TGraph_File_dict)
    Plot_2D_Limit_For(TGraph_File_dict, args.unblind, args.year, args.channel, args.outputdir, args.Masses, y_axis_title = 'R_{b}', ratio_file = args.ratio_file, signal_xsec_TGraph = signal_xsec_TGraph)
    Plot_1D_Limit_For(TGraph_File_dict, args.unblind, y_max=args.plot_y_max, y_min=args.plot_y_min, year=[args.year], region=[args.region], channel=[args.channel], outputFolder=args.outputdir, Masses=args.Masses, mode = "Rb", legend_dict={(0.1*0):'pp\\rightarrow bH^{+}', (0.1*10):'pp\\rightarrow bH^{+} + H^{+}'}, AN=True)
  else:
    TGraph_File = RL.TextFileToRootGraphs(Masses=mass_points, Higgs=Higgs_Mass_Name)
    CheckDir(args.outputdir,True)
    #RL.SaveLimitPdf1D(outputdir=args.outputdir,y_max=args.plot_y_max,y_min=args.plot_y_min)
    RL.SaveLimitPdf1D(outputdir=args.outputdir,y_max=args.plot_y_max,y_min=args.plot_y_min, signal_xsec_TGraph=signal_xsec_TGraph)
else:
    counter=0
    template_card = "{dc_dir}/{year}/{signal}/{signal}_{year}_{region}_{channel}.txt".format(dc_dir=args.datacard_dir, year=year, signal=signal_name_template, region=region, channel=channel)
    #datacards_2016apv_ttu/ttu_rtu04_datacard_2016apv_SR_em_em_MA1000.txt
    for imass in mass_points:
        mH = str(imass)
        card_name = template_card.replace("MASS", mH)
        if args.Scan2DNLL:
          RL.Scan2DNLL(card_name.replace('txt','root'), POI_name = args.POI_name, asimov=True, mass_point=Higgs_Mass_Name+str(imass), dc_dir=args.datacard_dir, out_dir=os.path.join(args.outputdir, '2DNLL'), model_name = args.model_name)

        elif not args.Scan2D:
          logname = RL.getLimits(card_name,asimov=False, mass_point=Higgs_Mass_Name+str(imass),cminDefaultMinimizerStrategy=args.cminDefaultMinimizerStrategy, rAbsAcc=args.rAbsAcc, cminDefaultMinimizerTolerance=args.cminDefaultMinimizerTolerance, dc_dir=args.datacard_dir, log_dir='datacard_log')
          mode_ = "w"

          if counter==0: mode_="w"

          param_list=(Higgs_Mass_Name,mH,RL.signal_str_) # e.g., (200,0.4)
          limitlogfile = RL.LogToLimitList(logname,param_list,mode_)
          counter=counter+1

        elif args.Scan2D:
          mode_ = 'w'
          for Rb in [0.1 * i for i in range(11)]:
            extraCommand = '--redefineSignalPOIs {POI}  --setParameters Rb={Rb},{POI}=0.0 --freezeParameters Rb --defineBackgroundOnlyModelParameters {POI}=0,Rb={Rb}'.format(Rb=Rb, POI=args.POI_name)
            logname = RL.getLimits(card_name.replace('txt','root'),asimov=False, mass_point=Higgs_Mass_Name+str(imass),cminDefaultMinimizerStrategy=args.cminDefaultMinimizerStrategy, rAbsAcc=args.rAbsAcc, cminDefaultMinimizerTolerance=args.cminDefaultMinimizerTolerance, dc_dir=args.datacard_dir, log_dir='datacard_log', logname=card_name.replace('.txt','_%s_Rb%.1f.log'%(args.POI_name, Rb)), extraCommand = extraCommand)
            param_list=(Higgs_Mass_Name,mH,RL.signal_str_) # e.g., (200,0.4)
            print('post logname:', logname)
            limitlogfile = RL.LogToLimitList(logname, param_list, mode_, postfix='_%s_Rb%.1f'%(args.POI_name, Rb), POI=args.POI_name)
## this is out of the for loop

### scale the limits with cross-section

# set to 1 not to have any additional scales (before it was 0.01 - see below)
#RL.getlimitScaled_1D(_value,1) ## 0.01 is the division factor as this is used in the datacards to make fit stable to avoid very small limit values specially the combination

### convert text file to root file


### save the .root file into a pdf file for presentations

print("Run time for the current program is : {}".format(time.time()-start_time))
