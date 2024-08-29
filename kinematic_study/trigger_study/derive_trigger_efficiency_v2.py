import awkward as ak
import numpy as np
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema, BaseSchema
import ROOT
import json
import optparse, argparse
import os, sys
sys.path.insert(1, '../../python')
from common import *
from coffea import processor
import hist
import time 
import matplotlib.pyplot as plt
import uproot
from collections import OrderedDict
ROOT.gStyle.SetOptStat(00000000)
ROOT.gStyle.SetPaintTextFormat(".2f")
from array import array
from plotstyle import *
import re
from runcondor import fileset
from termcolor import cprint
import cmsstyle as CMS


CMS.SetExtraText("Preliminary")
CMS.SetEnergy("13")

def Get_From_TH2(nbinX, x_binnings, hist2D, iy, name):
  TH1_ = ROOT.TH1D(name, name, nbinX, array('d', x_binnings))
  for ix in range(nbinX):
    TH1_.SetBinContent(ix+1, hist2D.GetBinContent(ix+1, iy+1))
    TH1_.SetBinError(ix+1, hist2D.GetBinError(ix+1, iy+1))
  return TH1_

def Draw_TH2(hist, fname, outdir, format_ = ".2f"):
  x_axis = hist.GetXaxis()
  y_axis = hist.GetYaxis()
  nbinX  = x_axis.GetNbins()
  nbinY  = y_axis.GetNbins()
  x_binnings = [x_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinX+1)]
  y_binnings = [y_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinY+1)]

  hist = hist.Clone()
  if 1.442 in y_binnings:
    iy = y_binnings.index(1.442)
    for ix in range(nbinX):
      hist.SetBinContent(ix+1, iy+1, 0)
  c = CMS.cmsCanvas('', min(x_binnings), max(x_binnings), min(y_binnings), max(y_binnings), '', '', square = CMS.kRectangular, extraSpace=0.01, iPos=0, with_z_axis=True)
  ROOT.gStyle.SetPaintTextFormat(format_)
  c.SetLogx()
  hist.GetZaxis().SetRangeUser(0.5, 1.2)
  hist.SetTitle(";pT[GeV];|#eta|")
  CMS.cmsDraw(hist, 'COLZ TEXT E')
  CMS.SetAlternative2DColor(hist, CMS.cmsStyle)
  CMS.UpdatePalettePosition(hist, c)
  CMS.SaveCanvas(c, os.path.join(outdir, '{}.png'.format(fname)), close=False)
  CMS.SaveCanvas(c, os.path.join(outdir, '{}.pdf'.format(fname)), close=True)

def Draw_TH2_w_AsymmetryError(central, up_error, do_error, fname, outdir):
  x_axis = central.GetXaxis()
  y_axis = central.GetYaxis()
  nbinX  = x_axis.GetNbins()
  nbinY  = y_axis.GetNbins()
  x_binnings = [x_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinX+1)]
  y_binnings = [y_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinY+1)]
  c = CMS.cmsCanvas('', min(x_binnings), max(x_binnings), min(y_binnings), max(y_binnings), '', '', square = CMS.kRectangular, extraSpace=0.01, iPos=0, with_z_axis=True)
  c.SetLogx()
  central.SetTitle(";pT[GeV];|#eta|")
  CMS.cmsDraw(central, 'COLZ')
  CMS.SetAlternative2DColor(central, CMS.cmsStyle)
  CMS.UpdatePalettePosition(central, c)

  latex = ROOT.TLatex()
  latex.SetTextSize(0.025)
  latex.SetTextAlign(22)  # Center align

  for ix in range(nbinX):
    for iy in range(nbinY):
        bin_content  = central.GetBinContent(ix+1, iy+1)
        bin_center_x = central.GetXaxis().GetBinCenter(ix+1)
        bin_center_y = central.GetYaxis().GetBinCenter(iy+1)
        if(bin_content == 0.0): continue
        up_error_content = up_error.GetBinContent(ix+1, iy+1)
        down_error_content = do_error.GetBinContent(ix+1, iy+1)
        text = r"%.2f^{+%.2f}_{-%.2f}"%(bin_content, up_error_content, down_error_content)  # Format the text
        latex.DrawLatex(bin_center_x, bin_center_y, text)


  CMS.SaveCanvas(c, os.path.join(outdir, '{}.png'.format(fname)), close=False)
  CMS.SaveCanvas(c, os.path.join(outdir, '{}.pdf'.format(fname)), close=True)

