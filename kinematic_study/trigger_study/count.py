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


class Accumulator(processor.ProcessorABC):
    def __init__(self, normfactor, era, ID_sf, region, lepton, Trig_List, nDAS_dict):
        jsonfile = open('../../data/MET_filter.json')
        MET_filters = json.load(jsonfile, object_pairs_hook=OrderedDict)
        jsonfile.close()

        jsonfile = open('../../data/sample.json')
        self.sample_json = json.load(jsonfile, object_pairs_hook=OrderedDict)
        jsonfile.close()

        self.MET_filters = MET_filters["MET_Filter"]
        self.era = era
        self.ID_sf = ID_sf
        self.region = region
        self.lepton = lepton
        self.Trig_List = Trig_List
        self.nDAS  = nDAS_dict
    def process(self, events):
        dataset = events.metadata['dataset']

        # Preliminary cut
        if self.lepton == 'Electron': region_idx = 2
        else: region_idx = 1
        events = events[events[self.region + "_region"]==region_idx]

        # Define Weight
        events['lepton_id'] = ak.unflatten(events[self.region + "_l1_id"], counts=ak.ones_like(events[self.region + "_l1_id"]))
        if dataset == 'Data':
            events['weight'] = ak.ones_like(events[self.region + "_met"])
        else:
            file_name = events.metadata['filename'].split('/')[-1]
            fin_raw   = file_name.replace('.root', '')
            sample_name = fin_raw
            normfactor = Lumi[self.era] / self.nDAS[sample_name]* self.sample_json[sample_name]['xsec'] 
            events['ID_weight'] = ak.flatten(events[self.ID_sf][events.lepton_id])
            if self.era == '2018':
                events['weight'] = events.genWeight/abs(events.genWeight)*events.puWeight*events.ID_weight*normfactor
            else:
                events['weight'] = events.genWeight/abs(events.genWeight)*events.puWeight*events.PrefireWeight*events.ID_weight*normfactor

        Base_Trig_List = ['HLT_PFMET120_PFMHT120_IDTight', 'HLT_PFHT700_PFMET85_PFMHT85_IDTight', 'HLT_PFHT800_PFMET75_PFMHT75_IDTight']

        met_cut = (events[self.region + "_met"] > 100)
        MET_filter_cut = None
        for met_filt_ in self.MET_filters:
            if met_filt_ not in events.fields: continue
            else:
                if MET_filter_cut is None: 
                    MET_filter_cut = events[met_filt_]
                else: 
                    MET_filter_cut = MET_filter_cut & events[met_filt_]

        Trig_cut = None
        for trig_ in self.Trig_List:
            if trig_ not in events.fields: continue
            else:
                if Trig_cut is None:
                    Trig_cut = events[trig_]
                else:
                    Trig_cut = Trig_cut | events[trig_]

        Base_Trig_cut = None
        for trig_ in Base_Trig_List:
            if trig_ not in events.fields:
                continue
            else:
                if Base_Trig_cut is None:
                    Base_Trig_cut = events[trig_]
                else:
                    Base_Trig_cut = Base_Trig_cut | events[trig_]

        if dataset == 'Data':
            trigger_derive_cut = met_cut & MET_filter_cut & Base_Trig_cut
        else: #TODO: need to add MET HLT to trigger
            trigger_derive_cut = met_cut & MET_filter_cut
        signal_cut = MET_filter_cut & events.n_tight_jet>2 & (events[self.region + "_met"] > 35) & (events['n_bjet_DeepB_medium']>0) & Trig_cut
        trigger_derive_overlap_signal_cut = trigger_derive_cut & signal_cut

        events_trigger_derive = events[trigger_derive_cut]
        events_signal         = events[signal_cut]
        events_overlap        = events[trigger_derive_overlap_signal_cut]

        
        return {
            dataset: {
                "trig_derive": ak.sum(events_trigger_derive.weight),
                "signal": ak.sum(events_signal.weight),
                "overlap": ak.sum(events_overlap.weight)
            }
        }
    def postprocess(self, accumulator):
        pass

