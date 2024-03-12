#!/bin/env python3
import os
import sys
import ROOT
import math
import datetime
import copy
from array import array
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import InputTree, Event, Collection

def bjet_filter(jets, era, WP): #returns collections of b jets and no b jets (discriminated with btaggers)
    # b-tag working points: mistagging efficiency tight = 0.1%, medium 1% and loose = 10%
    WPbtagger = {
        '2016preVFP':{'L': 0.0508, 'M': 0.2598, 'T': 0.6502},
        '2016postVFP':{'L': 0.0480, 'M': 0.2489, 'T': 0.6377},
        '2017':{'L': 0.0532, 'M': 0.3040, 'T': 0.7476},
        '2018':{'L': 0.0490, 'M': 0.2783, 'T': 0.7100}
    }
    threshold = WPbtagger[str(era)][str(WP)]
    return list(filter(lambda x : x.btagDeepFlavB >= threshold, jets)), list(filter(lambda x : x.btagDeepFlavB < threshold, jets))


if sys.argv[3] == 'remote':
    Debug = False
else:
    Debug = True
path, infile = sys.argv[1].rsplit("/", 1)
if "2016apv" in path:
    era = '2016preVFP'
elif "2016" in path:
    era = '2016postVFP'
elif "2017" in path:
    era = '2017'
elif "2018" in path:
    era = '2018'
else:
    print("era is not correctly set!")
print(infile)

startTime = datetime.datetime.now()
print("Starting running at " + str(startTime))

ROOT.gROOT.SetBatch()

chain = ROOT.TChain('Events')
chain.Add(path + "/" + infile)
tree = InputTree(chain)
print("Number of entries: " +str(tree.GetEntries()))


username = str(os.environ.get('USER'))
inituser = str(os.environ.get('USER')[0])
folder = sys.argv[2]
if not os.path.exists("/eos/user/" + inituser + "/" + username + "/Hplus/nosynch/" + folder):
    os.makedirs("/eos/user/" + inituser + "/" + username +"/Hplus/nosynch/" + folder)
outpath = "/eos/user/" + inituser + "/" + username +"/Hplus/nosynch/" + folder + "/"
#++++++++++++++++++++++++++++++++++
#++   branching the new trees    ++
#++++++++++++++++++++++++++++++++++
outTreeFile = ROOT.TFile(outpath + infile.replace(".root","") + "_out.root", "RECREATE") #some name of the output file

#++++++++++++++++++++++++++++++++++
#++      Efficiency studies      ++
#++++++++++++++++++++++++++++++++++
ptNBins = 100
ptMin = 0
ptMax = 1000.
etaNBins = 60
etaMin = -3.
etaMax = 3.
ptbins = array.array('f', [30., 40., 60., 80, 140., 200., 300, 500, 1000])
etabins = array.array('f', [0.0, 0.8, 1.6, 2.5])
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
for i in range(tree.GetEntries()):
    #++++++++++++++++++++++++++++++++++
    #++        taking objects        ++
    #++++++++++++++++++++++++++++++++++
    if Debug:
        if i > 2000:
            break
    if not Debug and i%5000 == 0:
        print("Event #", i+1, " out of ", tree.GetEntries())
    event = Event(tree,i)
    jets = Collection(event, "Jet")
    njets = len(jets)

    ###########################################
    ## Selecting only tight jets with pt>30  ##
    ###########################################
    for jet in jets:
        if not (jet.jetId==6 and jet.pt_nom > 30):
            continue #tight jets with pT > 30 GeV
        if(abs(jet.partonFlavour) == 5):
            h2_BTaggingEff_Denom_b.Fill(jet.pt, abs(jet.eta))
            if(len(bjet_filter([jet], era, 'L')[0])==1):
                h2_BTaggingLEff_Num_b.Fill(jet.pt, abs(jet.eta))
            if(len(bjet_filter([jet], era, 'M')[0])==1):
                h2_BTaggingMEff_Num_b.Fill(jet.pt, abs(jet.eta))
            if(len(bjet_filter([jet], era, 'T')[0])==1):
                h2_BTaggingTEff_Num_b.Fill(jet.pt, abs(jet.eta))
        elif(abs(jet.partonFlavour) == 4):
            h2_BTaggingEff_Denom_c.Fill(jet.pt, abs(jet.eta))
            if(len(bjet_filter([jet], era, 'L')[0])==1):
                h2_BTaggingLEff_Num_c.Fill(jet.pt, abs(jet.eta))
            if(len(bjet_filter([jet], era, 'M')[0])==1):
                h2_BTaggingMEff_Num_c.Fill(jet.pt, abs(jet.eta))
            if(len(bjet_filter([jet], era, 'T')[0])==1):
                h2_BTaggingTEff_Num_c.Fill(jet.pt, abs(jet.eta))
        else:
            h2_BTaggingEff_Denom_udsg.Fill(jet.pt, abs(jet.eta))
            if(len(bjet_filter([jet], era, 'L')[0])==1):
                h2_BTaggingLEff_Num_udsg.Fill(jet.pt, abs(jet.eta))
            if(len(bjet_filter([jet], era, 'M')[0])==1):
                h2_BTaggingMEff_Num_udsg.Fill(jet.pt, abs(jet.eta))
            if(len(bjet_filter([jet], era, 'T')[0])==1):
                h2_BTaggingTEff_Num_udsg.Fill(jet.pt, abs(jet.eta))

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
