#==============
# Last used:
# python compare_plots.py --inputDir 2017_sel2_mujets_kinematics_29Sep2023
#==============

#!/usr/bin/env python

import sys
import os
import array
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
print (thisdir)
#import config
#from datasets import allsamples
#from plotstyle import SimpleCanvas
sys.path.append('../../python')
from plotstyle import *
import ROOT


from argparse import ArgumentParser
parser = ArgumentParser()

parser.add_argument("--inputDir", "-i", dest="inputDir", default=None,
                    help="Provide inputDir containing histograms")
opts = parser.parse_args()

#from ROOT import *
ROOT.gROOT.SetBatch(True)
colors = {
    '200'    : ROOT.kRed,
    '350'    : ROOT.kGreen,
    '500'    : ROOT.kBlue,
    '800'    : ROOT.kCyan,
    '1000'   : ROOT.kOrange,
    'TTTo1L' : ROOT.kViolet-4,
    'zg'     :"#99ffaa",
    'wg'     :"#99eeff",
    'efake'  :"#ffee99",
    'hfake'  :"#bbaaff",
    'halo'   :"#ff9933",
    'spike'  :"#666666",
    'vvg'    :"#ff4499",
    'gjets'  :"#ffaacc",
    'minor'  :"#bb66ff",
    'top'    :"#5544ff",
    'zjets'  :"#99ffaa",
    'wjets'  :"#222222",
    'gg'     :"#bb66ff"
    }

histo_xtitle = {
    'DeepB_loose_j1_pt'  : "Leading b-jet p_{T}",
    'DeepB_loose_j2_pt'  : "2^{nd} leading b-jet p_{T}",
    'DeepB_loose_j3_pt'  : "3^{rd} leading b-jet p_{T}",
    'DeepB_loose_j1_eta' : "Leading b-jet #eta",
    'DeepB_loose_j2_eta' : "2^{nd} leading b-jet #eta",
    'DeepB_loose_j3_eta' : "3^{rd} leading b-jet #eta",
    'l1_pt'              : "Leading lepton p_{T}",
    'l1_eta'             : "Leading lepton #eta",
    'j1_pt'              : "Leading jet p_{T}",
    'MET_T1Smear_pt'     : "#slash{E}_{T} [GeV]",
    'j2_pt'              : "2^{nd} leading jet p_{T}",
    'j3_pt'              : "3^{rd} leading jet p_{T}",
    'j1_eta'             : "Leading jet #eta",
    'j2_eta'             : "2^{nd} leading jet #eta",
    'j3_eta'             : "3^{rd} leading jet #eta"
}


def makePlot(inDir, hname, xmin=0.0, xmax=100.0, year="2018", isNorm=True):
    
    wRatio = True
    
    #Get histograms
    root_file = ROOT.TFile("../%s/%s.root"%(inDir,hname))
    h_all = {}
    samples = ["200","350","500","800","1000","TTTo1L"]
    for sample in samples:
        #print ("adding histogram for sample: %s GeV",%(sample))
        h_all[sample] = root_file.Get("%s"%hname+"_"+sample)
    
    if wRatio:
        canvas = RatioCanvas(" "," ",41500)
        canvas.ytitle = 'Normalized to Unity'
        canvas.xtitle = histo_xtitle[hname]
    else:
        canvas = SimpleCanvas(" "," ",41500)
        canvas.ytitle = 'Normalized to Unity'
        canvas.xtitle = 'Jet Pt'
    canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)

    # Adding to canvas
    for i, key in enumerate(h_all):
        key = samples[i]
        print ("sample: ", key)
        h_all[key].Scale(1.0/h_all[key].Integral()) #normalize histogram
        canvas.legend.add(h_all[key], title = key, opt = 'LP', color = colors[key], fstyle = 0, lwidth = 2)
        canvas.addHistogram(h_all[key], drawOpt = 'HIST E')

    canvas.applyStyles()
    if wRatio:
        canvas.printWeb(inDir, hname, logy = True)
    else:
        canvas.printWeb(inDir, hname, logy = True)

# Main
if __name__ == "__main__":
    # plottting

    histos = ["j1_pt","j2_pt","j3_pt","j1_eta","j2_eta","j3_eta","l1_pt","l1_eta","MET_T1Smear_pt"]
    for hist in histos:
        makePlot(opts.inputDir, hist)
    
