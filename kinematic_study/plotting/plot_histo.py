import ROOT
import os, sys, shutil
import math
import json
import optparse, argparse
from collections import OrderedDict
from math import sqrt
thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
print (thisdir)
sys.path.append('../../python')
from plotstyle import *
from common import *

def Generate_Histogram(era, indir, outdir, Labels, Black_list, logy, plot_ratio, unblind, signals, region, channel, only_signal, overflow=False, normalize=False):

  Indir = os.path.join(indir, era, region, channel)

  ##########################
  ## Load Histogram Info  ##
  ##########################

  jsonfile   = open(os.path.join("../../data", "histogram.json"))
  Histograms = json.load(jsonfile, encoding='utf-8', object_pairs_hook=OrderedDict)
  jsonfile.close()

  #########################
  ## Add Extra Histogram ##
  #########################

  Histograms['cutflow'] = {'Label': Labels, 'Title': ';cutflow;nEvents/bin'}
  

  for histogram in Histograms:

    ##################
    ## Filter Label ##
    ##################

    Flag = False
    for Label in Labels:
      if Label in Histograms[histogram]["Label"]: Flag = True
    for Label in Black_list:
      if Label in Histograms[histogram]["Label"]: Flag = False
    if not Flag: continue

    print("Plotting", histogram)

    ######################
    ## Load sample list ##
    ######################

    json_file_name = "../../data/sample_%s.json"%era
    jsonfile = open(json_file_name)
    samples  = json.load(jsonfile, encoding='utf-8', object_pairs_hook=OrderedDict)
    jsonfile.close()
   

    ####################
    ## Canvas Setting ##
    ####################

    # TODO plot_ratio
    if not only_signal: 
      canvas = DataMCCanvas(" "," ", Lumi[era])
      canvas.legend.setPosition(0.35,0.77,0.8,0.9)
    else:
      canvas = SimpleCanvas(" ", " ", Lumi[era]) 
    canvas.ytitle = "nEvents/bin"
    
    ####################
    ## Read Histogram ##
    ####################

    for data_type in [["MC", "Background"], ["Data"], ["MC", "Signal"]]:
      File_List      = Get_Sample(json_file_name, data_type, era, withTail=True) # Use all the MC backgrounds
      Process_List   = Get_Sample(json_file_name, data_type, era, withTail=False)
      Histogram = dict()
      Integral  = dict()

      if only_signal and "Signal" not in data_type: continue

      for sample in Process_List:

        if "Signal" in data_type and not sample in signals: continue # Do not plot signal that is not required.
        if "Region" in samples[sample] and region not in samples[sample]["Region"]: continue
        if "Channel" in samples[sample] and channel not in samples[sample]["Channel"]:
          print("Do not satisfied channel criteria. sample_name: {}, channel: {}".format(sample, channel))
          continue


        ##################################
        ## Lumi & cross section scaling ##
        ##################################

        #if "MC" in data_type:  # MC normalize with lumi x cross section
        #  nDAS  = 0
        #  for file_ in File_List:
        #    if ((sample + "_") in file_) or ((sample + ".") in file_):
        #      ftemp = ROOT.TFile.Open(os.path.join(inputFile_path[era], file_), "READ")
        #      nDAS += ftemp.Get('nEventsGenWeighted').GetBinContent(1)
        #      ftemp.Close()
        #  norm_factor = Lumi[era]*samples[sample]['xsec']/float(nDAS)
        #else: # data doesn't need to be normalized by lumi x cross section
        #  norm_factor = 1.0

        ##########################
        ## Fetch Hist from File ##
        ##########################

        ftemp = ROOT.TFile.Open(os.path.join(Indir, sample + ".root"), "READ")
        htemp = ftemp.Get(str(histogram)).Clone()
        htemp.SetDirectory(0)
        ftemp.Close()
   
        ##############
        ## Overflow ##
        ##############

        if overflow:
          htemp = overunder_flowbin(htemp)

        ###################
        # Scale and Rebin #
        ###################

        # htemp.Scale(norm_factor)  # Scale done by previous step already
        if not(histogram == 'cutflow'): # only cutflow is special
          htemp.Rebin(int(htemp.GetNbinsX()/Histograms[histogram]["nbin"]))

        ##################################
        ## Add Hist to correspond group ##
        ##################################

        category = samples[sample]['Category']
        if category not in Histogram:
          Histogram[category] = htemp.Clone()
          Integral[category]  = htemp.Integral()
        else:
          Histogram[category].Add(htemp.Clone())
          Integral[category] += htemp.Integral()


      ###################
      ## Add To Canvas ##
      ###################
  
      sig_idx = 0
      for idx, sample_ in enumerate(Histogram):
      
        #################
        ## Normalized  ##
        ################# 
        if normalize and Integral[sample_] > 0:
          Histogram[sample_].Scale(1./Integral[sample_])
          canvas.ytitle = "Normalized"

        if "Background" in data_type:
          canvas.addStacked(Histogram[sample_], title = "%s"%(sample_), color = Color_Dict_ref[sample_], opt='F')
        elif "Signal" in data_type:
          color = Color_List_Signal[sig_idx]
          sig_idx += 1
          if not isinstance(canvas, DataMCCanvas):
            Histogram[sample_].SetName(Histogram[sample_].GetName() + "_" + sample_) # Otherwise, the legend will point to the sample histogram
            canvas.addHistogram(Histogram[sample_], drawOpt = 'HIST E')
            canvas.legend.add(Histogram[sample_], title = sample_, opt = 'LP', color = color, fstyle = 0, lwidth = 4)
          else:
            canvas.addSignal(Histogram[sample_], title = sample_, color = color)
        elif "Data" in data_type:
          canvas.addObs(Histogram[sample_])
    
    #############################
    ## Plot Setting for Canvas ##
    #############################

    if isinstance(canvas, DataMCCanvas):

      ############################################
      ##  Special treatment for alphabetic axis ##
      ############################################

      if(histogram == 'cutflow'):
        canvas.xaxis.SetNdivisions(110)
        canvas.xaxis.CenterLabels()
        ref_xaxis = canvas._histograms[1].GetXaxis()
        for idx in range(ref_xaxis.GetNbins()):
          canvas.xaxis.ChangeLabel(idx+1,45,0.022,-1,-1,-1,ref_xaxis.GetBinLabel(idx+1))

      canvas.rtitle = str("Data/MC") 
      canvas.yaxis.SetMaxDigits(4)
 
    canvas.applyStyles()
    canvas.printWeb(os.path.join(outdir,'plot',era,region,channel), histogram, logy=logy)
  