def draw_1D_eff(hist, fout_name, plotdir):

    TH1_Dict = OrderedDict()
    x_axis = hist.GetXaxis()
    y_axis = hist.GetYaxis()
    nbinX  = x_axis.GetNbins()
    nbinY  = y_axis.GetNbins()
    x_binnings = [x_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinX+1)]
    y_binnings = [y_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinY+1)]

    for iy in range(nbinY):
        TH1_ = ROOT.TH1D('h', 'h', nbinX, array('d', x_binnings))
        for ix in range(nbinX):
            TH1_.SetBinContent(ix+1, hist.GetBinContent(ix+1, iy+1))
            TH1_.SetBinError(ix+1, hist.GetBinError(ix+1, iy+1))
        TH1_Dict["{}<|#eta|<{}".format(y_binnings[iy], y_binnings[iy+1])] = TH1_



    c = CMS.cmsCanvas('', min(x_binnings), max(x_binnings), 0.3, 1.2, '', '', square = CMS.kSquare, extraSpace=0.0, iPos=0)
    legend = CMS.cmsLeg(0.65, 0.2, 0.85, 0.4, textSize=0.04)
    idx_hist = 0
    if 'Electron' in plotdir:
        color_List = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kOrange-3, ROOT.kViolet, ROOT.kSpring+9]
    else:
        color_List = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kOrange-3, ROOT.kViolet, ROOT.kSpring+9]

    TH1_Dict = OrderedDict(reversed(list(TH1_Dict.items())))

    for hist_ in TH1_Dict:
        if '1.442' in hist_ and '1.556' in hist_: continue
        TH1_Dict[hist_].SetLineWidth(2)
        legend.AddEntry(TH1_Dict[hist_], hist_, 'L')
        if idx_hist == 0:
            TH1_Dict[hist_].GetXaxis().SetTitle('pT[GeV]')
            TH1_Dict[hist_].GetYaxis().SetTitle('Efficiency')
            TH1_Dict[hist_].GetYaxis().SetRangeUser(0.3, 1.2)
            CMS.cmsDraw(TH1_Dict[hist_], 'P E', mcolor = color_List[idx_hist])
        else:
            CMS.cmsDraw(TH1_Dict[hist_], "SAME P E", mcolor = color_List[idx_hist])
        idx_hist+=1

    c.SetLogx()
    CMS.SaveCanvas(c, os.path.join(plotdir, '{}.png'.format(fout_name)), close = False)
    CMS.SaveCanvas(c, os.path.join(plotdir, '{}.pdf'.format(fout_name)))



