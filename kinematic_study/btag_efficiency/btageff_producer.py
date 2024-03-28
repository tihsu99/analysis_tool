#!/bin/env python3
import os
import sys
import ROOT
import datetime
from array import array
import argparse

# b-tag working points: mistagging efficiency tight = 0.1%, medium 1% and loose = 10%
WPbtagger = {
    '2016apv':{'L': 0.0508, 'M': 0.2598, 'T': 0.6502},
    '2016postapv':{'L': 0.0480, 'M': 0.2489, 'T': 0.6377},
    '2017':{'L': 0.0532, 'M': 0.3040, 'T': 0.7476},
    '2018':{'L': 0.0490, 'M': 0.2783, 'T': 0.7100}
}

def btageff_producer(era, infile, outpath):

    Debug = False
    startTime = datetime.datetime.now()
    print("Starting running at " + str(startTime))
    
    ROOT.gROOT.SetBatch()
    
    chain = ROOT.TChain('Events')
    chain.Add(infile)
    print("Number of entries: " +str(chain.GetEntries()))


    outTreeFile = ROOT.TFile(outpath + infile.replace(".root","").rsplit("/", 1)[1] + "_out.root", "RECREATE") #some name of the output file
    
    #++++++++++++++++++++++++++++++++++
    #++      Efficiency studies      ++
    #++++++++++++++++++++++++++++++++++
    ptNBins = 100
    ptMin = 0
    ptMax = 1000.
    etaNBins = 60
    etaMin = -3.
    etaMax = 3.
    ptbins = array('f', [30., 40., 60., 80, 140., 200., 300, 500, 1000])
    etabins = array('f', [0.0, 0.8, 1.6, 2.4])
    nptbins = len(ptbins)-1
    netabins = len(etabins)-1
    
    h2_BTaggingEff_Denom_b    = ROOT.TH2D("h2_BTaggingEff_Denom_b", ";p_{T} [GeV];#eta", nptbins, ptbins, netabins, etabins)
    h2_BTaggingEff_Denom_c    = ROOT.TH2D("h2_BTaggingEff_Denom_c", ";p_{T} [GeV];#eta", nptbins, ptbins, netabins, etabins)
    h2_BTaggingEff_Denom_udsg = ROOT.TH2D("h2_BTaggingEff_Denom_udsg", ";p_{T} [GeV];#eta", nptbins, ptbins, netabins, etabins)
    h2_BTaggingLEff_Num_b     = ROOT.TH2D("h2_BTaggingLEff_Num_b", ";p_{T} [GeV];#eta", nptbins, ptbins, netabins, etabins)
    h2_BTaggingLEff_Num_c     = ROOT.TH2D("h2_BTaggingLEff_Num_c", ";p_{T} [GeV];#eta", nptbins, ptbins, netabins, etabins)
    h2_BTaggingLEff_Num_udsg  = ROOT.TH2D("h2_BTaggingLEff_Num_udsg", ";p_{T} [GeV];#eta", nptbins, ptbins, netabins, etabins)
    h2_BTaggingMEff_Num_b     = ROOT.TH2D("h2_BTaggingMEff_Num_b", ";p_{T} [GeV];#eta", nptbins, ptbins, netabins, etabins)
    h2_BTaggingMEff_Num_c     = ROOT.TH2D("h2_BTaggingMEff_Num_c", ";p_{T} [GeV];#eta", nptbins, ptbins, netabins, etabins)
    h2_BTaggingMEff_Num_udsg  = ROOT.TH2D("h2_BTaggingMEff_Num_udsg", ";p_{T} [GeV];#eta", nptbins, ptbins, netabins, etabins)
    h2_BTaggingTEff_Num_b     = ROOT.TH2D("h2_BTaggingTEff_Num_b", ";p_{T} [GeV];#eta", nptbins, ptbins, netabins, etabins)
    h2_BTaggingTEff_Num_c     = ROOT.TH2D("h2_BTaggingTEff_Num_c", ";p_{T} [GeV];#eta", nptbins, ptbins, netabins, etabins)
    h2_BTaggingTEff_Num_udsg  = ROOT.TH2D("h2_BTaggingTEff_Num_udsg", ";p_{T} [GeV];#eta", nptbins, ptbins, netabins, etabins)
    #++++++++++++++++++++++++++++++++++
    #++   looping over the events    ++
    #++++++++++++++++++++++++++++++++++
    for i in range(chain.GetEntries()):
        #++++++++++++++++++++++++++++++++++
        #++        taking objects        ++
        #++++++++++++++++++++++++++++++++++
        if Debug:
            if i > 2000:
                break
        if not Debug and i%5000 == 0:
            print("Event #", i+1, " out of ", chain.GetEntries())
        chain.GetEntry(i)
        njets = chain.nJet
        
        ###########################################
        ## Selecting only tight jets with pt>30  ##
        ###########################################
        for ijet in range(chain.nJet):
            if not (chain.Jet_jetId[ijet]==6 and chain.Jet_pt_nom[ijet] > 30):
                continue #tight jets with pT > 30 GeV
            if(abs(chain.Jet_partonFlavour[ijet]) == 5):
                h2_BTaggingEff_Denom_b.Fill(chain.Jet_pt_nom[ijet], abs(chain.Jet_eta[ijet]))
                if(chain.Jet_btagDeepFlavB[ijet] > WPbtagger[str(era)]['L']):
                    h2_BTaggingLEff_Num_b.Fill(chain.Jet_pt_nom[ijet], abs(chain.Jet_eta[ijet]))
                if(chain.Jet_btagDeepFlavB[ijet] > WPbtagger[str(era)]['M']):
                    h2_BTaggingMEff_Num_b.Fill(chain.Jet_pt_nom[ijet], abs(chain.Jet_eta[ijet]))
                if(chain.Jet_btagDeepFlavB[ijet] > WPbtagger[str(era)]['T']):
                    h2_BTaggingTEff_Num_b.Fill(chain.Jet_pt_nom[ijet], abs(chain.Jet_eta[ijet]))
            elif(abs(chain.Jet_partonFlavour[ijet]) == 4):
                h2_BTaggingEff_Denom_c.Fill(chain.Jet_pt_nom[ijet], abs(chain.Jet_eta[ijet]))
                if(chain.Jet_btagDeepFlavB[ijet] > WPbtagger[str(era)]['L']):
                    h2_BTaggingLEff_Num_c.Fill(chain.Jet_pt_nom[ijet], abs(chain.Jet_eta[ijet]))
                if(chain.Jet_btagDeepFlavB[ijet] > WPbtagger[str(era)]['M']):
                    h2_BTaggingMEff_Num_c.Fill(chain.Jet_pt_nom[ijet], abs(chain.Jet_eta[ijet]))
                if(chain.Jet_btagDeepFlavB[ijet] > WPbtagger[str(era)]['T']):
                    h2_BTaggingTEff_Num_c.Fill(chain.Jet_pt_nom[ijet], abs(chain.Jet_eta[ijet]))
            else:
                h2_BTaggingEff_Denom_udsg.Fill(chain.Jet_pt_nom[ijet], abs(chain.Jet_eta[ijet]))
                if(chain.Jet_btagDeepFlavB[ijet] > WPbtagger[str(era)]['L']):
                    h2_BTaggingLEff_Num_udsg.Fill(chain.Jet_pt_nom[ijet], abs(chain.Jet_eta[ijet]))
                if(chain.Jet_btagDeepFlavB[ijet] > WPbtagger[str(era)]['M']):
                    h2_BTaggingMEff_Num_udsg.Fill(chain.Jet_pt_nom[ijet], abs(chain.Jet_eta[ijet]))
                if(chain.Jet_btagDeepFlavB[ijet] > WPbtagger[str(era)]['T']):
                    h2_BTaggingTEff_Num_udsg.Fill(chain.Jet_pt_nom[ijet], abs(chain.Jet_eta[ijet]))
                    
    outTreeFile.cd()
    h2_BTaggingEff_Denom_b.Write()
    h2_BTaggingEff_Denom_c.Write()
    h2_BTaggingEff_Denom_udsg.Write()
    h2_BTaggingLEff_Num_b.Write()
    h2_BTaggingLEff_Num_c.Write()
    h2_BTaggingLEff_Num_udsg.Write()
    h2_BTaggingMEff_Num_b.Write()
    h2_BTaggingMEff_Num_c.Write()
    h2_BTaggingMEff_Num_udsg.Write()
    h2_BTaggingTEff_Num_b.Write()
    h2_BTaggingTEff_Num_c.Write()
    h2_BTaggingTEff_Num_udsg.Write()
    
    h2_LEff_b = ROOT.TEfficiency(h2_BTaggingLEff_Num_b.Clone(), h2_BTaggingEff_Denom_b.Clone())
    h2_LEff_b.SetName("h2_LEff_b")
    h2_LEff_c = ROOT.TEfficiency(h2_BTaggingLEff_Num_c.Clone(), h2_BTaggingEff_Denom_c.Clone())
    h2_LEff_c.SetName("h2_LEff_c")
    h2_LEff_udsg = ROOT.TEfficiency(h2_BTaggingLEff_Num_udsg.Clone(), h2_BTaggingEff_Denom_udsg.Clone())
    h2_LEff_udsg.SetName("h2_LEff_udsg")
    h2_MEff_b = ROOT.TEfficiency(h2_BTaggingMEff_Num_b.Clone(), h2_BTaggingEff_Denom_b.Clone())
    h2_MEff_b.SetName("h2_MEff_b")
    h2_MEff_c = ROOT.TEfficiency(h2_BTaggingMEff_Num_c.Clone(), h2_BTaggingEff_Denom_c.Clone())
    h2_MEff_c.SetName("h2_MEff_c")
    h2_MEff_udsg = ROOT.TEfficiency(h2_BTaggingMEff_Num_udsg.Clone(), h2_BTaggingEff_Denom_udsg.Clone())
    h2_MEff_udsg.SetName("h2_MEff_udsg")
    h2_TEff_b = ROOT.TEfficiency(h2_BTaggingTEff_Num_b.Clone(), h2_BTaggingEff_Denom_b.Clone())
    h2_TEff_b.SetName("h2_TEff_b")
    h2_TEff_c = ROOT.TEfficiency(h2_BTaggingTEff_Num_c.Clone(), h2_BTaggingEff_Denom_c.Clone())
    h2_TEff_c.SetName("h2_TEff_c")
    h2_TEff_udsg = ROOT.TEfficiency(h2_BTaggingTEff_Num_udsg.Clone(), h2_BTaggingEff_Denom_udsg.Clone())
    h2_TEff_udsg.SetName("h2_TEff_udsg")
    
    h2_LEff_b.Write()
    h2_LEff_c.Write()
    h2_LEff_udsg.Write()
    h2_MEff_b.Write()
    h2_MEff_c.Write()
    h2_MEff_udsg.Write()
    h2_TEff_b.Write()
    h2_TEff_c.Write()
    h2_TEff_udsg.Write()
    
    endTime = datetime.datetime.now()
    print("Ending running at " + str(endTime))

if __name__ == "__main__":

  usage  = 'usage: %prog [options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('-e', '--era', dest='era', help='[2016apv/2016postapv/2017/2018]', default='2017', type=str)
  parser.add_argument('-o', '--outdir', dest='out', help='ouput directory', default='./', type=str)
  parser.add_argument('-i', '--infile', dest='infile', help='input file', default='./', type=str)

  args = parser.parse_args()
  
  btageff_producer(args.era, args.infile, args.out)
