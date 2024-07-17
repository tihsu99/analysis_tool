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

def Calculate_Trigger_Scale_Factor(era, inputDir, region, lepton, plotdir):

    tstart = time.time()
    if not os.path.exists(plotdir):
        os.system('mkdir -p {}'.format(plotdir))

    ############
    ##  ROOT  ##
    ############

    eff_dict = dict()
    num_dict = dict() # Base + Target
    den_dict = dict() # Base
    pure_Trig_dict = dict() # Target

    MC_num = None
    MC_den = None
    MC_pure_Trig = None
    Get_hist_key = True
    var_list = []
    variation = inputDir.split('/')[-1]
    # Draw Efficiency
    for dataset_ in fileset[era][lepton]:
        num_dataset = None
        den_dataset = None
        pure_Trig_dataset = None
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
                        if hist_name == 'num' or hist_name == 'den': continue
                        var_name = '_'.join(hist_name.split('_')[:-1])
                        if var_name not in var_list:
                            var_list.append(var_name)
                Get_hist_key = False

            num       = fin.Get("num")
            den       = fin.Get("den")
            pure_Trig = fin.Get("pure_Trig")
            cprint(file_, "yellow")
            if num_dataset is None:
                num_dataset = num.Clone()
                den_dataset = den.Clone()
                pure_Trig_dataset = pure_Trig.Clone()
                num_dataset.SetDirectory(0)
                den_dataset.SetDirectory(0)
                pure_Trig_dataset.SetDirectory(0)
            else:
                num_dataset.Add(num)
                den_dataset.Add(den)
                pure_Trig_dataset.Add(pure_Trig)
            fin.Close()
        num_dict[dataset_] = overunder_flowbin2D(num_dataset)
        den_dict[dataset_] = overunder_flowbin2D(den_dataset)
        pure_Trig_dict[dataset_] = pure_Trig_dataset.Clone()
        num_dict[dataset_].Sumw2()
        den_dict[dataset_].Sumw2()
        pure_Trig_dict[dataset_].Sumw2()


        c = ROOT.TCanvas()
        c.SetLogx()
        num_dataset.SetTitle(";pT[GeV];|#eta|")
        num_dataset.Draw("COLZ TEXT E")
        c.SaveAs(os.path.join(plotdir, "num_2D_{}.png".format(dataset_)))
        c.SaveAs(os.path.join(plotdir, "num_2D_{}.pdf".format(dataset_)))
        den_dataset.SetTitle(";pT[GeV];|#eta|")
        den_dataset.Draw("COLS TEXT E")
        c.SaveAs(os.path.join(plotdir, "den_2D_{}.png".format(dataset_)))
        c.SaveAs(os.path.join(plotdir, "den_2D_{}.pdf".format(dataset_)))


        eff = num_dataset.Clone()
        eff.SetName('{}_eff'.format(dataset_))
        eff.Divide(den_dataset)
        eff.SetTitle(";pT[GeV];|#eta|")
        eff.Write()
        eff.Draw("COLZ TEXT E")
        c.SaveAs(os.path.join(plotdir, "eff_2D_{}.png".format(dataset_)))
        c.SaveAs(os.path.join(plotdir, "eff_2D_{}.pdf".format(dataset_)))
        eff_dict[dataset_] = eff.Clone()
        draw_1D_eff(eff, 'eff_1D_{}'.format(dataset_), plotdir)

    MC_num = None
    for dataset_ in fileset[era][lepton]:
        if not dataset_ == 'Data':
            if MC_num is None:
                MC_num = num_dict[dataset_].Clone()
                MC_den = den_dict[dataset_].Clone()
                MC_pure_Trig = pure_Trig_dict[dataset_].Clone()
            else:
                MC_num.Add(num_dict[dataset_])
                MC_den.Add(den_dict[dataset_])
                MC_pure_Trig.Add(pure_Trig_dict[dataset_])


    MC_num = overunder_flowbin2D(MC_num)
    MC_den = overunder_flowbin2D(MC_den)
    MC_pure_Trig = overunder_flowbin2D(MC_pure_Trig)
    
    eff_MC = MC_num.Clone()
    eff_MC.SetName('MC_eff')
    eff_MC.Divide(MC_den)
    eff_MC.SetDirectory(0)

    x_axis = eff_MC.GetXaxis()
    y_axis = eff_MC.GetYaxis()
    nbinX  = x_axis.GetNbins()
    nbinY  = y_axis.GetNbins()
    x_binnings = [x_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinX+1)]
    y_binnings = [y_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinY+1)]

    c = CMS.cmsCanvas('', min(x_binnings), max(x_binnings), min(y_binnings), max(y_binnings), '', '', square = CMS.kRectangular, extraSpace=0.01, iPos=0, with_z_axis=True)
    ROOT.gStyle.SetPaintTextFormat(".2f")
    c.SetLogx()
    eff_MC.SetTitle(";pT[GeV];|#eta|")
    CMS.cmsDraw(eff_MC, 'COLZ TEXT E')
    CMS.SetAlternative2DColor(eff_MC, CMS.cmsStyle)
    CMS.UpdatePalettePosition(eff_MC, c)
    CMS.SaveCanvas(c, os.path.join(plotdir, "eff_2D_MC.png"), close=False)
    CMS.SaveCanvas(c, os.path.join(plotdir, "eff_2D_MC.pdf"), close=True)
    TH1_Dict = draw_1D_eff(eff_MC, 'eff_1D_MC', plotdir)
    eff_dict['MC'] = eff_MC.Clone()

    c = CMS.cmsCanvas('', min(x_binnings), max(x_binnings), min(y_binnings), max(y_binnings), '', '', square = CMS.kRectangular, extraSpace=0.01, iPos=0, with_z_axis=True)
    ROOT.gStyle.SetPaintTextFormat(".2f")
    c.SetLogx()
    MC_correlation = MC_num.Clone()
    MC_correlation.Divide(MC_den)
    MC_correlation.Divide(MC_pure_Trig)
    MC_correlation.SetDirectory(0)
    MC_correlation.SetTitle(";pT[GeV];|#eta|")
    CMS.cmsDraw(MC_correlation, 'COLZ TEXT E')
    CMS.SetAlternative2DColor(MC_correlation, CMS.cmsStyle)
    CMS.UpdatePalettePosition(MC_correlation, c)
    CMS.SaveCanvas(c, os.path.join(plotdir, "correlation_2D_MC.png"), close=False)
    CMS.SaveCanvas(c, os.path.join(plotdir, "correlation_2D_MC.pdf"), close=True)
    draw_1D_eff(MC_correlation, "correlation_1D_MC", plotdir)
    # Draw Scale Factor
    eff_Data = eff_dict['Data'].Clone()
    eff_Data.Divide(eff_MC)
    sf   = eff_Data.Clone()
    sf.SetName('sf_2D')
    sf.SetDirectory(0)
    c = ROOT.TCanvas()
    c.SetLogx()
    sf.SetTitle(";pT[GeV];|#eta|")
    sf.Draw("COLZ TEXT E")
    c.SaveAs(os.path.join(plotdir, "sf_2D.png"))
    c.SaveAs(os.path.join(plotdir, "sf_2D.pdf"))
    TH1_Dict = draw_1D_eff(sf, 'sf_1D', plotdir)

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
                    print( "{}_{}_".format(region, lepton) + file_, str(var_ + "_{}".format(cate_)))
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

    return sf