def Efficiency(Data_num, Data_den, MC_num, MC_den, fout_name, plotdir):
 
    TH1_Dict = OrderedDict()
    TEfficiency_Dict = OrderedDict()
    TH1_Efficiency_Dict = OrderedDict()

    x_axis   = Data_num.GetXaxis()
    y_axis   = Data_num.GetYaxis()
    nbinX    = x_axis.GetNbins()
    nbinY    = y_axis.GetNbins()
    x_binnings = [x_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinX+1)]
    y_binnings = [y_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinY+1)]


    ScaleFactor2D      = ROOT.TH2D('nominal', 'nominal', nbinX, array('d', x_binnings), nbinY, array('d', y_binnings))
    ScaleFactor2D_up   = ROOT.TH2D('Up', 'Up', nbinX, array('d', x_binnings), nbinY, array('d', y_binnings))
    ScaleFactor2D_do   = ROOT.TH2D('Do', 'Do', nbinX, array('d', x_binnings), nbinY, array('d', y_binnings))

    for iy in range(nbinY):
      TH1_Data_num = Get_From_TH2(nbinX, x_binnings, Data_num, iy, 'Data_num')
      TH1_Data_den = Get_From_TH2(nbinX, x_binnings, Data_den, iy, 'Data_den')
      TH1_MC_num   = Get_From_TH2(nbinX, x_binnings, MC_num,   iy, 'MC_num')
      TH1_MC_den   = Get_From_TH2(nbinX, x_binnings, MC_den,   iy, 'MC_den')
      TEfficiency_Data = ROOT.TEfficiency(TH1_Data_num, TH1_Data_den)
      TEfficiency_MC   = ROOT.TEfficiency(TH1_MC_num,   TH1_MC_den)

      TEfficiency_Dict["{}<|#eta|<{}".format(y_binnings[iy], y_binnings[iy+1])] = {'Data': TEfficiency_Data, 'MC': TEfficiency_MC}

    c = CMS.cmsDiCanvas('c', min(x_binnings), max(x_binnings), 0.3, 1.2, 0.5, 1.5, 'pT[GeV]', 'Efficiency', 'Data/Pred.', square = CMS.kSquare, extraSpace=0.0, iPos=0)
    c.cd(1)
    legend = CMS.cmsLeg(0.65, 0.2, 0.85, 0.4, textSize=0.04)
    color_List = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kOrange-3, ROOT.kViolet, ROOT.kSpring+9]
    #TEfficiency_Dict = OrderedDict(reversed(list(TEfficiency_Dict.items())))

    Efficiency_BaseTrig   = ROOT.TH2D('Base', 'Base', nbinX, array('d', x_binnings), nbinY, array('d', y_binnings))
    Efficiency_BothTrig   = ROOT.TH2D('Both', 'Both', nbinX, array('d', x_binnings), nbinY, array('d', y_binnings))
    Efficiency_TargetTrig = ROOT.TH2D('Target', 'Target', nbinX, array('d', x_binnings), nbinY, array('d', y_binnings))


    for idx_hist, eff_ in enumerate(TEfficiency_Dict):
      c.cd(1)
      if '1.442' in eff_ and '1.556' in eff_: continue
      eff_Data = TEfficiency_Dict[eff_]['Data']
      #eff_Data.SetConfidenceLevel(0.683)
      eff_MC   = TEfficiency_Dict[eff_]['MC']
      #eff_MC.SetConfidenceLevel(0.683)
      legend.AddEntry(eff_Data, eff_ + "(Data)", 'L')
      CMS.cmsDraw(eff_Data, 'SAME P', mcolor = color_List[idx_hist], lwidth=2)

      x_array = ROOT.std.vector('Double_t')(nbinX)
      x_low   = ROOT.std.vector('Double_t')(nbinX)
      x_high  = ROOT.std.vector('Double_t')(nbinX)
      y_array = ROOT.std.vector('Double_t')(nbinX)
      y_low   = ROOT.std.vector('Double_t')(nbinX)
      y_high  = ROOT.std.vector('Double_t')(nbinX)

      for ix in range(nbinX):
        x_array[ix] = eff_Data.GetTotalHistogram().GetBinCenter(ix+1)
        x_low[ix]   = eff_Data.GetTotalHistogram().GetBinWidth(ix+1)/2
        x_high[ix]  = eff_Data.GetTotalHistogram().GetBinWidth(ix+1)/2

        eff_data_      = eff_Data.GetEfficiency(ix+1)
        eff_data_low_  = eff_Data.GetEfficiencyErrorLow(ix+1)
        eff_data_high_ = eff_Data.GetEfficiencyErrorUp(ix+1)
        eff_mc_        = eff_MC.GetEfficiency(ix+1)
        eff_mc_low_    = eff_MC.GetEfficiencyErrorLow(ix+1)
        eff_mc_high_   = eff_MC.GetEfficiencyErrorUp(ix+1)
        y_array[ix]    = eff_data_ / eff_mc_ 
        y_low[ix]      = (((eff_data_low_/eff_mc_)**2) + ((eff_data_/eff_mc_/eff_mc_*eff_mc_high_)**2))**0.5 
        y_high[ix]     = (((eff_data_high_/eff_mc_)**2) + ((eff_data_/eff_mc_/eff_mc_*eff_mc_low_)**2))**0.5


        ScaleFactor2D.SetBinContent(ix+1, idx_hist+1, y_array[ix])
        ScaleFactor2D_up.SetBinContent(ix+1, idx_hist+1, y_high[ix])
        ScaleFactor2D_do.SetBinContent(ix+1, idx_hist+1, y_low[ix])

        ScaleFactor2D.SetBinError(ix+1, idx_hist+1, max(y_high[ix], y_low[ix]))
        ScaleFactor2D_up.SetBinError(ix+1, idx_hist+1, 0)
        ScaleFactor2D_do.SetBinError(ix+1, idx_hist+1, 0)

      Scale_Factor = ROOT.TGraphAsymmErrors(nbinX, x_array.data(), y_array.data(), x_low.data(), x_high.data(), y_low.data(), y_high.data())
      Scale_Factor = Scale_Factor.Clone()
      Scale_Factor.SetName(eff_)
      c.cd(2)
      if idx_hist == 0:
        CMS.cmsDraw(Scale_Factor, 'SAME P E', mcolor = color_List[idx_hist], msize=1.0, lwidth=1)
      else:
        CMS.cmsDraw(Scale_Factor, 'SAME P E', mcolor = color_List[idx_hist], lwidth=1, msize=1.0)

    c.SetLogx()
    CMS.SaveCanvas(c, os.path.join(plotdir, '{}.png'.format(fout_name)), close=False)
    CMS.SaveCanvas(c, os.path.join(plotdir, '{}.pdf'.format(fout_name)), close=True)

    Draw_TH2(ScaleFactor2D, 'ScaleFactor2D', plotdir)
    Draw_TH2(ScaleFactor2D_up, 'ScaleFactor2D_up_unc', plotdir)
    Draw_TH2(ScaleFactor2D_do, 'ScaleFactor2D_down_unc', plotdir)

    Draw_TH2_w_AsymmetryError(ScaleFactor2D, ScaleFactor2D_up, ScaleFactor2D_do, 'ScaleFactor2D_AsymmetricError', plotdir)

    return ScaleFactor2D

