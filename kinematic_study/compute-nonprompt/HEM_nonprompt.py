import ROOT
from copy import deepcopy
from array import array
import numpy as np
import os

folder_noHEM = '/eos/user/g/gkole/database/bHplus/25Apr2025/'
folder_HEM = '/eos/user/a/adeiorio/Hplus/nosynch/'

#years = ['2016apv', '2016postapv', '2017', '2018']
years = ['2018']  # for testing purposes,

channels = {'mu_resolved_data': [ 'SingleMuon' ],
            'mu_resolved_mc': ["DYnlo",  "tbarW", "TTtoHadronic", "TTTo1L", "TTTo2L", "tW", "WJets_HT70to100_LO", "WJets_HT100to200_LO", "WJets_HT200to400_LO", "WJets_HT400to600_LO",
                               "WJets_HT600to800_LO", "WJets_HT800to1200_LO", "WJets_HT1200to2500_LO", "WJets_HT2500toInf_LO", "tbar_tch", "t_tch",  "t_sch"],
            'mu_resolved_qcd': ["QCD_HT100to200", "QCD_HT200to300", "QCD_HT300to500", "QCD_HT500to700", "QCD_HT700to1000", "QCD_HT1000to1500",
                                "QCD_HT1500to2000", "QCD_HT2000toInf"],
            'ele_resolved_data': [ 'SingleEG', 'SinglePhoton' ],
            'ele_resolved_mc': ["DYnlo",  "tbarW", "TTtoHadronic", "TTTo1L", "TTTo2L", "tW", "WJets_HT70to100_LO", "WJets_HT100to200_LO", "WJets_HT200to400_LO", "WJets_HT400to600_LO",
                               "WJets_HT600to800_LO", "WJets_HT800to1200_LO", "WJets_HT1200to2500_LO", "WJets_HT2500toInf_LO", "tbar_tch", "t_tch",  "t_sch"],
            'ele_resolved_qcd': ["QCD_HT100to200", "QCD_HT200to300", "QCD_HT300to500", "QCD_HT500to700", "QCD_HT700to1000", "QCD_HT1000to1500",
                                "QCD_HT1500to2000", "QCD_HT2000toInf"],
            }
ROOT.gROOT.cd()
ROOT.gROOT.SetBatch(True)
def plot_subtract(folder, year, channel, region, hist):
    datah = ROOT.TH1F()
    print(datah.GetNbinsX())
    #datah.SetDirectory(0)
    if year == '2018' and channel == 'ele_resolved':
        channels[channel+'_data'] = [ 'EGamma' ]
    print(region)
    for datafile in channels[channel+'_data']:
        print(datafile)
        datain = ROOT.TFile.Open(folder + '/' + year + '/' + region + '/' + channel + '/' + datafile + '.root')
        print(folder + '/' + year + '/' + region + '/' + channel + '/' + datafile + '.root')
        histo = datain.Get(hist)
        print(histo.Integral())
        if datah.Integral() == 0:
            datah = histo.Clone()
            datah.SetDirectory(0)
        else:
            datah.Add(histo)
        print(datah.Integral())
    for mcfile in channels[channel+'_mc']:
        print(mcfile)
        mcin = ROOT.TFile.Open(folder + '/' + year + '/' + region + '/' + channel + '/' + mcfile + '.root')
        datah.Add(mcin.Get(hist), -1)
        print(datah.Integral())
    #check the negative bins
    for ix in range(1, datah.GetNbinsX() + 1):
        #for iy in range(1, datah.GetNbinsY() + 1):
        content = datah.GetBinContent(ix)
        if content < 0:
            print(f"WARNING: bin {ix} has negative content: {content}")
            datah.SetBinContent(ix, 0.0001)
            datah.SetBinError(ix, 0.0001)
    return datah

def ratio_and_save(hist1, hist2, name, options='COLZ', logz=False, year="", channel=""):
    canvas = ROOT.TCanvas(name, name, 800, 600)
    hist1.SetLineColor(ROOT.kRed)
    hist2.SetStats(0)
    hist2.SetMaximum(hist2.GetMaximum() * 1.4)
    histo =  ROOT.TRatioPlot(hist2, hist1)
    #histo.SetTitle('; lepton p_{T} [GeV]; lepton #eta')
    #print('Drawing', histo.Integral())
    histo.Draw(options)
    # Draw channel and year information
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.045)
    latex.SetTextAlign(13)
    latex.DrawLatex(0.13, 0.88, f"{year}, {channel}")
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend.AddEntry(hist1, 'No HEM', 'l')
    legend.AddEntry(hist2, 'HEM', 'l')
    legend.Draw()
    if logz:
        canvas.SetLogz()
    canvas.Modified()
    canvas.Update()
    canvas.Print(f'HEM_nonprompt/{name}.png')
    canvas.Print(f'HEM_nonprompt/{name}.pdf')
    return canvas

