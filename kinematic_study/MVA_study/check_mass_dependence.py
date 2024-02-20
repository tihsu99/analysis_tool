import ROOT
import os, sys
import json
import optparse, argparse
sys.path.insert(1, '../../python')
from common import *
ROOT.gStyle.SetOptStat(00000000)


def plot_mass_dependence(indir):

  mass_bin = [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]

  BG_TH_AUC = ROOT.TH2D("BG_AUC", "AUC;Trained mass;Test mass", len(mass_bin), 0, len(mass_bin), len(mass_bin),0, len(mass_bin))
  CG_BH_AUC = ROOT.TH2D("CG_AUC", "AUC;Trained mass;Test mass", len(mass_bin), 0, len(mass_bin), len(mass_bin),0, len(mass_bin))

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
  c.SaveAs("BG_AUC.png")
  CG_BH_AUC.Draw("COLZ TEXT")
  c.SaveAs("CG_AUC.png")


if __name__ == "__main__":
  usage = 'usage: %prog [options]'
  parser =  argparse.ArgumentParser(description=usage)
  parser.add_argument('--indir', type = str)
  args = parser.parse_args()
  plot_mass_dependence(args.indir)
