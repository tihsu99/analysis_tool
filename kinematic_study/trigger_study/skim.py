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
from coffea.nanoevents.methods import vector

def get_trigger(events, Trig_List):
    Trig_cut = None
    for trig_ in Trig_List:
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
    return Trig_cut


class Accumulator(processor.ProcessorABC):
    def __init__(self, var_Dict, normfactor, era, ID_sf, region, lepton, Trig_List, Trig_Veto_List, variation, Base_Trig_List, Base_Trig_Veto_List):
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
        self.Trig_Veto_List = Trig_Veto_List
        self.Base_Trig_List = Base_Trig_List
        self.Base_Trig_Veto_List = Base_Trig_Veto_List
        self.variation = variation
        self.nPV_Cut   = read_json('nPV_quantile50.json')
    def process(self, events):
        dataset = events.metadata['dataset']
        if self.lepton == 'Electron':
            if (self.era == '2017') or (self.era == '2018'): pt_bin = [30, 35, 60, 115, 200, 500]
            else: pt_bin = [30, 35, 60, 115, 175, 500]
            hist_ = (
                hist.Hist.new
                .StrCat(["num", "den", "pure_Trig", "basic_cut"], name="eff")
                .Variable(pt_bin, name="pt")
                .Variable([0, 0.8, 1.442, 1.556, 2.5], name='eta')
                .Weight()
             )
        else:
            hist_ = (
                hist.Hist.new
                .StrCat(["num", "den", "pure_Trig", "basic_cut"], name="eff")
                .Variable([20, 30, 50, 100, 500], name="pt")
                .Variable([0, 0.9, 1.5, 2.1, 2.4], name='eta')
                .Weight()
            )
        # Preliminary cut
        events = events[events["Trigger_derived_region"]==1] # Choose em channel (Veto has been applied when producing ntuples)
        if self.lepton == "Electron": 
            events = events[events["n_tight_muon"] == 1] # Use Muon as "Tag"
            events['tag_lepton_id'] = ak.unflatten(events["tightMuons_id"][:,0], counts=ak.ones_like(events[self.region + "_l1_id"]))
            events['tag_pt']   = ak.flatten(events['Muon_pt'][events.tag_lepton_id])
            events['tag_eta']  = ak.flatten(events['Muon_eta'][events.tag_lepton_id])
            events['tag_phi']  = ak.flatten(events['Muon_phi'][events.tag_lepton_id])
            events['tag_mass'] = ak.flatten(events['Muon_mass'][events.tag_lepton_id])
            events = events[events.tag_pt > 40] # Tag Muon pT cut

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
            events['lepton_phi'] = ak.flatten(events['Electron_phi'][events.lepton_id])
            events['lepton_mass']= ak.flatten(events['Electron_mass'][events.lepton_id])

        else: 
            events = events[events["n_tight_ele"] == 1] # Use Electron as "Tag"
            events['tag_lepton_id'] = ak.unflatten(events['tightElectrons_id'][:,0], counts=ak.ones_like(events[self.region+"_l1_id"]))
            events['tag_pt']  = ak.flatten(events['Electron_pt'][events.tag_lepton_id])
            events['tag_eta'] = ak.flatten(events['Electron_eta'][events.tag_lepton_id])
            events['tag_phi'] = ak.flatten(events['Electron_phi'][events.tag_lepton_id])
            events['tag_mass']= ak.flatten(events['Electron_mass'][events.tag_lepton_id])
            events = events[events.tag_pt > 50] # Tag Electron pT cut

            if not dataset == 'Data':
                events['tag_lepton_id_sf'] = ak.flatten(events["Electron_topMVA_Tight_SF"][events.tag_lepton_id]) * ak.flatten(events["Electron_RECO_SF"][events.tag_lepton_id])
            if self.region == 'bh':
                events = events[events["n_tight_muon"] == 1] # Use Muon as "Probe"
                events['lepton_id']  = ak.unflatten(events["tightMuons_id"][:,0], counts=ak.ones_like(events[self.region + "_l1_id"]))
            else:
                events = events[events["n_tight_muon_noIso"] == 1] # Use Muon as "Probe"
                events['lepton_id']  = ak.unflatten(events["tightMuons_noIso_id"][:,0], counts=ak.ones_like(events[self.region + "_l1_id"])) 

            events['lepton_pt']  = ak.flatten(events['Muon_pt'][events.lepton_id])
            events['lepton_eta'] = ak.flatten(events['Muon_eta'][events.lepton_id])
            events['lepton_phi'] = ak.flatten(events['Muon_phi'][events.lepton_id])
            events['lepton_mass']= ak.flatten(events['Muon_mass'][events.lepton_id])

        lepton_v4 = ak.zip(
            {
              "pt":   events["lepton_pt"],
              "eta":  events["lepton_eta"],
              "phi":  events["lepton_phi"],
              "mass": events["lepton_mass"],
            },
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.behavior,
        )
        tag_v4 = ak.zip(
            {
              "pt":   events["tag_pt"],
              "eta":  events["tag_eta"],
              "phi":  events["tag_phi"],
              "mass": events["tag_mass"],
            },
            with_name="PtEtaPhiMLorentzVector",
            behavior=vector.behavior,
        )
        events['inv_mass'] = (lepton_v4 + tag_v4).mass


        events = events[events['inv_mass'] > 20] # Veto QCD for data 

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
                events['weight'] = events.genWeight/abs(events.genWeight)*events.puWeight*events.L1PreFiringWeight_Nom*events.ID_weight*self.normfactor

        if dataset == 'Data':
            events["met"] = events['MET_T1_pt']
        else:
            events["met"] = events['MET_T1Smear_pt']

        ###############
        ##  MET CUT  ##
        ###############

        MET_Cut = 30
        if(self.variation == "nPV_up"):
            basic_cut = ((events["met"] > MET_Cut) & (events["PV_npvsGood"] > int(self.nPV_Cut[self.era])))
        elif(self.variation == "nPV_down"):
            basic_cut = ((events["met"] > MET_Cut) & (events["PV_npvsGood"] <= int(self.nPV_Cut[self.era])))
        elif(self.variation == "nJet_up"):
            basic_cut = ((events["met"] > MET_Cut) & (events["n_tight_jet"] > 2))
        elif(self.variation == "nJet_down"):
            basic_cut = ((events["met"] > MET_Cut) & (events["n_tight_jet"] <= 2))
        else:
            basic_cut = (events["met"] > MET_Cut)

        MET_filter_cut = None
        for met_filt_ in self.MET_filters:
            if met_filt_ not in events.fields: continue
            else:
                if MET_filter_cut is None: 
                    MET_filter_cut = events[met_filt_]
                else: 
                    MET_filter_cut = MET_filter_cut & events[met_filt_]

        Trig_cut = get_trigger(events, self.Trig_List)
        Trig_Veto_cut = get_trigger(events, self.Trig_Veto_List)
        Base_Trig_cut = get_trigger(events, self.Base_Trig_List)
        Base_Trig_Veto_cut = get_trigger(events, self.Base_Trig_Veto_List)

        Trig_cut = Trig_cut & ~Trig_Veto_cut if (Trig_Veto_cut is not None) else Trig_cut
        Base_Trig_cut = Base_Trig_cut & ~Base_Trig_Veto_cut if (Base_Trig_Veto_cut is not None) else Base_Trig_cut
        basic_cut = basic_cut & MET_filter_cut

        basic_cut_Base_Triggered = basic_cut & Base_Trig_cut
        cut_den = (basic_cut_Base_Triggered)
        cut_num = (basic_cut_Base_Triggered) & (Trig_cut)
        cut_pure_Trig = basic_cut & Trig_cut

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
        )\
        .fill(
            eff='pure_Trig',
            pt=events[cut_pure_Trig]['lepton_pt'],
            eta=abs(events[cut_pure_Trig]['lepton_eta']),
            weight=events[cut_pure_Trig].weight
        )\
        .fill(
           eff='basic_cut',
           pt=events[basic_cut]['lepton_pt'],
           eta=abs(events[basic_cut]['lepton_eta']),
           weight=events[basic_cut].weight
        )

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

    iin_fullpath = os.path.join(inputFile_path[era], iin)
    fileset = {
        dataset: [iin_fullpath]
    }


    ##########################
    ##  Trigger Definition  ##
    ##########################

    if era == '2017':
      Muon_Trig_List = ['HLT_IsoMu27', 'HLT_Mu50', 'HLT_TkMu100', 'HLT_OldMu100']
      Muon_Trig_Veto_List = []
      if 'SingleEG' in iin:
        Electron_Trig_List = ['HLT_passEle32WPTight', 'HLT_Ele115_CaloIdVT_GsfTrkIdT']
        Electron_Trig_Veto_List = []
      elif 'SinglePhoton' in iin:
        Electron_Trig_List = ['HLT_Photon200']
        Electron_Trig_Veto_List = ['HLT_passEle32WPTight', 'HLT_Ele115_CaloIdVT_GsfTrkIdT']
      else:
        Electron_Trig_List = ['HLT_passEle32WPTight', 'HLT_Ele115_CaloIdVT_GsfTrkIdT', 'HLT_Photon200']
        Electron_Trig_Veto_List = []
    elif era == '2018':
        Electron_Trig_List = ['HLT_Ele32_WPTight_Gsf', 'HLT_Ele115_CaloIdVT_GsfTrkIdT', 'HLT_Photon200']
        Electron_Trig_Veto_List = []
        Muon_Trig_List     = ['HLT_IsoMu27', 'HLT_Mu50', 'HLT_TkMu100', 'HLT_OldMu100']
        Muon_Trig_Veto_List = []
    else:
        Muon_Trig_List = ['HLT_IsoMu24', 'HLT_IsoTkMu24', 'HLT_Mu50', 'HLT_TkMu50']
        Muon_Trig_Veto_List = []
        if 'SingleEG' in iin:
          Electron_Trig_List =  ['HLT_Ele27_WPTight_Gsf', 'HLT_Ele115_CaloIdVT_GsfTrkIdT']
          Electron_Trig_Veto_List = []
        elif 'SinglePhoton' in iin:
          Electron_Trig_List = ['HLT_Photon175']
          Electron_Trig_Veto_List =  ['HLT_Ele27_WPTight_Gsf', 'HLT_Ele115_CaloIdVT_GsfTrkIdT']
        else:
          Electron_Trig_List =  ['HLT_Ele27_WPTight_Gsf', 'HLT_Ele115_CaloIdVT_GsfTrkIdT', 'HLT_Photon175']
          Electron_Trig_Veto_List = []




    if lepton == 'Electron':
        Var_Dict = {
            'Electron_pt': np.linspace(0,300,30),
            'Electron_eta': np.linspace(-2.5,2.5,10),
            'PV_npvsGood': np.linspace(0,60,6)
        }

        # Reference: https://twiki.cern.ch/twiki/bin/view/CMS/EgHLTRunIISummary
        Trig_List = Electron_Trig_List
        Base_Trig_List = Muon_Trig_List
        Trig_Veto_List = Electron_Trig_Veto_List
        Base_Trig_Veto_List = Muon_Trig_Veto_List

    else:
        Var_Dict = {
            'Muon_pt': np.linspace(0, 300, 30),
            'Muon_eta': np.linspace(-2.4, 2.4, 10),
            'PV_npvsGood': np.linspace(0,60,6)
        }
        # Reference https://twiki.cern.ch/twiki/bin/view/CMS/MuonHLT#Details_for_each_year
        Trig_List = Muon_Trig_List
        Base_Trig_List = Electron_Trig_List
        Trig_Veto_List = Muon_Trig_Veto_List
        Base_Trig_Veto_List = Electron_Trig_Veto_List

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
            processor_instance=Accumulator(var_Dict=Var_Dict, normfactor=normfactor, era=era, ID_sf=ID_sf_name, region=region, lepton=lepton, Trig_List=Trig_List, variation=variation, Base_Trig_List=Base_Trig_List, Trig_Veto_List = Trig_Veto_List, Base_Trig_Veto_List = Base_Trig_Veto_List)
            )
    
    f = uproot.recreate(os.path.join(outdir, "{}_{}_".format(region, lepton) + iin))
    for dataset_ in fileset:
        f['num'] = output[dataset_]["hist_"][0,:,:]
        f['den'] = output[dataset_]["hist_"][1,:,:]
        f['pure_Trig'] = output[dataset_]["hist_"][2,:,:]
        f['basic_cut'] = output[dataset_]["hist_"][3,:,:]
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
    parser.add_argument('--trigger_json', dest = 'trigger_json', type=str, default = '../../data/trigger.json')
    parser.add_argument('--iin', dest='iin', type=str)
    parser.add_argument('--region', dest='region', type=str)
    parser.add_argument('--lepton', dest='lepton', type=str)
    parser.add_argument('--maxchunks', dest='maxchunks', default=-1, type=int)
    parser.add_argument('--normfactor', dest='normfactor', default=1.0, type=float)
    parser.add_argument('--outdir', dest='outdir', default='./', type=str)
    parser.add_argument('--variation', dest='variation', default='nominal', type=str)
    args = parser.parse_args()
    if args.maxchunks == -1: args.maxchunks = None

    args.outdir = os.path.join(args.outdir, args.era, args.variation)

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