def summary_trigger_scale_factor(indir, outdir, variations, era):
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


      c = CMS.cmsCanvas('', min(x_binnings), max(x_binnings), min(y_binnings), max(y_binnings), '', '', square = CMS.kRectangular, extraSpace=0.01, iPos=0, with_z_axis=True)
      c.SetLogx()
      h_nominal_stat.SetTitle(";pT[GeV];|#eta|")
      ROOT.gStyle.SetPaintTextFormat(".2f")
      CMS.cmsDraw(h_nominal_stat, 'COLZ TEXT E')
      CMS.SetAlternative2DColor(h_nominal_stat, CMS.cmsStyle)
      CMS.UpdatePalettePosition(h_nominal_stat, c)

      CMS.SaveCanvas(c, os.path.join(outdir, '{}_{}_scale_factor_2D_stat.png'.format(region_, lepton_)), close = False)
      CMS.SaveCanvas(c, os.path.join(outdir, '{}_{}_scale_factor_2D_stat.pdf'.format(region_, lepton_)), close = False)

      h_nominal_syst.SetTitle(";pT[GeV];|#eta|")
      CMS.cmsDraw(h_nominal_syst, 'COLZ TEXT E')
      CMS.SetAlternative2DColor(h_nominal_syst, CMS.cmsStyle)
      CMS.UpdatePalettePosition(h_nominal_syst, c)
      CMS.SaveCanvas(c, os.path.join(outdir, '{}_{}_scale_factor_2D_syst.png'.format(region_, lepton_)), close = False)
      CMS.SaveCanvas(c, os.path.join(outdir, '{}_{}_scale_factor_2D_syst.pdf'.format(region_, lepton_)), close = False)

      h_nominal_total.SetTitle(";pT[GeV];|#eta|")
      CMS.cmsDraw(h_nominal_total, 'COLZ TEXT E')
      CMS.SetAlternative2DColor(h_nominal_total, CMS.cmsStyle)
      CMS.UpdatePalettePosition(h_nominal_total, c)
      CMS.SaveCanvas(c, os.path.join(outdir, '{}_{}_scale_factor_2D_total.png'.format(region_, lepton_)), close = False)
      CMS.SaveCanvas(c, os.path.join(outdir, '{}_{}_scale_factor_2D_total.pdf'.format(region_, lepton_)), close = False)

      for var_ in variations:
        h_variation_dict[var_].SetTitle(";pT[GeV];|#eta|")
        CMS.cmsDraw(h_variation_dict[var_], 'COLZ TEXT E')
        CMS.SetAlternative2DColor(h_variation_dict[var_], CMS.cmsStyle)
        CMS.UpdatePalettePosition(h_variation_dict[var_], c)
        CMS.SaveCanvas(c, os.path.join(outdir, '{}_{}_scale_factor_2D_{}.png'.format(region_, lepton_, var_)), close = False)
        CMS.SaveCanvas(c, os.path.join(outdir, '{}_{}_scale_factor_2D_{}.pdf'.format(region_, lepton_, var_)), close = False)

      fout.cd()
      h_nominal_syst.Write()
      h_nominal_stat.Write()
      h_nominal_total.Write()      

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
        sf_dir = 'data/' + variation_
        os.system('mkdir -p {}'.format(sf_dir))
        fout = ROOT.TFile.Open(os.path.join(sf_dir, 'Trigger_scale_factor_{}.root'.format(era_)), 'RECREATE')
        for region_ in ['bh', 'boost']:
          for lepton_ in ['Electron', 'Muon']:
              plotdir = os.path.join('plot',era_,region_,lepton_, variation_)
              sf = Calculate_Trigger_Scale_Factor(era_, inputDir = os.path.join(args.inputdir, era_, variation_), region=region_, lepton=lepton_, plotdir=plotdir)
              fout.cd()
              sf.Write('{}_{}_scale_factor'.format(region_, lepton_))
        fout.Close()
      output_directory = 'data/summary/{}'.format(era_)
      input_directory  = 'data'
      variation        = ['nPV', 'nJet']
      os.system('mkdir -p {}'.format(output_directory))
      summary_trigger_scale_factor(input_directory, output_directory, variation, era_)
