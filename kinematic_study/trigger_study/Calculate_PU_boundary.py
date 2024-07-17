import awkward as ak
import numpy as np
import json
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema, BaseSchema
from runcondor import fileset
import os, sys
sys.path.insert(1, '../../python')
from common import *

PV_Cut = dict()

for era in ['2016apv', '2016postapv', '2017', '2018']:
  files = fileset[era]['Electron']['Data'] # Use SingleMuon Data to measure nPV
  nPV_list = []
  for file_ in files:
    print(file_)
    events = NanoEventsFactory.from_root(
      os.path.join(inputFile_path[era], file_),
      schemaclass = BaseSchema,
      treepath = "Events",
    ).events()

    MET_filters = read_json('../../data/MET_filter.json')
    MET_filter_cut = None
    for met_filt_ in MET_filters['MET_Filter']:
      if met_filt_ not in events.fields: continue
      else:
        if MET_filter_cut is None: MET_filter_cut = events[met_filt_]
        else: MET_filter_cut = MET_filter_cut & events[met_filt_]

    basic_cut = ((events["MET_T1_pt"] > 30) & MET_filter_cut) & (events["Trigger_derived_region"]==1)
    GoodEvent = events[basic_cut]
    nPV_list.append(ak.to_numpy(GoodEvent["PV_npvsGood"]))
  nPV_list = np.concatenate(nPV_list)
  PV_Cut[era] = np.quantile(nPV_list, 0.5)
  print(era, PV_Cut[era])
print(PV_Cut)
store_json(PV_Cut, 'nPV_quantile50.json')