def Correlation(MC_num, MC_den, MC_pure_Trig, MC_basic_cut, plotdir):

    TEfficiency_Dict = OrderedDict()
    TH1_Dict = OrderedDict()

    x_axis   = MC_num.GetXaxis()
    y_axis   = MC_num.GetYaxis()
    nbinX    = x_axis.GetNbins()
    nbinY    = y_axis.GetNbins()
    x_binnings = [x_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinX+1)]
    y_binnings = [y_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinY+1)]

    Efficiency_BaseTrig   = ROOT.TH2D('Base', 'Base', nbinX, array('d', x_binnings), nbinY, array('d', y_binnings))
    Efficiency_BothTrig   = ROOT.TH2D('Both', 'Both', nbinX, array('d', x_binnings), nbinY, array('d', y_binnings))
    Efficiency_TargetTrig = ROOT.TH2D('Target', 'Target', nbinX, array('d', x_binnings), nbinY, array('d', y_binnings))


    for iy in range(nbinY):
      TH1_MC_num   = Get_From_TH2(nbinX, x_binnings, MC_num,   iy, 'MC_num')
      TH1_MC_den   = Get_From_TH2(nbinX, x_binnings, MC_den,   iy, 'MC_den')
      TH1_MC_pure_Trig   = Get_From_TH2(nbinX, x_binnings, MC_pure_Trig,   iy, 'MC_pure_Trig')
      TH1_MC_basic_cut   = Get_From_TH2(nbinX, x_binnings, MC_basic_cut,   iy, 'MC_basic_cut')
      TEfficiency_BothTrig   = ROOT.TEfficiency(TH1_MC_num,   TH1_MC_basic_cut)
      TEfficiency_BaseTrig   = ROOT.TEfficiency(TH1_MC_den,   TH1_MC_basic_cut)
      TEfficiency_TargetTrig = ROOT.TEfficiency(TH1_MC_pure_Trig, TH1_MC_basic_cut)

      for ix in range(nbinX):
        BothTrig_Eff = [TEfficiency_BothTrig.GetEfficiency(ix+1), (TEfficiency_BothTrig.GetEfficiencyErrorUp(ix+1) + TEfficiency_BothTrig.GetEfficiencyErrorLow(ix+1))/2]
        BaseTrig_Eff = [TEfficiency_BaseTrig.GetEfficiency(ix+1), (TEfficiency_BaseTrig.GetEfficiencyErrorUp(ix+1) + TEfficiency_BaseTrig.GetEfficiencyErrorLow(ix+1))/2]
        TargetTrig_Eff = [TEfficiency_TargetTrig.GetEfficiency(ix+1), (TEfficiency_TargetTrig.GetEfficiencyErrorUp(ix+1) + TEfficiency_TargetTrig.GetEfficiencyErrorLow(ix+1))/2]

        Efficiency_BaseTrig.SetBinContent(ix+1, iy+1, BaseTrig_Eff[0])
        Efficiency_BaseTrig.SetBinError(ix+1, iy+1, BaseTrig_Eff[1])
        Efficiency_BothTrig.SetBinContent(ix+1, iy+1, BothTrig_Eff[0])
        Efficiency_BothTrig.SetBinError(ix+1, iy+1, BothTrig_Eff[1])
        Efficiency_TargetTrig.SetBinContent(ix+1, iy+1, TargetTrig_Eff[0])
        Efficiency_TargetTrig.SetBinError(ix+1, iy+1, TargetTrig_Eff[1])

      TH1_BaseTrig = Get_From_TH2(nbinX, x_binnings, Efficiency_BaseTrig, iy, 'BaseTrig')
      TH1_BothTrig = Get_From_TH2(nbinX, x_binnings, Efficiency_BothTrig, iy, 'BothTrig')
      TH1_TargetTrig = Get_From_TH2(nbinX, x_binnings, Efficiency_TargetTrig, iy, 'TargetTrig')

      TH1_Correlation = TH1_BothTrig.Clone()
      TH1_Correlation.Divide(TH1_TargetTrig)
      TH1_Correlation.Divide(TH1_BaseTrig)

      TEfficiency_Dict["{}<|#eta|<{}".format(y_binnings[iy], y_binnings[iy+1])] = {'BothTrig': TEfficiency_BothTrig, 'BaseTrig': TEfficiency_BaseTrig, 'TargetTrig': TEfficiency_BaseTrig}
      TH1_Dict["{}<|#eta|<{}".format(y_binnings[iy], y_binnings[iy+1])] = TH1_Correlation

    c = CMS.cmsDiCanvas('c', min(x_binnings), max(x_binnings), 0.3, 1.2, 0.5, 1.5, 'pT[GeV]', 'Efficiency', 'Correlation', square = CMS.kSquare, extraSpace=0.0, iPos=0)
    c.cd(1)
    legend = CMS.cmsLeg(0.50, 0.1, 0.85, 0.5, textSize=0.04)
    color_List = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kOrange-3, ROOT.kViolet, ROOT.kSpring+9]

    for idx_hist, eff_ in enumerate(TEfficiency_Dict):
      c.cd(1)
      if '1.442' in eff_ and '1.556' in eff_: continue
      BaseTrig = TEfficiency_Dict[eff_]['BaseTrig']
      TargetTrig   = TEfficiency_Dict[eff_]['TargetTrig']
      BothTrig  = TEfficiency_Dict[eff_]['BothTrig']

      legend.AddEntry(BothTrig, eff_ + "(BothTrig)", 'L')
      legend.AddEntry(BaseTrig, eff_ + "(BaseTrig)", 'L')
      legend.AddEntry(TargetTrig, eff_ + "(TargetTrig)", 'L')

      CMS.cmsDraw(BaseTrig, 'SAME P', mcolor = color_List[idx_hist], lwidth=2, lstyle = 1)
      CMS.cmsDraw(TargetTrig, 'SAME P', mcolor = color_List[idx_hist], lwidth=2, lstyle = 2)
      CMS.cmsDraw(BothTrig, 'SAME P', mcolor = color_List[idx_hist], lwidth=2, lstyle = 3)

      c.cd(2)
      CMS.cmsDraw(TH1_Dict[eff_], 'SAME P E', mcolor = color_List[idx_hist], msize=1.0, lwidth=1)

    fout_name = 'Correlation'
    CMS.SaveCanvas(c, os.path.join(plotdir, '{}.png'.format(fout_name)), close=False)
    CMS.SaveCanvas(c, os.path.join(plotdir, '{}.pdf'.format(fout_name)), close=True) 

    Correlation2D = Efficiency_BothTrig.Clone()
    Correlation2D.Divide(Efficiency_BaseTrig)
    Correlation2D.Divide(Efficiency_TargetTrig)
  

    Draw_TH2(Efficiency_BothTrig, 'BothTrigEfficiency_MC', plotdir)
    Draw_TH2(Efficiency_BaseTrig, 'BaseTrigEfficiency_MC', plotdir)
    Draw_TH2(Efficiency_TargetTrig, 'TargetTrigEfficiency_MC', plotdir)
    Draw_TH2(Correlation2D, 'Correlation2D', plotdir, format_ = ".4f")
    return Correlation2D
