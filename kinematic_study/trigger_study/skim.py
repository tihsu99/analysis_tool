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
    def __init__(self, var_Dict, normfactor, era, ID_sf, region, lepton, Trig_List, variation):
        jsonfile = open('../../data/MET_filter.json')
        MET_filters = json.load(jsonfile, object_pairs_hook=OrderedDict)
        jsonfile.close()

        jsonfile = open('../../data/sample.json')
        self.sample_json = json.load(jsonfile, object_pairs_hook=OrderedDict)
        jsonfile.close()

        self.MET_filters = MET_filters["MET_Filter"]
        self.var_Dict = var_Dict
        self.normfactor = normfactor
        self.era = era
        self.ID_sf = ID_sf
        self.region = region
        self.lepton = lepton
        self.Trig_List = Trig_List
        self.variation = variation
    def process(self, events):
        dataset = events.metadata['dataset']
        if self.lepton == 'Electron':
            hist_ = (
                hist.Hist.new
                .StrCat(["num", "den"], name="eff")
                .Variable([30, 35, 50, 100, 200, 500], name="pt")
                .Variable([0, 0.8, 1.442, 1.556, 2.1, 2.5], name='eta')
                .Weight()
             )
        else:
            hist_ = (
                hist.Hist.new
                .StrCat(["num", "den"], name="eff")
                .Variable([20, 30, 40, 60, 120, 200, 500], name="pt")
                .Variable([0, 0.9, 1.2, 2.1, 2.4], name='eta')
                .Weight()
            )
        # Preliminary cut
        events = events[events["Trigger_derived_region"]==1] # Choose em channel (Veto has been applied when producing ntuples)
        if self.lepton == "Electron": 
            events = events[events["n_tight_muon"] == 1] # Use Muon as "Tag"
            events['tag_lepton_id'] = ak.unflatten(events["tightMuons_id"][:,0], counts=ak.ones_like(events[self.region + "_l1_id"]))
            if not dataset == 'Data':
                events['tag_lepton_id_sf'] = ak.flatten(events["Muon_topMVA_Tight_SF"][events.tag_lepton_id])
            if self.region == 'bh':
                events = events[events["n_tight_ele"] == 1] # Use Electron as "Probe"
                events['lepton_id']  = ak.unflatten(events["tightElectrons_id"][:,0], counts=ak.ones_like(events[self.region + "_l1_id"]))
            else:
                events = events[events["n_tight_ele_noIso"] == 1] # Use noIso Electron as "Probe"
                events['lepton_id']  = ak.unflatten(events["tightElectrons_noIso_id"][:,0], counts=ak.ones_like(events[self.region + "_l1_id"]))
            events['lepton_pt']  = ak.flatten(events['Electron_pt'][events.lepton_id])
            events['lepton_eta'] = ak.flatten(events['Electron_eta'][events.lepton_id])

        else: 
            events = events[events["n_tight_ele"] == 1] # Use Electron as "Tag"
            events['tag_lepton_id'] = ak.unflatten(events['tightElectrons_id'][:,0], counts=ak.ones_like(events[self.region+"_l1_id"]))
            if not dataset == 'Data':
                events['tag_lepton_id_sf'] = ak.flatten(events["Electron_topMVA_Tight_SF"][events.tag_lepton_id]) * ak.flatten(events["Electron_RECO_SF"][events.tag_lepton_id])
            if self.region == 'bh':
                events = events[events["n_tight_muon"] == 1] # Use Muon as "Probe"
                events['lepton_id']  = ak.unflatten(events["tightMuons_id"][:,0], counts=ak.ones_like(events[self.region + "_l1_id"]))
            else:
                events = events[events["n_tight_muon_noIso"] == 1] # Use Muon as "Probe"
                events['lepton_id']  = ak.unflatten(events["tightMuons_noIso_id"][:,0], counts=ak.ones_like(events[self.region + "_l1_id"])) 
            events['lepton_pt']  = ak.flatten(events['Muon_corrected_pt'][events.lepton_id])
            events['lepton_eta'] = ak.flatten(events['Muon_eta'][events.lepton_id])


        # Define Weight
        if dataset == 'Data':
            events['weight'] = ak.ones_like(events[self.region + "_met"])
        else:
            if self.lepton == "Electron":
                events['ID_weight'] = ak.flatten(events[self.ID_sf][events.lepton_id])*ak.flatten(events["Electron_RECO_SF"][events.lepton_id])*events.tag_lepton_id_sf
            else:
                events['ID_weight'] = ak.flatten(events[self.ID_sf][events.lepton_id])*events.tag_lepton_id_sf
            if self.era == '2018':
                events['weight'] = events.genWeight/abs(events.genWeight)*events.puWeight*events.ID_weight*self.normfactor
            else:
                events['weight'] = events.genWeight/abs(events.genWeight)*events.puWeight*events.PrefireWeight*events.ID_weight*self.normfactor

        Base_Trig_List = ['HLT_PFMET120_PFMHT120_IDTight', 'HLT_PFHT700_PFMET85_PFMHT85_IDTight', 'HLT_PFHT800_PFMET75_PFMHT75_IDTight', 'HLT_PFMET250_HBHECleaned', 'HLT_PFHT500_PFMET100_PFMHT100_IDTight']

        if dataset == 'Data':
            events["met"] = events['MET_T1_pt']
        else:
            events["met"] = events['MET_T1Smear_pt']


        if(self.variation == "nPV_up"):
            basic_cut = ((events["met"] > 100) & (events["PV_npvsGood"] > 30))
        elif(self.variation == "nPV_down"):
            basic_cut = ((events["met"] > 100) & (events["PV_npvsGood"] <= 30))
        elif(self.variation == "nJet_up"):
            basic_cut = ((events["met"] > 100) & (events["n_tight_jet"] > 3))
        elif(self.variation == "nJet_down"):
            basic_cut = ((events["met"] > 100) & (events["n_tight_jet"] <= 3))
        else:
            basic_cut = (events["met"] > 100)

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
                if 'HLT_passEle32WPTight' == trig_:
                   trig_cut_ = (events[trig_] == 1)
                else:
                   trig_cut_ = events[trig_]
                if Trig_cut is None: 
                    Trig_cut = trig_cut_
                else:
                    Trig_cut = Trig_cut | trig_cut_

        Base_Trig_cut = None
        for trig_ in Base_Trig_List:
            if trig_ not in events.fields:
                print(trig_, 'not in NanoAOD')
                continue
            else:
                if Base_Trig_cut is None:
                    Base_Trig_cut = events[trig_]
                else:
                    Base_Trig_cut = Base_Trig_cut | events[trig_]

        basic_cut = basic_cut & MET_filter_cut & Base_Trig_cut
        cut_den = (basic_cut)
        cut_num = (basic_cut) & (Trig_cut)


        hist_.fill(
            eff='num',
            pt=events[cut_num]['lepton_pt'],
            eta=abs(events[cut_num]['lepton_eta']),
            weight = events[cut_num].weight
        )\
        .fill(
            eff='den',
            pt=events[cut_den]['lepton_pt'],
            eta=abs(events[cut_den]["lepton_eta"]),
            weight = events[cut_den].weight
        )

        num = hist_["num",:,:].values()
        den = hist_["den",:,:].values()

        events_total = events[basic_cut]
        events_pass  = events[(basic_cut) & (Trig_cut)]
        events_fail  = events[(basic_cut) & ~(Trig_cut)]
        distribution_Dict = dict()
        for var_ in self.var_Dict:
            if ("Electron" in var_) or ("Muon" in var_):
                var_total = ak.flatten(events_total[var_][events_total.lepton_id])
                var_pass  = ak.flatten(events_pass[var_][events_pass.lepton_id])
                var_fail  = ak.flatten(events_fail[var_][events_fail.lepton_id])
            else:
                var_total = events_total[var_]
                var_pass  = events_pass[var_]
                var_fail  = events_fail[var_]
            distribution_ = (
                hist.Hist.new
                .StrCat(["total", "pass", "fail"], name='category')
                .Variable(self.var_Dict[var_], name='var')
                .Weight()
            )
            distribution_.fill(
                category = 'total',
                var = var_total,
                weight = events_total.weight
            )\
            .fill(
                category = 'pass',
                var = var_pass,
                weight = events_pass.weight
            )\
            .fill(
                category = 'fail',
                var = var_fail,
                weight = events_fail.weight
            )
            distribution_Dict[var_] = distribution_

        return {
            dataset: {
                "entries": len(events),
                "hist_": hist_,
                "distribution_": distribution_Dict
            }
        }
    def postprocess(self, accumulator):
        pass

