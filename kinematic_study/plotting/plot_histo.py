import ROOT
import os, sys, shutil
import math
import json, array
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

ROOT.gROOT.SetBatch(True)

def Generate_Histogram(era, indir, outdir, Labels, Black_list, logy, plot_ratio, unblind, partial_blind, signals, region, channel, only_signal, nooverflow=False, normalize=False, histogram_json="../../data/histogram.json", sample_json="../../data/sample.json", block_sample = [], Yield=False, ymax=None, ymin=None, ratio_max=1.25, ratio_min=0.75, ratio_Ndiv=210, cutflow = False, noQCDsmooth = True):

  Indir = os.path.join(indir, era, region, channel)

  ##########################
  ## Load Histogram Info  ##
  ##########################

  Histograms = read_json(histogram_json)

  #########################
  ## Add Extra Histogram ##
  #########################

  if cutflow:
    Histograms['cutflow'] = {'Label': Labels, 'Title': ';cutflow;Events/bin'}


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

    samples  = read_json(sample_json)


    ####################
    ## Canvas Setting ##
    ####################
    # y coordinates will be adjusted later
    resultLegend = Legend(0.60, 0.60, 0.90, 0.65)
    resultLegend.SetTextSize(0.02)
    resultLegend.SetX2(0.95)
    # resultLegend.add('stat', title = 'stat-unc', opt = 'LF', color = ROOT.kBlack, lstyle = ROOT.kDashed, lwidth = 2, fstyle = 3004, mstyle = 8, msize = 0.8)

    # TODO plot_ratio
    if not only_signal:
      canvas = DataMCCanvas(" "," ", Lumi[era])
      # canvas.legend.setPosition(0.35,0.77,0.8,0.9)
      canvas.legend.setPosition(0.20, 0.73, 0.95, 0.92)
      canvas.raxis.SetNdivisions(ratio_Ndiv)
      canvas.rlimits = (ratio_min, ratio_max)
      if ymin is not None and ymax is not None:
        canvas.ylimits = (ymin, ymax)
        # canvas.ylimits = (1e-1, 1e8)
    else:
      canvas = SimpleCanvas(" ", " ", Lumi[era])
    if Yield:
      canvas.legend.SetTextSize(0.02)
      canvas.legend.SetX2(0.95)

    canvas.ytitle = "Events/bin"

    ####################
    ## Read Histogram ##
    ####################

    Histo_exist_in_file = True
    for data_type in [["MC", "Background"], ["Data"], ["MC", "Signal"]]:
      if not unblind and "Data" in data_type: continue
      if era == "2025":
        Process_List   = Get_Sample(sample_json, data_type, "2017", withTail=False)
      else:
        Process_List   = Get_Sample(sample_json, data_type, era, withTail=False)

      Histogram = dict()
      Integral  = dict()

      if only_signal and "Signal" not in data_type: continue

      for sample in Process_List:

        if "Signal" in data_type and not sample in signals: continue # Do not plot signal that is not required.
        if "Region" in samples[sample] and region not in samples[sample]["Region"]: continue
        if "Channel" in samples[sample] and channel not in samples[sample]["Channel"]:
          print("Do not satisfied channel criteria. sample_name: {}, channel: {}".format(sample, channel))
          continue
        category = samples[sample]['Category']
        if category in block_sample: continue

        if 'SubProcess' in samples[sample]:
          subprocess = []
          for sub in samples[sample]['SubProcess']:
            subprocess.append(sub)
        else:
          subprocess = [sample]

        for subprocess_ in subprocess:
          if "Signal" in data_type and not os.path.exists(os.path.join(Indir, subprocess_+".root")): continue


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

          ftemp = ROOT.TFile.Open(os.path.join(Indir, subprocess_ + ".root"), "READ")
          # Good debug tips
          # print ("1-->", os.path.join(Indir, subprocess_ + ".root"))
          # print ("2-->", histogram)
          try:
            htemp = ftemp.Get(str(histogram)).Clone()
          except:
            Histo_exist_in_file = False
            continue
          htemp.SetDirectory(0)
          ftemp.Close()

          ##############
          ## NO Overflow ##
          ##############

          if nooverflow:
            print ('Over and upderflow is NOT included')
          else:
            htemp = overunder_flowbin(htemp)

          ###################
          # Scale and Rebin #
          ###################

          # htemp.Scale(norm_factor)  # Scale done by previous step already
          if not(histogram == 'cutflow'): # only cutflow is special
            # print ("input binning", Histograms[histogram]["nbin"])
            try: # (Histograms[histogram]["plottingbins"])
              binning = array.array('d', Histograms[histogram]["plottingbins"])
              htemp = htemp.Rebin(len(binning)-1, "htemp", binning )
            except:
              htemp.Rebin(int(htemp.GetNbinsX()/Histograms[histogram]["nbin"]))
            # h = h.Rebin(len(bins)-1, "h", bins)
            # htemp.GetXaxis().SetRangeUser(float(Histograms[histogram]["xlow"]), float(Histograms[histogram]["xhigh"])) # this does not work (23Jul2024)
            # print ("xmin: ", htemp.GetXaxis().GetXmin())
            # print ("nbins: ", htemp.GetNbinsX())
            # print ("histogram name", histogram )
            if (histogram == 'n_tight_jet' or histogram == 'n_bjet_DeepB_v'):
              htemp.GetXaxis().SetNdivisions(505)
              htemp.GetXaxis().CenterLabels()



          ##################################
          ## Add Hist to correspond group ##
          ##################################
          # if histogram == 'cutflow':
          #  if 'WJets' in subprocess_:
          #    print ("Name: ", subprocess_, " and Integral:  ", round(htemp.Integral(), 2))

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
        if noQCDsmooth:
          if 'QCD' in sample_:
            print("smoothing: ", sample_)
            original_integral = Histogram[sample_].Integral()
            # print ("original_integral: ", original_integral)
            Histogram[sample_].Smooth(10)
            after_integral = Histogram[sample_].Integral()
            # print ("after_integral: ", after_integral)
            if (after_integral> 0): Histogram[sample_].Scale(original_integral/after_integral)
            # print ("final_integral: ", Histogram[sample_].Integral())
            # Uncertainties add 30%
            # Loop over each bin in the histogram and increase the error (uncertainty)
            for bin in range(1, Histogram[sample_].GetNbinsX() + 1):
              # Get the current bin content and uncertainty (error)
              # current_error = Histogram[sample_].GetBinError(bin)
              # Increase the error by 30%
              #new_error = current_error * 1.30

              ## fix to 30% error
              #new_error = 0.3*Histogram[sample_].GetBinContent(bin)
              # fix to 50% error
              new_error = 0.5*Histogram[sample_].GetBinContent(bin)
              # Set the new error for the bin
              Histogram[sample_].SetBinError(bin, new_error)
        #################
        ## Normalized  ##
        #################
        if normalize and Integral[sample_] > 0:
          Histogram[sample_].Scale(1./Integral[sample_])
          canvas.ytitle = "Normalized"

        if "Background" in data_type:
          if Yield:
            if "TT" in sample_:
              for bin in range(1, Histogram[sample_].GetNbinsX() + 1):
                syst_err = 0.10 * Histogram[sample_].GetBinContent(bin)
                stat_err = Histogram[sample_].GetBinError(bin)
                total_err = (stat_err**2 + syst_err**2)**0.5
                Histogram[sample_].SetBinError(bin, total_err)
              canvas.addStacked(Histogram[sample_], title = "%s [%.0f]"%(sample_, Integral[sample_]), color = Color_Dict_ref[sample_], opt='F')
            else:
              canvas.addStacked(Histogram[sample_], title = "%s [%.0f]"%(sample_, Integral[sample_]), color = Color_Dict_ref[sample_], opt='F')
            # Assuming sample_ is a string and Histogram[sample_].Integral() returns a float
            print(f"Name: {sample_:<20} Integral: {Histogram[sample_].Integral():>10.2f}")
          else:
            canvas.addStacked(Histogram[sample_], title = "%s"%(sample_), color = Color_Dict_ref[sample_], opt='F')

          # # trying to add systematics:
          # if "TT" in sample_:
          #   print ("Add TT syst: -> ")
          #   print ("sample_ again: -> ", sample_)
          #   tt_syst_band = Histogram[sample_].Clone(sample_ + "_tt_syst_band")
          #   for bin in range(1, tt_syst_band.GetNbinsX() + 1):
          #       syst_err = 0.30 * tt_syst_band.GetBinContent(bin)
          #       tt_syst_band.SetBinError(bin, syst_err)
          #   tt_syst_band.SetFillColor(ROOT.kRed)
          #   tt_syst_band.SetFillStyle(1001)
          #   tt_syst_band.SetLineColor(ROOT.kRed)
          #   idx_syst = canvas.addExtra(tt_syst_band, drawOpt="E2")
          #   # Add legend entry for the band
          #   resultLegend.add('tt_syst', title='TT syst. (30%)', opt='F', color=ROOT.kRed, fstyle=3002)
          #   canvas.legend.add(tt_syst_band, title='TT syst. (30%)', opt='F', color=ROOT.kRed, fstyle=3002)

          #   #FIXME the ratio (if possible)
          #   ratio_band = tt_syst_band.Clone("tt_syst_ratio_band")
          #   nominal = Histogram["TT"]
          #   for bin in range(1, ratio_band.GetNbinsX() + 1):
          #       nom_val = nominal.GetBinContent(bin)
          #       syst_err = ratio_band.GetBinError(bin)
          #       # Avoid division by zero
          #       if nom_val > 0:
          #           ratio_band.SetBinContent(bin, 1.0)  # Centered at 1
          #           ratio_band.SetBinError(bin, syst_err / nom_val)
          #       else:
          #           ratio_band.SetBinContent(bin, 0)
          #           ratio_band.SetBinError(bin, 0)
          #   # for bin in range(1, ratio_band.GetNbinsX() + 1):
          #   #   print ("bin: ", bin , " ratio_band.GetBinContent(bin): ", ratio_band.GetBinContent(bin))
          #   #   print ("bin: ", bin , " ratio_band.GetBinError(bin): ", ratio_band.GetBinError(bin))
          #   ratio_band.SetFillColor(ROOT.kRed)
          #   ratio_band.SetFillStyle(3002)
          #   ratio_band.SetLineColor(ROOT.kRed)
          #   ratio_band.absolute = True
          #   print("absolute flag:", getattr(ratio_band, "absolute", False))
          #   idx_ratio_band = canvas.addExtraRatio(ratio_band, drawOpt="E2")

          #   # resultLegend.add('tt_syst_ratio', title='TT syst. (30%)', opt='F', color=ROOT.kRed, fstyle=3002)
          #   # canvas.legend.add(ratio_band, title='TT syst. (30%)', opt='F', color=ROOT.kRed, fstyle=3002)

        elif "Signal" in data_type:
          color = Color_List_Signal[sig_idx]
          sig_idx += 1
          Histogram[sample_].Scale(100) #Scale the signal by 10 times (DOES work, why ?) fixme gkole as general --sigscale
          if not isinstance(canvas, DataMCCanvas):
            Histogram[sample_].SetName(Histogram[sample_].GetName() + "_" + sample_) # Otherwise, the legend will point to the sample histogram
            canvas.addHistogram(Histogram[sample_], drawOpt = 'HIST E')
            canvas.legend.add(Histogram[sample_], title = sample_, opt = 'LP', color = color, fstyle = 0, lwidth = 4)
            resultLegend.apply('stat', Histogram[sample_], opt = 'L') #this is working (but need to understand more ?)
          else:
            canvas.addSignal(Histogram[sample_], title = sample_+"x 100", color = color)
        elif "Data" in data_type and unblind:
          print(f"Name: {sample_:<20} Integral: {Histogram[sample_].Integral():>10.2f}")
          if partial_blind: #partial_blind:
            # show_ranges = [(binsx[0], sb1_edge), (sb2_edge, binsx[-1])]
            if histogram == 'j1_pt': #gkole its hard coded but can change if needed (as well the show_ranges)
              print ("partial_blinding applied to: ", histogram)
              show_ranges = [(50.0, 150.0)]
              blind_data_hist = apply_blinding(Histogram[sample_], ranges = show_ranges)
              canvas.addObs(blind_data_hist, title = 'Data', drawOpt = 'X0 P E1')
            else:
              canvas.addObs(Histogram[sample_], title = 'Data', drawOpt = 'X0 P E1')
          else:
            canvas.addObs(Histogram[sample_], title = 'Data', drawOpt = 'X0 P E1')

    #############################
    ## Plot Setting for Canvas ##
    #############################
    if not Histo_exist_in_file:
      pass # TODO: happens when there is zero entries