def Calculate_Trigger_Scale_Factor(era, inputDir, region, lepton, plotdir):

    tstart = time.time()
    if not os.path.exists(plotdir):
        os.system('mkdir -p {}'.format(plotdir))

    ###############################
    ##  Basic Object Definition  ##
    ###############################

    num_dict = dict() # Base + Target
    den_dict = dict() # Base
    pure_Trig_dict = dict() # Target
    basic_cut_dict = dict() # Basic Cut

    MC_num = None
    MC_den = None
    MC_pure_Trig = None
    MC_basic_cut = None

    Get_hist_key = True
    var_list = []
    variation = inputDir.split('/')[-1]

    ##############################################
    ##  Obtain Necessary Information from root  ##
    ##############################################

    for dataset_ in fileset[era][lepton]:
        num_dataset = None
        den_dataset = None
        pure_Trig_dataset = None
        basic_cut_dataset = None
        for file_ in fileset[era][lepton][dataset_]:
            fin = ROOT.TFile.Open(os.path.join(inputDir, "{}_{}_".format(region, lepton) + file_), "READ")

            #################################
            ##  Get Distribution Key Name  ##
            #################################
            print(fin)
            if Get_hist_key:
                keys = fin.GetListOfKeys()
                for key in keys:
                    obj = key.ReadObj()
                    if obj.InheritsFrom(str("TH1D")):
                        hist_name = obj.GetName()
                        var_name = '_'.join(hist_name.split('_')[:-1])
                        if var_name not in var_list:
                            var_list.append(var_name)
                Get_hist_key = False

            num       = fin.Get("num")
            den       = fin.Get("den")
            pure_Trig = fin.Get("pure_Trig")
            basic_cut = fin.Get("basic_cut")
            cprint(file_, "yellow")
            if num_dataset is None:
                num_dataset = num.Clone()
                den_dataset = den.Clone()
                pure_Trig_dataset = pure_Trig.Clone()
                basic_cut_dataset = basic_cut.Clone()
                num_dataset.SetDirectory(0)
                den_dataset.SetDirectory(0)
                pure_Trig_dataset.SetDirectory(0)
                basic_cut_dataset.SetDirectory(0)
            else:
                num_dataset.Add(num)
                den_dataset.Add(den)
                pure_Trig_dataset.Add(pure_Trig)
                basic_cut_dataset.Add(basic_cut)
            fin.Close()
        num_dict[dataset_] = num_dataset.Clone()
        den_dict[dataset_] = den_dataset.Clone()
        pure_Trig_dict[dataset_] = pure_Trig_dataset.Clone()
        basic_cut_dict[dataset_] = basic_cut_dataset.Clone()
        num_dict[dataset_].Sumw2()
        den_dict[dataset_].Sumw2()
        pure_Trig_dict[dataset_].Sumw2()
        basic_cut_dict[dataset_].Sumw2()

    # Accumulate Monte Carlo
    MC_num = None
    for dataset_ in fileset[era][lepton]:
        if not dataset_ == 'Data':
            if MC_num is None:
                MC_num = num_dict[dataset_].Clone()
                MC_den = den_dict[dataset_].Clone()
                MC_pure_Trig = pure_Trig_dict[dataset_].Clone()
                MC_basic_cut = basic_cut_dict[dataset_].Clone()
            else:
                MC_num.Add(num_dict[dataset_])
                MC_den.Add(den_dict[dataset_])
                MC_pure_Trig.Add(pure_Trig_dict[dataset_])
                MC_basic_cut.Add(basic_cut_dict[dataset_])


    MC_num = overunder_flowbin2D(MC_num)
    MC_den = overunder_flowbin2D(MC_den)
    MC_pure_Trig = overunder_flowbin2D(MC_pure_Trig)
    MC_basic_cut = overunder_flowbin2D(MC_basic_cut)

    Data_num = overunder_flowbin2D(num_dict["Data"])
    Data_den = overunder_flowbin2D(den_dict["Data"])

    sf = Efficiency(Data_num, Data_den, MC_num, MC_den, "ScaleFactor", plotdir)
    correlation = Correlation(MC_num, MC_den, MC_pure_Trig, MC_basic_cut, plotdir)    
    # Draw Distribution
    for var_ in var_list:
      if not (variation == 'nominal'): continue
      for cate_ in ["total", "pass", "fail"]:
        canvas = DataMCCanvas(" "," ", Lumi[era])
        canvas.legend.setPosition(0.35,0.77,0.8,0.9)
        canvas.raxis.SetNdivisions(210)
        canvas.rlimits = (0,2)
        canvas.legend.SetTextSize(0.02)
        canvas.legend.SetX2(0.95)
        canvas.ytitle = "nEvents/bin"
        for dataset_ in fileset[era][lepton]:
            h_ = None
            for file_ in fileset[era][lepton][dataset_]:
                fin = ROOT.TFile.Open(os.path.join(inputDir, "{}_{}_".format(region, lepton) + file_), "READ")
                #print(inputDir, file_, var_, cate_)
                if h_ is None:
                    h_ = fin.Get(str(var_ + "_{}".format(cate_))).Clone()
                    h_.SetDirectory(0)
                else:
                    print( "{}_{}_".format(region, lepton) + file_, str(var_ + "_{}".format(cate_)), variation)
                    h_.Add(fin.Get(str(var_ + "_{}".format(cate_))).Clone())
                fin.Close()
            if dataset_ == 'Data':
                canvas.addObs(h_)
            else:
                canvas.addStacked(h_, title=dataset_, color=Color_Dict_ref[dataset_], opt='F')
        canvas.rtitle = str("Data/MC")
        canvas.yaxis.SetMaxDigits(4)
        canvas.applyStyles()
        canvas.printWeb(plotdir,"{}_{}_log".format(var_, cate_), logy=True)
        canvas.SetLogy(False)
        canvas.applyStyles()
        canvas.printWeb(plotdir,"{}_{}".format(var_, cate_), logy=False)

    return sf, correlation


