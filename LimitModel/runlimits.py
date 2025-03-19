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

import pandas as pd

def get_line_style_from_value(x, y):
    """
    Given a value x and y return a line style based on the default line styles.
    """
    if x==0.6 and y==0.1:
        return 1
    elif x==0.6 and y==1.0:
        return 2
    elif x==0.1 and y==0.4:
        return 3
    elif x==1.0 and y==0.4:
        return 4
    else:
        return 1

def get_color_from_value(x, min_val, max_val):
    """
    Given a value x, return a color based on the default heatmap gradient (kTemperature).
    """
    # Normalize x to the range [0, 1]
    normalized_x = (x - min_val) / (max_val - min_val)

    # Clamp the value between 0 and 1
    normalized_x = max(0.0, min(1.0, normalized_x))

    # Set the default color palette (kTemperature)
    rt.gStyle.SetPalette(rt.kLightTemperature)  # Choose a predefined palette like kTemperature

    # Retrieve the color at the normalized position
    color = rt.gStyle.GetColorPalette(int(normalized_x * 255))  # Scale to [0, 255] range for the palette

    return color



# Read the file into a DataFrame, skipping the header separator lines
file_path = "../data/signal_xsec.txt"  # Replace with your file path
df_sig_xsec = pd.read_csv(
    file_path,
    delim_whitespace=True,  # Handle white-space delimited data
    skiprows=2,             # Skip the second row containing '---'
)

# Rename columns to match the file structure (optional)
df_sig_xsec.columns = ["Mass", "rtt", "rtc", "xsec", "sigma(bgth)[pb]", "sigma(bgth)/sigma(cgbh)"]


file_path = "../data/signal_xsec_unc.txt"
# Define column names explicitly, as some have spaces or special characters
column_names = [
    "Mass", "rtt", "rtc",
    "scale_unc_+", "scale_unc_-", "scale_unc_avg",
    "PDF_unc_(%)", "total_unc"
]
# Read the file while handling whitespace and missing columns
df_sig_xsec_err = pd.read_csv(
    file_path,
    delim_whitespace=True,  # Handle white-space delimited data
    skiprows=1,             # Skip the comment row (starts with #)
    names=column_names,     # Use predefined column names
    engine="python",        # Use Python engine for complex parsing
    na_values=["..."]       # Handle potential missing values
)

# Clean up the uncertainty columns
# Ensure "scale_unc_+" and "scale_unc_-" are numeric
df_sig_xsec_err["scale_unc_+"] = pd.to_numeric(df_sig_xsec_err["scale_unc_+"], errors="coerce")
df_sig_xsec_err["scale_unc_-"] = pd.to_numeric(df_sig_xsec_err["scale_unc_-"], errors="coerce")
df_sig_xsec_err["rtt"] = df_sig_xsec_err["rtt"] * 0.1
df_sig_xsec_err["rtc"] = df_sig_xsec_err["rtc"] * 0.1

print(df_sig_xsec)
print(df_sig_xsec_err)