if __name__ == "__main__":

  usage  = 'usage: %prog [options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('-e', '--era',    dest='era', help='[2016apv/2106postapv/2017/2018]', default='2017', type=str)
  parser.add_argument('-i', '--indir',  dest='indir', help='input directory', default='./', type=str)
  parser.add_argument('-o', '--outdir', dest='outdir', help='output directory', default=None, type=str)
  parser.add_argument("--Labels", dest = 'Labels', default = ['Normal'], nargs='+')
  parser.add_argument("--Black_list", dest = 'Black_list', default = [], nargs='+')
  parser.add_argument("--logy", dest = 'logy', action = 'store_true', default = False)
  parser.add_argument("--plot_ratio", dest = 'plot_ratio', action = 'store_true', default = False)
  parser.add_argument("--unblind", dest = 'unblind', action = 'store_true', default = False)
  parser.add_argument("--signals", dest = 'signals', default = ["CGToBHpm_a_350_rtt06_rtc04","CGToBHpm_a_500_rtt06_rtc04","CGToBHpm_a_800_rtt06_rtc04","CGToBHpm_a_1000_rtt06_rtc04"], type=str, nargs = '+')
  parser.add_argument("--region_json", dest = 'region_json', default = '../../data/cut.json')
  parser.add_argument("--channels", dest = 'channels', default = ['all'], nargs = '+')
  parser.add_argument('--region', dest = 'region', default = ['all'], type=str, nargs = '+')
  parser.add_argument("--only_signal", dest = 'only_signal', action = 'store_true')
  parser.add_argument("--overflow", dest = 'overflow', action = 'store_true')
  parser.add_argument("--normalize", dest = 'normalize', action = 'store_true')
  args = parser.parse_args()

  if args.outdir is None:
    args.outdir = args.indir

  args.plot_ratio = (args.plot_ratio and args.unblind)
  args.plot_ratio = True # develop purpose

  os.system('cp %s/../../python/common.py .'%cwd)
  from common import prepare_shell, Get_Sample, cmsswBase, inputFile_path, read_json, Lumi, inputFile_path
 
  # List of regions
  region_channel_dict = dict()
  cut_regions = read_json(args.region_json)
  if 'all' in args.region:
    for region_ in cut_regions:
      region_channel_dict[region_] = []
  else:
    for region_ in args.region:
      region_channel_dict[region_] = []

  # List of channels
  for region_ in region_channel_dict:
    if 'all' in args.channels:
      for channel_ in cut_regions[region_]["channel_cut"]:
        region_channel_dict[region_].append(channel_)
    else:
      region_channel_dict[region_] = args.channels
 
  for region in region_channel_dict:
    for channel in region_channel_dict[region]: 
      Generate_Histogram(args.era, args.indir, args.outdir, args.Labels, args.Black_list, args.logy, args.plot_ratio, args.unblind, args.signals, region, channel, args.only_signal,args.overflow, normalize = args.normalize)

  