#      continue

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

      canvas.rtitle = str("Obs/Exp")
      canvas.yaxis.SetMaxDigits(4)

    # Extract x-axis title from the Title string in the JSON
    title_str = Histograms[histogram]["Title"]
    title_parts = title_str.split(";")
    if len(title_parts) > 1:
      xaxis_title = title_parts[1]
    else:
      xaxis_title = ""  # fallback if not found

    canvas.xtitle = xaxis_title

    # Total backgrounds (as sheed plotted on stack)
    totalbkgs = canvas.drawTotalUncertaintyBand(rel_unc=0.0, color=ROOT.kGray + 2, fstyle=3345)  # 0% uncertainty band
    canvas.addExtra(totalbkgs, drawOpt="E2")

    print('Generating png')
    resultLegend.construct()

    # canvas.legend.add(tt_syst_band, title='TT syst. (30%)', opt='F', color=ROOT.kRed, fstyle=3002)
    canvas.addObject(resultLegend.legend, clone = False) # commented out to remove addtional "stat-unc"

    # add text region and channel
    canvas.addText(channel.replace("_resolved","").replace("ele","e, ").replace("mu","#mu, "), 0.93, 0.74, 0.46, 0.75)
    canvas.addText(region.replace("SR_",""), 1.00, 0.74, 0.48, 0.75)


    canvas.applyStyles()
    if args.unblind:
        outdir_plot = os.path.join(outdir, 'plot', era, region+'_unblind', channel)
    else:
        outdir_plot = os.path.join(outdir, 'plot', era, region, channel)

    if logy:
        outdir_plot = os.path.join(outdir_plot, 'log')

    # Ensure directory exists
    os.makedirs(outdir_plot, exist_ok=True)
    print ("1: ", canvas._sigs)
    print ("2: ", canvas._obs)
    print ("3: ", canvas._bkgs)
    canvas.printWeb(outdir_plot, histogram, logy=logy)

    # Save as .C and .root
    canvas.SaveAs(os.path.join(outdir_plot, f"{histogram}.C"))
    canvas.SaveAs(os.path.join(outdir_plot, f"{histogram}.root"))
    # canvas.applyStyles()
    # if args.unblind:
    #   if logy:
    #     canvas.printWeb(os.path.join(outdir,'plot',era,region+'_unblind',channel,'log'), histogram, logy=logy)
    #   else:
    #     canvas.printWeb(os.path.join(outdir,'plot',era,region+'_unblind',channel), histogram, logy=logy)
    # else:
    #   if logy:
    #     canvas.printWeb(os.path.join(outdir,'plot',era,region,channel,'log'), histogram, logy=logy)
    #   else:
    #     canvas.printWeb(os.path.join(outdir,'plot',era,region,channel), histogram, logy=logy)
    print (100*"=")