extra = ''

if __name__ == '__main__':
    savedir = f"HEM_nonprompt{extra}"
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    for year in years:
        for lep in ['mu_resolved', 'ele_resolved']:
            print('Processing year:', year, 'channel:', lep)
            regionC_pt = plot_subtract(folder_noHEM + 'NonPrompt_C', year, lep, 'NonPrompt_C_default', 'bh_l1_pt')
            regionC_eta = plot_subtract(folder_noHEM + 'NonPrompt_C', year, lep, 'NonPrompt_C_default', 'bh_l1_eta')
            regionC_HEM_pt = plot_subtract(folder_HEM + 'NonPrompt_C_HEM', year, lep, 'NonPrompt_C_default', 'bh_l1_pt')
            regionC_HEM_eta = plot_subtract(folder_HEM + 'NonPrompt_C_HEM', year, lep, 'NonPrompt_C_default', 'bh_l1_eta')
            regionC_j1pt = plot_subtract(folder_noHEM + 'NonPrompt_C', year, lep, 'NonPrompt_C_default', 'j1_pt')
            regionC_HEM_j1pt = plot_subtract(folder_HEM + 'NonPrompt_C_HEM', year, lep, 'NonPrompt_C_default', 'j1_pt')
            ratio_and_save(regionC_pt, regionC_HEM_pt, f'ratioC_{year}_{lep}_pt', '', year=year, channel=lep + ' region C')
            ratio_and_save(regionC_eta, regionC_HEM_eta, f'ratioC_{year}_{lep}_eta', '', year=year, channel=lep + ' region C')
            ratio_and_save(regionC_j1pt, regionC_HEM_j1pt, f'ratioC_{year}_{lep}_j1pt', '', year=year, channel=lep + ' region C')
            
            regionD_pt = plot_subtract(folder_noHEM + 'NonPrompt_D', year, lep, 'NonPrompt_D_default', 'QCD_Lepton_pt')
            regionD_eta = plot_subtract(folder_noHEM + 'NonPrompt_D', year, lep, 'NonPrompt_D_default', 'bh_l1_eta')
            regionD_HEM_pt = plot_subtract(folder_HEM + 'NonPrompt_D_HEM', year, lep, 'NonPrompt_D_default', 'QCD_Lepton_pt')
            regionD_HEM_eta = plot_subtract(folder_HEM + 'NonPrompt_D_HEM', year, lep, 'NonPrompt_D_default', 'bh_l1_eta')
            regionD_j1pt = plot_subtract(folder_noHEM + 'NonPrompt_D', year, lep, 'NonPrompt_D_default', 'j1_pt')
            regionD_HEM_j1pt = plot_subtract(folder_HEM + 'NonPrompt_D_HEM', year, lep, 'NonPrompt_D_default', 'j1_pt')
            ratio_and_save(regionD_pt, regionD_HEM_pt, f'ratioD_{year}_{lep}_pt', '', year=year, channel=lep + ' region D')
            ratio_and_save(regionD_eta, regionD_HEM_eta, f'ratioD_{year}_{lep}_eta', '', year=year, channel=lep + ' region D')
            ratio_and_save(regionD_j1pt, regionD_HEM_j1pt, f'ratioD_{year}_{lep}_j1pt', '', year=year, channel=lep + ' region D')
            
            regionB_pt = plot_subtract(folder_noHEM + 'NonPrompt_B', year, lep, 'NonPrompt_B_default', 'QCD_Lepton_pt')
            regionB_eta = plot_subtract(folder_noHEM + 'NonPrompt_B', year, lep, 'NonPrompt_B_default', 'bh_l1_eta')
            regionB_HEM_pt = plot_subtract(folder_HEM + 'NonPrompt_B_HEM', year, lep, 'NonPrompt_B_default', 'QCD_Lepton_pt')
            regionB_HEM_eta = plot_subtract(folder_HEM + 'NonPrompt_B_HEM', year, lep, 'NonPrompt_B_default', 'bh_l1_eta')
            regionB_j1pt = plot_subtract(folder_noHEM + 'NonPrompt_B', year, lep, 'NonPrompt_B_default', 'j1_pt')
            regionB_HEM_j1pt = plot_subtract(folder_HEM + 'NonPrompt_B_HEM', year, lep, 'NonPrompt_B_default', 'j1_pt')
            ratio_and_save(regionB_pt, regionB_HEM_pt, f'ratioB_{year}_{lep}_pt', '', year=year, channel=lep + ' region B')
            ratio_and_save(regionB_eta, regionB_HEM_eta, f'ratioB_{year}_{lep}_eta', '', year=year, channel=lep + ' region B')
            ratio_and_save(regionB_j1pt, regionB_HEM_j1pt, f'ratioB_{year}_{lep}_j1pt', '', year=year, channel=lep + ' region B')