usage = "python runlimits.py -c em"
parser = argparse.ArgumentParser(description=usage)
parser.add_argument("-c", "--channel", dest="channel", default="ele")
parser.add_argument("-r", "--region", dest="region", default="SR")
parser.add_argument("-y", "--year", dest="year", default="2017")
parser.add_argument("--year_for_plot", dest = 'year_for_plot', default = ['2016apv', '2016postapv', '2017', '2018', 'run2'])
parser.add_argument("--region_for_plot", dest = 'region_for_plot', default = ['SR_2b2j', 'SR_2b3j', 'SR_2b4j', 'SR_3b3j', 'SR_3b4j'])
parser.add_argument("--rtc", dest="rtc", default=0.4, type=float)
parser.add_argument("--rtt", dest="rtt", default=0.6, type=float)
parser.add_argument("--Masses",help='List of masses point. Default list=[200,300,350,400,500,600,700]',default=[200, 300, 350, 400, 500, 600, 700],nargs='+')
parser.add_argument("--plot_only",help='Plot Only',action="store_true")
parser.add_argument("--plot_y_max",help='Plot Only',default=3e2,type=float)
parser.add_argument("--plot_y_min",help='Plot Only',default=5e-3,type=float)
parser.add_argument("--datacard_dir", help='datacard directory', default='datacards_test', type=str)
parser.add_argument("--outputdir",help='Create your favour outputdir. (If the directory is already existed, then the plots will simply stored under this directory, otherwise create one.)',default='./')
parser.add_argument("--reset_outputfiles",help='Reset the output files.',action="store_true")
parser.add_argument('--cminDefaultMinimizerStrategy', help='cminDefaultMinimizerStrategy: default = 0', default=0, type=int)
parser.add_argument('--cminDefaultMinimizerTolerance', help= 'default = 1.0', default=0.1, type=float)
parser.add_argument('--rAbsAcc', help='default = 0.001', default=0.0002, type=float)
parser.add_argument('--unblind', help='for limit unbliding', action="store_true")
parser.add_argument('--verbose','-v', dest='verbose', help='for combine verbose', action="store_true")
parser.add_argument('--rMax',dest='rMax', default=5, type=float)
parser.add_argument('--signal_template', type=str, default = 'CGToBHpm_a_MASS_rttRTT_rtcRTC')
parser.add_argument('--analysis_name', type=str, default = 'bH')
parser.add_argument('--signal_xsec', action='store_true')
parser.add_argument('--sample_json', type=str, default='../data/sample.json')
parser.add_argument('--Scan2D', action='store_true')
parser.add_argument('--Scan2DNLL', action = 'store_true')
parser.add_argument('--Significance', action = 'store_true')
parser.add_argument('--POI_name', type=str, default='r_3b')
parser.add_argument('--model_name', type=str, default='g2HDM_separate')
parser.add_argument('--ratio_file', type=str, default=None)
parser.add_argument('--coupling_varied', type=str, default='best_rtt_rtc')
parser.add_argument('--all_signal', action = 'store_true')
parser.add_argument('--fastScan', action = 'store_true')
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
######################
## All Signal plot  ##
######################

all_signal = []
if args.all_signal:
  for rtt_ in ["0.1", "0.4", "0.6", "1.0"]:
      for rtc_ in ["0.1", "0.4", "0.6", "1.0"]:
          rtt_str = str(rtt_).replace(".","p")
          rtc_str = str(rtc_).replace(".","p")
          all_signal.append('_'.join(["rtt" + rtt_str, "rtc"+rtc_str]))


print("datacards_{}_{}/log".format(year, analysis_name))
CheckDir("datacards_{}_{}/log".format(year, analysis_name),True)
start_time = time.time()

RL  = RunLimits(year=year, analysis= analysis_name, region=region, channel=channel, postfix="asimov", unblind=args.unblind, verbose=args.verbose, rMax=args.rMax, signal_param=signal_param, outputdir = args.outputdir, all_signal = all_signal)

if args.reset_outputfiles:
    CheckFile(RL.limitlog,True)
    CheckFile(RL.limit_root_file,True)
else:pass
#print ("self.limitlog: ",RL.limitlog)