if __name__ == "__main__":

  usage  = 'usage: %prog [options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('-e', '--era',    dest='era', help='[2016apv/2016postapv/2017/2018]', default='2017', type=str)
  parser.add_argument('-i', '--indir',  dest='indir', help='input directory', default='./', type=str)
  parser.add_argument('-o', '--outdir', dest='outdir', help='output directory', default=None, type=str)
  parser.add_argument("--Labels", dest = 'Labels', default = ['Normal'], nargs='+')
  parser.add_argument("--Black_list", dest = 'Black_list', default = [], nargs='+')
  parser.add_argument("--logy", dest = 'logy', action = 'store_true', default = False)
  parser.add_argument("--plot_ratio", dest = 'plot_ratio', action = 'store_true', default = False)
  parser.add_argument("--unblind", dest = 'unblind', action = 'store_true', default = False)
  parser.add_argument("--partial_blind", dest= 'partial_blind', action = 'store_true', default=False)
  parser.add_argument("--signals", dest = 'signals', default = ["CGToBHpm_a_350_rtt06_rtc04","CGToBHpm_a_500_rtt06_rtc04","CGToBHpm_a_800_rtt06_rtc04","CGToBHpm_a_1000_rtt06_rtc04"], type=str, nargs = '+')
  parser.add_argument("--region_json", dest = 'region_json', default = '../../data/cut.json')
  parser.add_argument("--channels", dest = 'channels', default = ['all'], nargs = '+')
  parser.add_argument('--region', dest = 'region', default = ['all'], type=str, nargs = '+')
  parser.add_argument('--sample_json', dest='sample_json', default='../../data/sample.json', type=str)
  parser.add_argument('--histogram_json', dest='histogram_json', default='../../data/histogram.json', type=str)
  parser.add_argument("--only_signal", dest = 'only_signal', action = 'store_true')
  parser.add_argument("--nooverflow", dest = 'nooverflow', action = 'store_true')
  parser.add_argument("--normalize", dest = 'normalize', action = 'store_true')
  parser.add_argument("--block_sample", dest='block_sample', nargs='+', default=[])
  parser.add_argument("--ymax", dest='ymax', type=float)
  parser.add_argument("--ymin", dest='ymin', type=float)
  parser.add_argument("--ratio_max", dest='ratio_max', default=1.25, type=float)
  parser.add_argument("--ratio_min", dest='ratio_min', default=0.75, type=float)
  parser.add_argument("--ratio_Ndiv", dest='ratio_Ndiv', default=205, type=int)
  parser.add_argument("--Yield", action = 'store_true', default=False)
  parser.add_argument("--cutflow", action = 'store_true', default=False)
  parser.add_argument("--noQCDsmooth", action = 'store_false', default=True)

  args = parser.parse_args()

  if args.outdir is None:
    args.outdir = args.indir

  args.plot_ratio = (args.plot_ratio and args.unblind)
  args.plot_ratio = True # develop purpose


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

  if args.era == 'all':
    Era = ['2016apv', '2016postapv', '2017', '2018']
  else:
    Era = [args.era]

  for era in Era:
    for region in region_channel_dict:
      for channel in region_channel_dict[region]:
        Generate_Histogram(era, args.indir, args.outdir, args.Labels, args.Black_list, args.logy, args.plot_ratio, args.unblind, args.partial_blind, args.signals, region, channel, args.only_signal,args.nooverflow, normalize = args.normalize, sample_json=args.sample_json, histogram_json=args.histogram_json, block_sample=args.block_sample, Yield=args.Yield, ymax=args.ymax, ymin=args.ymin, ratio_max=args.ratio_max, ratio_min=args.ratio_min, ratio_Ndiv=args.ratio_Ndiv, cutflow = args.cutflow, noQCDsmooth = args.noQCDsmooth)
