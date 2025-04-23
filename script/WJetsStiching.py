# This script processes W+Jets HT samples, applies event weights based on cross-sections,
# Last used:
# python -i WJetsStiching.py

import ROOT
from ROOT import TChain

# Define cross-sections (in pb) and sum of weights for each HT bin
ht_bins = {
    "HT100to200": {
        "path": "root://eoscms.cern.ch//eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/v7/WJets_HT100to200.root",
        "xsec": 1434.5,  # cross-section in pb
        "sum_weights": 47424468.0  # nEvents->GetEntries() from the file above
    },
    "HT200to400": {
        "path": "root://eoscms.cern.ch//eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/v7/WJets_HT200to400.root",
        "xsec": 383.19,
        "sum_weights": 42281979.0
    },
    "HT400to600": {
        "path": "root://eoscms.cern.ch//eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/v7/WJets_HT400to600.root",
        "xsec": 51.68,
        "sum_weights": 5468473.0
    },
    "HT600to800": {
        "path": "root://eoscms.cern.ch//eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/v7/WJets_HT600to800.root",
        "xsec": 12.53,
        "sum_weights": 5545298.0
    },
    "HT800to1200": {
        "path": "root://eoscms.cern.ch//eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/v7/WJets_HT800to1200.root",
        "xsec": 5.62,
        "sum_weights": 5088483.0
    },
    "HT1200to2500": {
        "path": "root://eoscms.cern.ch//eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/v7/WJets_HT1200to2500.root",
        "xsec": 1.32,
        "sum_weights": 4752118.0
    },
    "HT2500toInf": {
        "path": "root://eoscms.cern.ch//eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/v7/WJets_HT2500toInf.root",
        "xsec": 0.009,
        "sum_weights": 10638271.0
    }
}

# Create TChains for each HT bin
chains = {}
for label, info in ht_bins.items():
    chain = TChain("Events")
    chain.Add(info["path"])
    chains[label] = chain

# Create histograms and apply event weights
hists = {}
for label, chain in chains.items():
    xsec = ht_bins[label]["xsec"]
    sum_weights = ht_bins[label]["sum_weights"]
    weight_formula = f"genWeight * ({xsec} / {sum_weights})"  # Event weight formula

    hist = ROOT.TH1F(f"ht_{label}", f"LHE_HT for {label}", 100, 0, 3000)
    print(f"Processing {label} with {chain.GetEntries()} entries")
    chain.Draw(f"LHE_HT >> ht_{label}", weight_formula, "goff")  # Apply event weight
    hists[label] = hist

# Plot histograms
c = ROOT.TCanvas()
c.SetLogy()
ROOT.gStyle.SetOptStat(0)
colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kOrange+1, ROOT.kMagenta, ROOT.kCyan+2, ROOT.kBlack]

# Determine the maximum value across all histograms
max_value = max(hist.GetMaximum() for hist in hists.values())

for i, (label, hist) in enumerate(hists.items()):
    hist.SetLineColor(colors[i % len(colors)])
    # hist.Scale(1 / hist.Integral())  # Normalize
    hist.SetMinimum(1e-4)  # Set minimum to cover the range down to 10^-4 (to view all histograms)
    hist.SetMaximum(max_value * 1.2)
    draw_opt = "HIST" if i == 0 else "HIST SAME"
    hist.Draw(draw_opt)
    # hist.SetTitle("W+Jets HT stitching check;LHE_HT [GeV];Normalized events")
    hist.SetTitle("W+Jets HT stitching check;LHE_HT [GeV];Events")

legend = ROOT.TLegend(0.6, 0.6, 0.88, 0.88)
for label, hist in hists.items():
    legend.AddEntry(hist, label, "l")
legend.Draw()
c.SaveAs("ht_stitching_check.png")
c.SaveAs("ht_stitching_check.pdf")
c.SaveAs("ht_stitching_check.C")
# c.Close()