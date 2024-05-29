import hist
import time
import matplotlib.pyplot as plt
import uproot
import awkward as np
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema, BaseSchema
import ROOT
import json
import optparse, argparse
import os, sys
sys.path.insert(1, '../../python')
from common import *
from coffea import processor
from collections import OrderedDict
ROOT.gStyle.SetOptStat(00000000)
from array import array
import re
import numpy as np


class Accumulator(processor.ProcessorABC):
  def __init__(self, normfactor, era, Ele_pT_threshold, Muon_pT_threshold, btag_wp):

    jsonfile = open('../../data/MET_filter.json')
    MET_filters = json.load(jsonfile, object_pairs_hook=OrderedDict)
    jsonfile.close()
 
    self.MET_filters = MET_filters["MET_Filter"]
    self.Ele_pT_threshold  = Ele_pT_threshold
    self.Muon_pT_threshold = Muon_pT_threshold
    self.btag_wp           = btag_wp
    self.norm_factor       = normfactor
    self.era               = era

  def process(self, events):
    dataset = events.metadata['dataset']
    hist_ = (
      hist.Hist.new
      .StrCat(["Muon", "Electron"], name="channel")
      .Variable(np.arange(1.5, 6.5, 1), name = 'nJet')
      .Variable(np.arange(-0.5, 4.5, 1), name = 'nbJet')
      .Weight() 
    )
  
    MET_filter_cut = None
    for met_filt_ in self.MET_filters:
      if met_filt_ not in events.fields: continue
      else:
        if MET_filter_cut is None:
          MET_filter_cut = events[met_filt_]
        else:
          MET_filter_cut = MET_filter_cut & events[met_filt_] 
  
    events     = events[(events['bh_met'] > 35)]
    events_mu  = events[(events['bh_region'] == 1) & (events['bh_l1_pt'] > self.Muon_pT_threshold)]
    events_ele = events[(events['bh_region'] == 2) & (events['bh_l1_pt'] > self.Ele_pT_threshold)]
    
    hist_.fill(
      channel = 'Electron',
      nJet    = events_ele['n_tight_jet'],
      nbJet   = events_ele['n_bjet_DeepB_' + self.btag_wp],
      weight  = events_ele.genWeight / abs(events_ele.genWeight) * events_ele.puWeight * self.norm_factor
    )

    hist_.fill(
      channel = 'Muon',
      nJet    = events_mu['n_tight_jet'],
      nbJet   = events_mu['n_bjet_DeepB_' + self.btag_wp],
      weight  = events_mu.genWeight / abs(events_mu.genWeight) * events_mu.puWeight * self.norm_factor
    ) 

    return {
      dataset: {
        "entries": len(events),
        "hist"   : hist_
      }
    }
   
  def postprocess(self, accumulator):
        pass

def Obtain_distribution(era, dataset, iin, maxchunks, normfactor, outdir, Ele_pT_threshold, Muon_pT_threshold):

  iin_fullpath = os.path.join(inputFile_path[era], iin)
  fileset = {
      dataset: [iin_fullpath]
  }

  run = processor.Runner(
      executor = processor.FuturesExecutor(compression=None, workers=4),
      schema   = BaseSchema,
      chunksize = 100_000,
      maxchunks = maxchunks
  )

  output = dict()
  for btag_wp_ in ['loose', 'medium', 'tight']:
    output[btag_wp_] = run(fileset,
                           "Events",
                           processor_instance=Accumulator(normfactor=normfactor, 
                                                          era=era,
                                                          Ele_pT_threshold  = Ele_pT_threshold, \
                                                          Muon_pT_threshold = Muon_pT_threshold, \
                                                          btag_wp           = btag_wp_),
                           )
  f = uproot.recreate(os.path.join(outdir, iin), compression=None)
  for btag_wp_ in output:
    f['ele_btag_{}'.format(btag_wp_)] = output[btag_wp_][dataset]['hist']['Electron', ...]
    f['mu_btag_{}'.format(btag_wp_)]  = output[btag_wp_][dataset]['hist']['Muon', ...]
  f.close()

if __name__ == '__main__':
  usage  = 'usage: %prog [options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('-e', '--era', dest='era', default='2017', type=str)
  parser.add_argument('--ele_pt', dest='ele_pt', default=35.0,   type=float)
  parser.add_argument('--mu_pt',  dest='mu_pt',   default=30.0,   type=float)
  parser.add_argument('--dataset', dest='dataset', type=str)
  parser.add_argument('--iin', dest='iin', type=str)
  parser.add_argument('--outdir', dest='outdir', default='./', type=str)
  parser.add_argument('--maxchunks', dest='maxchunks', default=-1, type=int)
  parser.add_argument('--normfactor', dest='normfactor', default=1.0, type=float)
  args = parser.parse_args()
  if args.maxchunks == -1: args.maxchunks = None
  if not os.path.exists(args.outdir):
    os.system('mkdir -p {}'.format(outdir))
  Obtain_distribution(era = args.era,
                      dataset =  args.dataset,
                      iin =  args.iin,
                      maxchunks = args.maxchunks,
                      normfactor =  args.normfactor,
                      outdir     =  args.outdir,
                      Ele_pT_threshold = args.ele_pt,
                      Muon_pT_threshold = args.mu_pt) 
 