if args.plot_only:




  signal_xsec_TGraph = None
  if args.signal_xsec:
    signal_xsec_TGraph = dict()
    signal_xsec_TGraph['color'] = dict()
    if args.coupling_varied == "best_rtt_rtc":
        print ("here 1")
        # Vary rtc
        for rtc_ in [0.4, 1.0]:
            signal_xsec = array('d')
            signal_xsec_up = array('d')
            signal_xsec_do = array('d')
            mass_bin    = array('d')
            errx = array('d')
            for imass in mass_points:
                try:
                    xsec = df_sig_xsec[(df_sig_xsec['Mass'] == int(imass)) & (abs(df_sig_xsec['rtt'] - args.rtt) < 1e-5) & (abs(df_sig_xsec['rtc'] - rtc_) < 1e-5)]['xsec'].iloc[0]
                    xsec_err = df_sig_xsec_err[(df_sig_xsec_err['Mass'] == int(imass)) & (abs(df_sig_xsec_err['rtt'] - args.rtt) < 1e-5) & ((df_sig_xsec_err['rtc'] - rtc_) < 1e-5)]['total_unc'].iloc[0]

                    signal_xsec.append(xsec)
                    signal_xsec_up.append(xsec*xsec_err/100.)
                    signal_xsec_do.append(xsec*xsec_err/100.)
                    mass_bin.append(float(imass))
                    errx.append(0.0)
                except Exception as e:
                    print(e)
                    print(imass, args.rtt, rtc_, 'no points')
            signal_xsec_TGraph["#rho_{tt}=%.1f, #rho_{tc}=%.1f"%(args.rtt, rtc_)] = ROOT.TGraphAsymmErrors(len(mass_bin), mass_bin, signal_xsec, errx, errx, signal_xsec_up, signal_xsec_do)
            signal_xsec_TGraph['color']["#rho_{tt}=%.1f, #rho_{tc}=%.1f"%(args.rtt, rtc_)] = get_color_from_value(rtc_, 0.0, 1.1)
        # Vary rtt
        for rtt_ in [0.1]:
            signal_xsec = array('d')
            signal_xsec_up = array('d')
            signal_xsec_do = array('d')
            mass_bin    = array('d')
            errx = array('d')
            for imass in mass_points:
                try:
                    xsec = df_sig_xsec[(df_sig_xsec['Mass'] == int(imass)) & (abs(df_sig_xsec['rtt'] -rtt_) < 1e-5) & (abs(df_sig_xsec['rtc'] - args.rtc) < 1e-5)]['xsec'].iloc[0]
                    xsec_err = df_sig_xsec_err[(df_sig_xsec_err['Mass'] == int(imass)) & (abs(df_sig_xsec_err['rtt'] - rtt_) < 1e-5) & ((df_sig_xsec_err['rtc'] - args.rtc) < 1e-5)]['total_unc'].iloc[0]

                    signal_xsec.append(xsec)
                    signal_xsec_up.append(xsec*xsec_err/100.)
                    signal_xsec_do.append(xsec*xsec_err/100.)
                    mass_bin.append(float(imass))
                    errx.append(0.0)
                except:
                    print(imass, rtt_, args.rtc, 'no points')
            signal_xsec_TGraph["#rho_{tt}=%.1f, #rho_{tc}=%.1f"%(rtt_, args.rtc)] = ROOT.TGraphAsymmErrors(len(mass_bin), mass_bin, signal_xsec, errx, errx, signal_xsec_up, signal_xsec_do)
            signal_xsec_TGraph['color']["#rho_{tt}=%.1f, #rho_{tc}=%.1f"%(rtt_, args.rtc)] = get_color_from_value(rtt_+0.3, 0.0, 1.1) #gkole(fixme color in better way)

    elif args.coupling_varied == "rtt":
        for rtt_ in [0.1, 0.4, 0.6, 1.0]:
            signal_xsec = array('d')
            signal_xsec_up = array('d')
            signal_xsec_do = array('d')
            mass_bin    = array('d')
            errx = array('d')
            for imass in mass_points:
                try:
                    xsec = df_sig_xsec[(df_sig_xsec['Mass'] == int(imass)) & (abs(df_sig_xsec['rtt'] -rtt_) < 1e-5) & (abs(df_sig_xsec['rtc'] - args.rtc) < 1e-5)]['xsec'].iloc[0]
                    xsec_err = df_sig_xsec_err[(df_sig_xsec_err['Mass'] == int(imass)) & (abs(df_sig_xsec_err['rtt'] - rtt_) < 1e-5) & ((df_sig_xsec_err['rtc'] - args.rtc) < 1e-5)]['total_unc'].iloc[0]

                    signal_xsec.append(xsec)
                    signal_xsec_up.append(xsec*xsec_err/100.)
                    signal_xsec_do.append(xsec*xsec_err/100.)
                    mass_bin.append(float(imass))
                    errx.append(0.0)
                except:
                    print(imass, rtt_, args.rtc, 'no points')
            signal_xsec_TGraph["#rho_{tt}=%.1f, #rho_{tc}=%.1f"%(rtt_, args.rtc)] = ROOT.TGraphAsymmErrors(len(mass_bin), mass_bin, signal_xsec, errx, errx, signal_xsec_up, signal_xsec_do)
            signal_xsec_TGraph['color']["#rho_{tt}=%.1f, #rho_{tc}=%.1f"%(rtt_, args.rtc)] = get_color_from_value(rtt_, 0.0, 1.1)
    else:
        for rtc_ in [0.1, 0.4, 0.6, 1.0]:
            signal_xsec = array('d')
            signal_xsec_up = array('d')
            signal_xsec_do = array('d')
            mass_bin    = array('d')
            errx = array('d')
            for imass in mass_points:
                try:
                    xsec = df_sig_xsec[(df_sig_xsec['Mass'] == int(imass)) & (abs(df_sig_xsec['rtt'] - args.rtt) < 1e-5) & (abs(df_sig_xsec['rtc'] - rtc_) < 1e-5)]['xsec'].iloc[0]
                    xsec_err = df_sig_xsec_err[(df_sig_xsec_err['Mass'] == int(imass)) & (abs(df_sig_xsec_err['rtt'] - args.rtt) < 1e-5) & ((df_sig_xsec_err['rtc'] - rtc_) < 1e-5)]['total_unc'].iloc[0]

                    signal_xsec.append(xsec)
                    signal_xsec_up.append(xsec*xsec_err/100.)
                    signal_xsec_do.append(xsec*xsec_err/100.)
                    mass_bin.append(float(imass))
                    errx.append(0.0)
                except Exception as e:
                    print(e)
                    print(imass, args.rtt, rtc_, 'no points')
            signal_xsec_TGraph["#rho_{tt}=%.1f, #rho_{tc}=%.1f"%(args.rtt, rtc_)] = ROOT.TGraphAsymmErrors(len(mass_bin), mass_bin, signal_xsec, errx, errx, signal_xsec_up, signal_xsec_do)
            signal_xsec_TGraph['color']["#rho_{tt}=%.1f, #rho_{tc}=%.1f"%(args.rtt, rtc_)] = get_color_from_value(rtc_, 0.0, 1.1)

  if args.Scan2DNLL:
      for imass in mass_points:
          mH = str(imass)
          RL.Save2DNLL(outputdir = args.outputdir,mass_point=Higgs_Mass_Name+str(imass), POI_name = args.POI_name, model_name = args.model_name, ratio_file = args.ratio_file, df_sig_xsec = df_sig_xsec)



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
      RL.SaveLimitPdf1D(outputdir=args.outputdir, y_max=args.plot_y_max, y_min=args.plot_y_min, signal_xsec_TGraph=signal_xsec_TGraph, coupling_varied = args.coupling_varied)

    print(TGraph_File_dict)
    Plot_2D_Limit_For(TGraph_File_dict, args.unblind, args.year, args.channel, args.outputdir, args.Masses, y_axis_title = 'R_{b}', ratio_file = args.ratio_file, signal_xsec_TGraph = signal_xsec_TGraph)
    Plot_1D_Limit_For(TGraph_File_dict, args.unblind, y_max=args.plot_y_max, y_min=args.plot_y_min, year=[args.year], region=[args.region], channel=[args.channel], outputFolder=args.outputdir, Masses=args.Masses, mode = "Rb", legend_dict={(0.1*0):'pp\\rightarrow bH^{+}', (0.1*10):'pp\\rightarrow bH^{+} + H^{+}'}, AN=True)

  elif args.Significance:
    RL.TextFileToSignificancePlot(Masses = mass_points, Eras = args.year_for_plot, Regions = args.region_for_plot, mode = 'era')