def summary_trigger_scale_factor(indir, outdir, variations, era, nui_correlation=False):
  fout = ROOT.TFile.Open(os.path.join(outdir, 'Trigger_scale_factor_{}_summary.root'.format(era)), 'RECREATE')
  for region_ in ['bh', 'boost']:
    for lepton_ in ['Electron', 'Muon']:
      # Get nominal scale factor
      f_nominal = ROOT.TFile.Open(os.path.join(indir, 'nominal', 'Trigger_scale_factor_{}.root'.format(era)), 'READ')
      h_nominal_stat = f_nominal.Get('{}_{}_scale_factor'.format(region_, lepton_))
      h_nominal_stat.SetDirectory(0)
      h_nominal_syst = h_nominal_stat.Clone()
      h_nominal_syst.SetDirectory(0)
      h_nominal_total = h_nominal_stat.Clone()
      h_nominal_total.SetDirectory(0)
      correlation = f_nominal.Get('{}_{}_correlation'.format(region_, lepton_))
      correlation.SetDirectory(0)
      f_nominal.Close()

      h_variation_dict = dict()
      for var_ in variations:
        for direction_ in ['_up', '_down']:
          f_variation = ROOT.TFile.Open(os.path.join(indir, var_ + direction_, 'Trigger_scale_factor_{}.root'.format(era)), 'READ')
          h_variation_dict[var_ + direction_] = f_variation.Get('{}_{}_scale_factor'.format(region_, lepton_))
          h_variation_dict[var_ + direction_].SetDirectory(0)
          f_variation.Close()
        h_variation_dict[var_] = h_nominal_stat.Clone()
        h_variation_dict[var_].SetDirectory(0)

      for binx in range(h_nominal_syst.GetNbinsX()):
        for biny in range(h_nominal_syst.GetNbinsY()):
          idx_x = binx + 1
          idx_y = biny + 1
          sf_nominal = h_nominal_stat.GetBinContent(idx_x, idx_y)
          sf_statUnc = h_nominal_stat.GetBinError(idx_x, idx_y)
          sigma = 0
          for var_ in variations:
            sf_up = h_variation_dict[var_ + '_up'].GetBinContent(idx_x, idx_y)
            sf_down = h_variation_dict[var_ + '_down'].GetBinContent(idx_x, idx_y)
            diff = (abs(sf_up - sf_nominal) + abs(sf_down - sf_nominal))/2.
            sigma += diff*diff
            h_variation_dict[var_].SetBinError(idx_x, idx_y, diff)
          sigma = sigma**0.5
          h_nominal_syst.SetBinError(idx_x, idx_y, sigma)
          sf_totalUnc = ((sigma*sigma) + (sf_statUnc*sf_statUnc))**0.5
          h_nominal_total.SetBinError(idx_x, idx_y, sf_totalUnc)

      h_correlation_nui = h_nominal_stat.Clone()
      h_correlation_nui.SetDirectory(0)
      if nui_correlation:
        for binx in range(h_correlation_nui.GetNbinsX()):
          for biny in range(h_correlation_nui.GetNbinsY()):
            correlation_ = correlation.GetBinContent(binx+1, biny+1)
            h_correlation_nui.SetBinError(binx+1, biny+1, abs(1-correlation_))
            total_unc    = h_nominal_total.GetBinError(binx+1, biny+1)
            total_unc    = ((total_unc*total_unc) + ((1-correlation_) * (1-correlation_)))**0.5
            h_nominal_total.SetBinError(binx+1, biny+1, total_unc)
        h_correlation_nui.SetName('{}_{}_scale_factor_corre_unc'.format(region_, lepton_))
        draw_1D_eff(h_correlation_nui, '{}_{}_scale_factor_1D_corre_unc'.format(region_, lepton_), outdir)
        Draw_TH2(h_correlation_nui, '{}_{}_scale_factor_2D_corre_unc'.format(region_, lepton_), outdir)
  

      h_nominal_syst.SetName('{}_{}_scale_factor_syst'.format(region_, lepton_))
      h_nominal_stat.SetName('{}_{}_scale_factor_stat'.format(region_, lepton_))
      h_nominal_total.SetName('{}_{}_scale_factor_total'.format(region_, lepton_))

      draw_1D_eff(h_nominal_syst, '{}_{}_scale_factor_1D_syst'.format(region_, lepton_), outdir)
      draw_1D_eff(h_nominal_stat, '{}_{}_scale_factor_1D_stat'.format(region_, lepton_), outdir)
      draw_1D_eff(h_nominal_total, '{}_{}_scale_factor_1D_total'.format(region_, lepton_), outdir)
     

      x_axis = h_nominal_syst.GetXaxis()
      y_axis = h_nominal_syst.GetYaxis()
      nbinX  = x_axis.GetNbins()
      nbinY  = y_axis.GetNbins()
      x_binnings = [x_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinX+1)]
      y_binnings = [y_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinY+1)]

      Draw_TH2(h_nominal_stat, '{}_{}_scale_factor_2D_stat'.format(region_, lepton_), outdir)
      Draw_TH2(h_nominal_syst, '{}_{}_scale_factor_2D_syst'.format(region_, lepton_), outdir)
      Draw_TH2(h_nominal_total, '{}_{}_scale_factor_2D_total'.format(region_, lepton_), outdir)

      for var_ in variations:
        Draw_TH2(h_variation_dict[var_], '{}_{}_scale_factor_2D_{}'.format(region_, lepton_, var_), outdir)

      fout.cd()
      h_nominal_syst.Write()
      h_nominal_stat.Write()
      h_nominal_total.Write()      
      if nui_correlation: h_correlation_nui.Write()
  fout.Close()

