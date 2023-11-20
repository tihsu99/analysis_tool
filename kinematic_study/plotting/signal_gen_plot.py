import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from collections import OrderedDict
from copy import deepcopy
import ROOT
import os ,sys
thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
print (thisdir)
sys.path.append('../../python')
from plotstyle import *
from common import *

'''''
Coffea provides good structure for quick analysis, gen-study. 
Thus, simple signal kinematic is performed in this code rather than plot_histo.py
'''''

def get_decay_chain(decay_mode=dict(), mothers=[]):
  decay_chain = deepcopy(decay_mode)
  for mother in decay_mode:
    if decay_mode[mother] is None:
      decay_chain[mother] = (mothers + [mother])
      decay_chain[mother].reverse()
    else:
      decay_chain[mother] = get_decay_chain(decay_mode[mother], mothers + [mother])
  return decay_chain
  

def signal_kinematic(decay_chain = [], events=None):
  parents_command = ['(events.GenPart.hasFlags([\'isPrompt\',\'fromHardProcess\', \'isFirstCopy\']))']
  for idx, mother in enumerate(decay_chain):
    parents_command.append('(abs(events.GenPart' + '.distinctParent'*idx + '.pdgId) == ' + mother + ')')
  parents_command = ' & '.join(parents_command)
  print(parents_command)
  GenParton_ = events.GenPart[eval(parents_command)]
  GenParton_ = GenParton_[~ak.is_none(GenParton_, axis=1)]
  return GenParton_

def get_signal_genpart(decay_chain = dict(), events=None, mask_ = None):
  decay_chain_genpart = deepcopy(decay_chain)
  for mother in decay_chain:
    if isinstance(decay_chain[mother], list):
      GenPart_ = signal_kinematic(decay_chain[mother], events)
      decay_chain_genpart[mother] = GenPart_
      if mask_ is None:
        mask_ = (ak.num(GenPart_) == 1)
      else:
        mask_ = (mask_) & (ak.num(GenPart_) == 1)
    else:
      decay_chain_genpart[mother], mask_ = get_signal_genpart(decay_chain[mother], events, mask_)
  return decay_chain_genpart, mask_

def add_decay_product(decay_genpart_, mask_):
  mother_ = None
  for product in decay_genpart_:
    if isinstance(decay_genpart_[product], dict): 
      if mother_ is None:
        mother_ = add_decay_product(decay_genpart_[product], mask_)
      else:
        mother_ = add_decay_product(decay_genpart_[product], mask_) + mother_
    else:
      if mother_ is None:
        mother_ = decay_genpart_[product][mask_][:,0]
      else:
        mother_ = decay_genpart_[product][mask_][:,0] + mother_
  return mother_

def get_all_genpart(decay_genpart_, mask_):
  all_genpart = dict()
  for mother in decay_genpart_:
    all_genpart[mother] = dict()
    if isinstance(decay_genpart_[mother], dict):
      genpart_ = add_decay_product(decay_genpart_[mother], mask_)
      all_genpart[mother] = get_all_genpart(decay_genpart_[mother], mask_)
    else:
      genpart_ = decay_genpart_[mother][mask_][:,0]
    all_genpart[mother]["GenPart"] = genpart_
  return all_genpart


def print_decay(decay_mode, layer=0):
  if(layer == 0):
    print("---------decay mode---------")
  for decay in decay_mode:
    print('    '*layer + '--->' +  decay)
    if decay_mode[decay] is not None:
      print_decay(decay_mode[decay], layer+1)
    else:
      pass
  if(layer == 0):
    print("----------------------------")

def get_signal(lepton_pdgId='11', fname=None):
  decay_mode = OrderedDict({'5000003': {'5':None, '6': {'5':None, '24': {lepton_pdgId:None, str(int(lepton_pdgId)+1):None}}}})
  #decay_mode = OrderedDict({'24': {'11':None, '12':None}})
  print_decay(decay_mode)
  decay_chain = get_decay_chain(decay_mode)
  print(get_decay_chain(decay_mode))
  events = NanoEventsFactory.from_root(fname, schemaclass=NanoAODSchema.v6).events()
  decay_genpart, mask = get_signal_genpart(decay_chain, events)
  return get_all_genpart(decay_genpart, mask)

def plot_histogram(fname=dict(), lepton_pdgId='11', era='2017'):
  canvas = SimpleCanvas(" ", " ", Lumi[era])
  canvas.ytitle = "Normalized"

  Histograms = dict()
  for sig_idx, signal_name in enumerate(fname):
    signal_ = get_signal(lepton_pdgId, fname[signal_name])
    Histograms[signal_name] = ROOT.TH1F(str(signal_name), str(";mass[GeV];nEntries"), 100, 0, 1000)
    for mass in signal_["5000003"]["GenPart"].mass:
      Histograms[signal_name].Fill(mass)
    Histograms[signal_name].Scale(1./Histograms[signal_name].Integral())
    canvas.addHistogram(Histograms[signal_name], drawOpt = 'HIST E')
    canvas.legend.add(Histograms[signal_name], title=signal_name, opt = 'LP', color = Color_List_Signal[sig_idx], fstyle=0, lwidth=4)
  print(Histograms)
  canvas.applyStyles()
  canvas.printWeb('./', 'test', logy=False)

if __name__ == '__main__':
  
  fname = {"200": "/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/CGToBHpm_a_200_rtt06_rtc04.root",
           "300": "/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/CGToBHpm_a_300_rtt06_rtc04.root",
           "350": "/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/CGToBHpm_a_350_rtt06_rtc04.root",
           "400": "/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/CGToBHpm_a_400_rtt06_rtc04.root",
           "500": "/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/CGToBHpm_a_500_rtt06_rtc04.root"}
  plot_histogram(fname)