def Calculate_Trigger_Scale_Factor(era, dataset, iin, maxchunks, region, lepton, normfactor, outdir, variation):

    tstart = time.time()

    iin_fullpath = os.path.join(inputFile_path[era], iin).replace('v2', 'v3')
    fileset = {
        dataset: [iin_fullpath]
    }


    if lepton == 'Electron':
        Var_Dict = {
            'Electron_pt': np.linspace(0,300,30),
            'Electron_eta': np.linspace(-2.5,2.5,10),
            #'Electron_dr03TkSumPt': np.linspace(0,2,40),
            #'Electron_eInvMinusPInv':np.linspace(-0.02,0.02,20),
            #'Electron_hoe':np.linspace(0,6,60),
            #'Electron_miniPFRelIso_all': np.linspace(0,2,20),
            #'Electron_miniPFRelIso_chg': np.linspace(0,2,20),
            #'Electron_pfRelIso03_all': np.linspace(0,2,20),
            #'Electron_pfRelIso03_chg': np.linspace(0,2,20),
            #'Electron_sieie': np.linspace(0,0.04,40)
        }
        if era == '2017':
            Trig_List = ['HLT_passEle32WPTight', 'HLT_Ele115_CaloIdVT_GsfTrkIdT', 'HLT_Photon200']
        else if era == '2018':
            Trig_List = ['HLT_Ele32_WPTight_Gsf',  'HLT_Ele115_CaloIdVT_GsfTrkIdT', 'HLT_Photon200']
        else:
            Trig_List = ['HLT_Ele27_WPTight_Gsf', 'HLT_Ele115_CaloIdVT_GsfTrkIdT', 'HLT_Photon175']
    else:
        Var_Dict = {
            'Muon_corrected_pt': np.linspace(0, 300, 30),
            'Muon_eta': np.linspace(-2.5, 2.5, 10),
            #'Muon_miniPFRelIso_all': np.linspace(0,2,20),
            #'Muon_miniPFRelIso_chg': np.linspace(0,2,20),
            #'Muon_pfRelIso03_all': np.linspace(0,2,20),
            #'Muon_pfRelIso03_chg': np.linspace(0,2,20)
        }
        if era == '2017' or era == '2018':
            Trig_List = ['HLT_IsoMu27', 'HLT_Mu50', 'HLT_TkMu100', 'HLT_OldMu100']
        else:
            Trig_List = ['HLT_Mu50', 'HLT_TkMu50']


    run = processor.Runner(
        executor = processor.FuturesExecutor(compression=None, workers=4),
        schema=BaseSchema,
        chunksize=100_000,
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
            processor_instance=Accumulator(var_Dict=Var_Dict, normfactor=normfactor, era=era, ID_sf=ID_sf_name, region=region, lepton=lepton, Trig_List=Trig_List, variation=variation)
            )
    
    f = uproot.recreate(os.path.join(outdir, "{}_{}_".format(region, lepton) + iin))
    for dataset_ in fileset:
        f['num'] = output[dataset_]["hist_"][0,:,:]
        f['den'] = output[dataset_]["hist_"][1,:,:]
        for var_ in Var_Dict:
            f["{}_total".format(var_)] = output[dataset_]["distribution_"][var_][0,:]
            f["{}_pass".format(var_)] = output[dataset_]["distribution_"][var_]["pass",:]
            f["{}_fail".format(var_)] = output[dataset_]["distribution_"][var_]["fail",:]
    f.close()



if __name__ == '__main__':
    usage = 'usage: %prog [options]'
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('-e', '--era', dest='era', help='[2016apv/2016postapv/2017/2018/all]', default='2017', type=str)
    parser.add_argument('--dataset', dest='dataset', type=str)
    parser.add_argument('--iin', dest='iin', type=str)
    parser.add_argument('--region', dest='region', type=str)
    parser.add_argument('--lepton', dest='lepton', type=str)
    parser.add_argument('--maxchunks', dest='maxchunks', default=-1, type=int)
    parser.add_argument('--normfactor', dest='normfactor', default=1.0, type=float)
    parser.add_argument('--outdir', dest='outdir', default='./', type=str)
    parser.add_argument('--variation', dest='variation', default='nominal', type=str)
    args = parser.parse_args()
    if args.maxchunks == -1: args.maxchunks = None

    args.outdir = os.path.join(args.outdir, args.variation)

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
        Calculate_Trigger_Scale_Factor(era=era_, dataset=args.dataset, iin=args.iin, maxchunks=args.maxchunks, region=args.region, lepton=args.lepton, normfactor=args.normfactor, outdir=args.outdir, variation=args.variation)