#    RL.TextFileToSignificancePlot(Masses = mass_points, Eras = args.year_for_plot, Regions = args.region_for_plot, mode = 'region')

  else:
    TGraph_File = RL.TextFileToRootGraphs(Masses=mass_points, Higgs=Higgs_Mass_Name)
    CheckDir(args.outputdir,True)
    #RL.SaveLimitPdf1D(outputdir=args.outputdir,y_max=args.plot_y_max,y_min=args.plot_y_min)
    RL.SaveLimitPdf1D(outputdir=args.outputdir,y_max=args.plot_y_max,y_min=args.plot_y_min, signal_xsec_TGraph=signal_xsec_TGraph, coupling_varied = args.coupling_varied) #gkole-9Feb2025
else:
    counter=0
    template_card = "{dc_dir}/{year}/{signal}/{signal}_{year}_{region}_{channel}.txt".format(dc_dir=args.datacard_dir, year=year, signal=signal_name_template, region=region, channel=channel)
    #datacards_2016apv_ttu/ttu_rtu04_datacard_2016apv_SR_em_em_MA1000.txt
    for imass in mass_points:
        mH = str(imass)
        card_name = template_card.replace("MASS", mH)
        if args.Scan2DNLL:
          RL.Scan2DNLL(card_name.replace('txt','root'), POI_name = args.POI_name, asimov=True, mass_point=Higgs_Mass_Name+str(imass), dc_dir=args.datacard_dir, out_dir=os.path.join(args.outputdir, '2DNLL'), model_name = args.model_name, cminDefaultMinimizerStrategy=args.cminDefaultMinimizerStrategy, cminDefaultMinimizerTolerance=args.cminDefaultMinimizerTolerance, fastScan = args.fastScan)


        elif args.Scan2D:
          mode_ = 'w'
          for Rb in [0.1 * i for i in range(11)]:
            extraCommand = '--redefineSignalPOIs {POI}  --setParameters Rb={Rb},{POI}=0.0 --freezeParameters Rb --defineBackgroundOnlyModelParameters {POI}=0,Rb={Rb}'.format(Rb=Rb, POI=args.POI_name)
            logname = RL.getLimits(card_name.replace('txt','root'),asimov=False, mass_point=Higgs_Mass_Name+str(imass),cminDefaultMinimizerStrategy=args.cminDefaultMinimizerStrategy, rAbsAcc=args.rAbsAcc, cminDefaultMinimizerTolerance=args.cminDefaultMinimizerTolerance, dc_dir=args.datacard_dir, log_dir=os.path.join(args.outputdir, 'datacard_log'), logname=card_name.replace('.txt','_%s_Rb%.1f.log'%(args.POI_name, Rb)), extraCommand = extraCommand)
            param_list=(Higgs_Mass_Name,mH,RL.signal_str_) # e.g., (200,0.4)
            print('post logname:', logname)
            limitlogfile = RL.LogToLimitList(logname, param_list, mode_, postfix='_%s_Rb%.1f'%(args.POI_name, Rb), POI=args.POI_name)

        elif args.Significance:
          logname = RL.getSignificance(card_name, mass_point=Higgs_Mass_Name+str(imass), dc_dir=args.datacard_dir, log_dir = 'significance_log', cminDefaultMinimizerStrategy=args.cminDefaultMinimizerStrategy, rAbsAcc=args.rAbsAcc, cminDefaultMinimizerTolerance=args.cminDefaultMinimizerTolerance)
          param_list = (Higgs_Mass_Name,mH,RL.signal_str_) # e.g., (200,0.4)
          significance_log_file = RL.LogToSignificanceList(logname, param_list, 'w')

        else:
          logname = RL.getLimits(card_name,asimov=False, mass_point=Higgs_Mass_Name+str(imass),cminDefaultMinimizerStrategy=args.cminDefaultMinimizerStrategy, rAbsAcc=args.rAbsAcc, cminDefaultMinimizerTolerance=args.cminDefaultMinimizerTolerance, dc_dir=args.datacard_dir, log_dir='datacard_log')
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