def Calculate_Trigger_Scale_Factor(era, maxchunks, region, lepton, normfactor, outdir):

    tstart = time.time()
    fileset = {
        'Data': [os.path.join(inputFile_path[era],'v2','MET_{}.root'.format(subera)) for subera in subera_list[era]],
        'signal_M200': [os.path.join(inputFile_path[era], 'v2', subfile + ".root") for subfile in ['BGToTHpm_a_200_rtt06_rtc04', 'CGToBHpm_a_200_rtt06_rtc04']],
        'signal_M500': [os.path.join(inputFile_path[era], 'v2', subfile + ".root") for subfile in ['BGToTHpm_a_500_rtt06_rtc04', 'CGToBHpm_a_500_rtt06_rtc04']],
        'signal_M900': [os.path.join(inputFile_path[era], 'v2', subfile + ".root") for subfile in ['BGToTHpm_a_900_rtt06_rtc04', 'CGToBHpm_a_900_rtt06_rtc04']],

    }

    if lepton == 'Electron':
        if era == '2017' or era == '2018':
            Trig_List = ['HLT_Ele35_WPTight_Gsf', 'HLT_Ele115_CaloIdVT_GsfTrkIdT', 'HLT_Photon200']
        else:
            Trig_List = ['HLT_Ele27_WPTight_Gsf', 'HLT_Ele115_CaloIdVT_GsfTrkIdT', 'HLT_Photon175']
    else:
        if era == '2017' or era == '2018':
            Trig_List = ['HLT_IsoMu27', 'HLT_Mu50', 'HLT_TkMu100', 'HLT_OldMu100']
        else:
            Trig_List = ['HLT_Mu50', 'HLT_TkMu50']


    nDAS_dict = dict()
    for dataset_ in fileset:
        #nDAS_dict[dataset_] = 0.0
        if dataset_ == "Data": nDAS_dict[dataset_] = 1.0
        else:
            file_list = fileset[dataset_]
            for file_ in file_list:
                file_name = file_.split('/')[-1]
                fin_raw = file_name.replace('.root','')
                sample_ = fin_raw
                ftemp = ROOT.TFile.Open(file_, "READ")
                if sample_ not in nDAS_dict: nDAS_dict[sample_] = 0.0
                nDAS_dict[sample_] += ftemp.Get('nEventsGenWeighted').GetBinContent(1)
                ftemp.Close()

    run = processor.Runner(
        executor = processor.FuturesExecutor(compression=None, workers=16),
        schema=BaseSchema,
        chunksize=1_000_000,
        maxchunks = maxchunks,
    )

    
    if region == 'bh':
        ID_sf_name = lepton + "_topMVA_Tight_SF"
    else:
        if lepton == 'Electron':
            ID_sf_name = "Electron_MVAFall17V2noIso_WP90_SF"
        else:
            ID_sf_name = 'Muon_CutBased_MediumID_SF'

    output = run(
            fileset,
            "Events",
            processor_instance=Accumulator(normfactor=normfactor, era=era, ID_sf=ID_sf_name, region=region, lepton=lepton, Trig_List=Trig_List, nDAS_dict=nDAS_dict)
            )

    print("---------- {}  {} -------------".format(region, lepton))
    print(output)
    



if __name__ == '__main__':
    usage = 'usage: %prog [options]'
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('-e', '--era', dest='era', help='[2016apv/2016postapv/2017/2018/all]', default='2017', type=str)
    parser.add_argument('--maxchunks', dest='maxchunks', default=-1, type=int)
    parser.add_argument('--normfactor', dest='normfactor', default=1.0, type=float)
    parser.add_argument('--outdir', dest='outdir', default='./', type=str)
    args = parser.parse_args()
    if args.maxchunks == -1: args.maxchunks = None

    if not os.path.exists(args.outdir):
        os.system('mkdir -p {}'.format(args.outdir))
    os.system('mkdir -p plot')
    Eras = []
    if args.era == 'all':
        Eras = ['2016apv', '2016postapv', '2017', '2018']
    else:
        Eras = [args.era]
    print(args.normfactor)
    for era_ in Eras:
        for region in ['bh', 'boost']:
            for lepton in ['Electron', 'Muon']:
                Calculate_Trigger_Scale_Factor(era=era_, maxchunks=args.maxchunks, region=region, lepton=lepton, normfactor=args.normfactor, outdir=args.outdir)
