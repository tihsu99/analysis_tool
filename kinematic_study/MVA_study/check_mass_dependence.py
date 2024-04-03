import ROOT
import os, sys
import json
import optparse, argparse
sys.path.insert(1, '../../python')
from common import *
ROOT.gStyle.SetOptStat(00000000)
import numpy as np
import matplotlib.pyplot as plt

def plot_mass_dependence_xgboost(indir, outdir):

  mass_bin = [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]

  BG_TH_AUC = ROOT.TH2D("BG_AUC(xgboost)", "AUC(xgboost);Trained mass;Test mass", len(mass_bin), 0, len(mass_bin), len(mass_bin),0, len(mass_bin))
  CG_BH_AUC = ROOT.TH2D("CG_AUC(xgboost)", "AUC(xgboost);Trained mass;Test mass", len(mass_bin), 0, len(mass_bin), len(mass_bin),0, len(mass_bin))

  c = ROOT.TCanvas()
  ROOT.gStyle.SetPaintTextFormat(".3f")

  for idx, mass in enumerate(mass_bin):
      BG_TH_AUC.GetXaxis().SetBinLabel(idx+1, str(mass))
      CG_BH_AUC.GetXaxis().SetBinLabel(idx+1, str(mass))
      dir_ = os.path.join(indir, 'CGToBHpm_a_{}_rtt06_rtc04'.format(mass))
      json_ = os.path.join(dir_, 'AUC_accross_signal.json')
      dict_ = read_json(json_)
      for idx_y, mass_y in enumerate(mass_bin):
        BG_TH_AUC.GetYaxis().SetBinLabel(idx_y+1, str(mass_y))
        CG_BH_AUC.GetYaxis().SetBinLabel(idx_y+1, str(mass_y))
        bg_auc = dict_["BGToTHpm_a_{}_rtt06_rtc04".format(mass_y)]
        cg_auc = dict_["CGToBHpm_a_{}_rtt06_rtc04".format(mass_y)]
        BG_TH_AUC.SetBinContent(idx+1, idx_y+1, bg_auc)
        CG_BH_AUC.SetBinContent(idx+1, idx_y+1, cg_auc)
  BG_TH_AUC.Draw("COLZ TEXT")
  c.SaveAs(os.path.join(outdir, "BG_AUC.png"))
  CG_BH_AUC.Draw("COLZ TEXT")
  c.SaveAs(os.path.join(outdir, "CG_AUC.png"))


def plot_mass_dependence_DNN(indir, outdir):

  mass_bin = ['M200', 'M300', 'M350', 'M400', 'M500', 'M600', 'M700', 'M800', 'M900', 'M1000', 'MassSet1', 'MassSet2', 'MassSet3']
  real_mass_bin = [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]
  CG_BH_AUC = ROOT.TH2D("CG_AUC(DNN)", "AUC(DNN);Trained mass;Test mass", len(mass_bin), 0, len(mass_bin), len(real_mass_bin),0, len(real_mass_bin))

  c = ROOT.TCanvas()
  ROOT.gStyle.SetPaintTextFormat(".3f")

  for idx, mass in enumerate(mass_bin):
      CG_BH_AUC.GetXaxis().SetBinLabel(idx+1, str(mass).replace('Mass','').replace('M',''))
      dir_ = os.path.join(indir, mass)
      json_ = os.path.join(dir_, 'AUC_accross_signal.json')
      dict_ = read_json(json_)
      for idx_y, mass_y in enumerate(dict_):
        CG_BH_AUC.GetYaxis().SetBinLabel(idx_y+1, str(mass_y))
        cg_auc = dict_[mass_y]
        CG_BH_AUC.SetBinContent(idx+1, idx_y+1, cg_auc)
  CG_BH_AUC.Draw("COLZ TEXT")
  c.SaveAs(os.path.join(outdir, "CG_AUC.png"))

def compare(indir_xgb, indir_DNN, outdir):
  
  mass_bin = [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]
  AUC = dict()
  # xgboost
  AUC['xgboost'] = []
  for mass in mass_bin:
    dir_ = os.path.join(indir_xgb, 'CGToBHpm_a_{}_rtt06_rtc04'.format(mass))
    json_ = os.path.join(dir_, 'AUC_accross_signal.json')
    dict_ = read_json(json_)
    AUC['xgboost'].append(dict_["CGToBHpm_a_{}_rtt06_rtc04".format(mass)])

  #DNN
  AUC['DNN'] = []
  for mass in mass_bin:
    dir_ = os.path.join(indir_DNN, 'M' + str(mass))
    json_ = os.path.join(dir_, 'AUC_accross_signal.json')
    dict_ = read_json(json_)
    AUC['DNN'].append(dict_[str(mass)])
 
  AUC['pNN100']  = []
  for mass in mass_bin:
    dir_ = os.path.join(indir_DNN, 'MassSet3')
    json_ = os.path.join(dir_, 'AUC_accross_signal.json')
    dict_ = read_json(json_)
    AUC['pNN100'].append(dict_[str(mass)])


  AUC['pNN200']  = []
  for mass in mass_bin:
    dir_ = os.path.join(indir_DNN, 'MassSet1')
    json_ = os.path.join(dir_, 'AUC_accross_signal.json')
    dict_ = read_json(json_)
    AUC['pNN200'].append(dict_[str(mass)])

  AUC['pNN300']  = []
  for mass in mass_bin:
    dir_ = os.path.join(indir_DNN, 'MassSet2')
    json_ = os.path.join(dir_, 'AUC_accross_signal.json')
    dict_ = read_json(json_)
    AUC['pNN300'].append(dict_[str(mass)])

  fig, ax = plt.subplots(figsize=(8,8))
  ax.set_title('Perfomance of algorithm')
  ax.set_xlabel('Mass')
  ax.set_ylabel('AUC')
  ax.plot(mass_bin, AUC['xgboost'], 'o--', c='blue', alpha=0.7, label='xgboost(individual)')
  ax.plot(mass_bin, AUC['DNN'], 'o--',  c='orange', alpha=0.7, label='DNN(individual)')
  ax.plot(mass_bin, AUC['pNN300'], 'o',  c='green',  alpha=0.7, label='DNN(parametric)[300GeV gap]')
  ax.plot(mass_bin, AUC['pNN200'], 'o',  c='red',  alpha=0.7, label='DNN(parametric)[200GeV gap]')
  ax.plot(mass_bin, AUC['pNN100'], 'o--',  c='purple',  alpha=0.7, label='DNN(parametric)[100GeV gap]')
  ax.grid(True)
  ax.set_ylim((0.8, 1.0))
  ax.legend(loc="lower right")
  fig.savefig(os.path.join(outdir, 'AUC_comparison.png'))



if __name__ == "__main__":
  usage = 'usage: %prog [options]'
  parser =  argparse.ArgumentParser(description=usage)
  parser.add_argument('--indir', type = str)
  parser.add_argument('--outdir', type=str)
  parser.add_argument('--xgboost', action='store_true')
  parser.add_argument('--DNN', action='store_true')
  parser.add_argument('--comparison', action='store_true')
  parser.add_argument('--indir_xgb', type=str)
  parser.add_argument('--indir_DNN', type=str)
  args = parser.parse_args()
  if not os.path.exists(args.outdir):
    os.system('mkdir -p {}'.format(args.outdir))

  if args.xgboost:
    plot_mass_dependence_xgboost(args.indir, args.outdir)
  if args.DNN:
    plot_mass_dependence_DNN(args.indir, args.outdir)
  if args.comparison:
    compare(args.indir_xgb, args.indir_DNN, args.outdir)