if __name__ == '__main__':
    usage = 'usage: %prog [options]'
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('-e', '--era', dest='era', help='[2016apv/2016postapv/2017/2018/all]', default='2017', type=str)
    parser.add_argument('-i', '--indir', dest='inputdir', default='./', type=str)
    args = parser.parse_args()

    os.system('mkdir -p plot')
    Eras = []
    if args.era == 'all':
        Eras = ['2016apv', '2016postapv', '2017', '2018']
    else:
        Eras = [args.era]

    for era_ in Eras:
      CMS.SetLumi(Lumi_text[era_])
      for variation_ in ['nominal', 'nPV_up', 'nPV_down', 'nJet_up', 'nJet_down']:
        sf_dir = 'data_v2/' + variation_
        os.system('mkdir -p {}'.format(sf_dir))
        fout = ROOT.TFile.Open(os.path.join(sf_dir, 'Trigger_scale_factor_{}.root'.format(era_)), 'RECREATE')
        for region_ in ['bh', 'boost']:
          for lepton_ in ['Muon', 'Electron']:
              plotdir = os.path.join('plot_v2',era_,region_,lepton_, variation_)
              sf, correlation = Calculate_Trigger_Scale_Factor(era_, inputDir = os.path.join(args.inputdir, era_, variation_), region=region_, lepton=lepton_, plotdir=plotdir)
              fout.cd()
              sf.Write('{}_{}_scale_factor'.format(region_, lepton_))
              correlation.Write('{}_{}_correlation'.format(region_, lepton_))
        fout.Close()

      output_directory = 'data_v2/summary/{}'.format(era_)
      input_directory  = 'data_v2'
      variation        = ['nPV', 'nJet']
      os.system('mkdir -p {}'.format(output_directory))
      summary_trigger_scale_factor(input_directory, output_directory, variation, era_, nui_correlation = True)
