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
from array import array
from plotstyle import *
import re
from runcondor import fileset

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

    c = ROOT.TCanvas()
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    idx_hist = 0
    if 'Electron' in plotdir:
        color_List = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kOrange-3, ROOT.kViolet, ROOT.kSpring+9]
    else:
        color_List = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kOrange-3, ROOT.kViolet, ROOT.kSpring+9]

    TH1_Dict = OrderedDict(reversed(list(TH1_Dict.items())))

    for hist_ in TH1_Dict:
        if '1.442' in hist_ and '1.556' in hist_: continue 
        TH1_Dict[hist_].SetLineWidth(2)
        TH1_Dict[hist_].SetLineColor(color_List[idx_hist])
        legend.AddEntry(TH1_Dict[hist_], hist_, 'L')
        if idx_hist == 0:
            TH1_Dict[hist_].GetXaxis().SetTitle('pT[GeV]')
            TH1_Dict[hist_].GetYaxis().SetTitle('Efficiency')
            TH1_Dict[hist_].GetYaxis().SetRangeUser(0.3, 1.2)
            TH1_Dict[hist_].Draw('P E')
        else:
            TH1_Dict[hist_].Draw('SAME P E')
        idx_hist+=1
    legend.Draw("SAME")
    latex = ROOT.TLatex();
    latex.SetNDC();
    latex.SetTextFont(42);
    latex.SetTextSize(0.04);
    latex.SetTextAlign(31);
    latex.SetTextAlign(12);
    c.SaveAs(os.path.join(plotdir, '{}.png'.format(fout_name)))
    c.SaveAs(os.path.join(plotdir, '{}.pdf'.format(fout_name)))


def Calculate_Trigger_Scale_Factor(era, inputDir, region, lepton, plotdir):

    tstart = time.time()
    if not os.path.exists(plotdir):
        os.system('mkdir -p {}'.format(plotdir))

    ############
    ##  ROOT  ##
    ############

    eff_dict = dict()
    num_dict = dict()
    den_dict = dict()
    MC_num = None
    MC_den = None
    Get_hist_key = True
    var_list = []
    # Draw Efficiency
    for dataset_ in fileset[era]:
        num_dataset = None
        den_dataset = None
        for file_ in fileset[era][dataset_]:
            fin = ROOT.TFile.Open(os.path.join(inputDir, "{}_{}_".format(region, lepton) + file_), "READ")

            #################################
            ##  Get Distribution Key Name  ##
            #################################

            if Get_hist_key:
                keys = fin.GetListOfKeys()
                for key in keys:
                    obj = key.ReadObj()
                    if obj.InheritsFrom("TH1D"):
                        hist_name = obj.GetName()
                        if hist_name == 'num' or hist_name == 'den': continue
                        var_name = '_'.join(hist_name.split('_')[:-1])
                        if var_name not in var_list:
                            var_list.append(var_name)
                Get_hist_key = False

            num = fin.Get("num".format(dataset_))
            den = fin.Get("den".format(dataset_))
            print(file_)
            if num_dataset is None:
                num_dataset = num.Clone()
                den_dataset = den.Clone()
                num_dataset.SetDirectory(0)
                den_dataset.SetDirectory(0)
            else:
                num_dataset.Add(num)
                den_dataset.Add(den)
            fin.Close()
        num_dict[dataset_] = num_dataset.Clone()
        den_dict[dataset_] = den_dataset.Clone()
        for binx in range(num_dict[dataset_].GetNbinsX()):
            for biny in range(num_dict[dataset_].GetNbinsY()):
                num_dict[dataset_].SetBinError(binx+1, biny+1, (num_dict[dataset_].GetBinContent(binx+1, biny+1))**0.5)
                den_dict[dataset_].SetBinError(binx+1, biny+1, (num_dict[dataset_].GetBinContent(binx+1, biny+1))**0.5)
        eff = num_dataset.Clone()
        eff.SetName('{}_eff'.format(dataset_))
        eff.Divide(den_dataset)
        eff.Write()
        c = ROOT.TCanvas()
        eff.Draw("COLZ TEXT E")
        c.SaveAs(os.path.join(plotdir, "eff_2D_{}.png".format(dataset_)))
        c.SaveAs(os.path.join(plotdir, "eff_2D_{}.pdf".format(dataset_)))
        eff_dict[dataset_] = eff.Clone()
        draw_1D_eff(eff, 'eff_1D_{}'.format(dataset_), plotdir)

    MC_num = None
    for dataset_ in fileset[era]:
        if not dataset_ == 'Data':
            if MC_num is None:
                MC_num = num_dict[dataset_].Clone()
                MC_den = den_dict[dataset_].Clone()
            else:
                MC_num.Add(num_dict[dataset_])
                MC_den.Add(den_dict[dataset_])

    for binx in range(MC_num.GetNbinsX()):
        for biny in range(MC_num.GetNbinsY()):
            print(MC_num.GetBinContent(binx+1, biny+1), MC_num.GetBinError(binx+1, biny+1))
    eff_MC = MC_num.Clone()
    eff_MC.SetName('MC_eff')
    eff_MC.Divide(MC_den)
    eff_MC.SetDirectory(0)
    c = ROOT.TCanvas()
    eff_MC.Draw("COLZ TEXT E")
    c.SaveAs(os.path.join(plotdir, "eff_2D_MC.png"))
    c.SaveAs(os.path.join(plotdir, "eff_2D_MC.pdf"))
    TH1_Dict = draw_1D_eff(eff_MC, 'eff_1D_MC', plotdir)
    eff_dict['MC'] = eff_MC.Clone()

    # Draw Scale Factor
    eff_Data = eff_dict['Data'].Clone()
    eff_Data.Divide(eff_MC)
    sf       = eff_Data.Clone()
    sf.SetName('sf_2D')
    sf.SetDirectory(0)
    c = ROOT.TCanvas()
    sf.Draw("COLZ TEXT E")
    c.SaveAs(os.path.join(plotdir, "sf_2D.png"))
    c.SaveAs(os.path.join(plotdir, "sf_2D.pdf"))
    TH1_Dict = draw_1D_eff(sf, 'sf_1D', plotdir)

    # Draw Distribution
    for var_ in var_list:
      for cate_ in ["total", "pass", "fail"]:
        canvas = DataMCCanvas(" "," ", Lumi[era])
        canvas.legend.setPosition(0.35,0.77,0.8,0.9)
        canvas.raxis.SetNdivisions(210)
        canvas.rlimits = (0,2)
        canvas.legend.SetTextSize(0.02)
        canvas.legend.SetX2(0.95)
        canvas.ytitle = "nEvents/bin"
        for dataset_ in fileset[era]:
            h_ = None
            for file_ in fileset[era][dataset_]:
                fin = ROOT.TFile.Open(os.path.join(inputDir, "{}_{}_".format(region, lepton) + file_), "READ")
                print(file_, var_, cate_)
                if h_ is None:
                    h_ = fin.Get(str(var_ + "_{}".format(cate_))).Clone()
                    h_.SetDirectory(0)
                else:
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
      fout = ROOT.TFile.Open('Trigger_scale_factor_{}.root'.format(era_), 'RECREATE')
      for region_ in ['bh', 'boost']:
          for lepton_ in ['Electron', 'Muon']:
              plotdir = os.path.join('plot',era_,region_,lepton_)
              sf = Calculate_Trigger_Scale_Factor(era_, inputDir=args.inputdir, region=region_, lepton=lepton_, plotdir=plotdir)
              fout.cd()
              sf.Write('{}_{}_scale_factor'.format(region_, lepton_))
      fout.Close()
