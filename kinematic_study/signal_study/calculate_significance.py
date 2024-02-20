import os 
import sys
import optparse, argparse
import json
import ROOT
from collections import OrderedDict
sys.path.insert(1, '../../python')
from common import *
import re
ROOT.gStyle.SetOptStat(00000000)
import math

def func_asymptotic_significance(h_sig, h_bkg, bins):

  significance = 0.0
  for bin_ in bins:
    binx = bin_[0]
    biny = bin_[1]
    n_sig = h_sig.GetBinContent(binx, biny)
    n_bkg = h_bkg.GetBinContent(binx, biny)
    significance += -2.0 * (n_sig + (n_sig+n_bkg)*math.log(n_bkg/(n_sig+n_bkg)))
  return significance
def calculate_significance(bkg_list, sig_list, indir, plotdir, postfix):


  for lepton_ in ['ele', 'mu']:
    for btag_wp_ in ['loose', 'medium', 'tight']:
      h_bkg = None
      h_sig = None
      for sig_file_ in sig_list:
        f_sig = ROOT.TFile.Open(os.path.join(indir, sig_file_), "READ")
        if h_sig is None:
          h_sig = f_sig.Get("{}_btag_{}".format(lepton_, btag_wp_)).Clone()
          print(sig_file_, indir)
          h_sig.SetDirectory(0)
        else:
          h_sig.Add(f_sig.Get("{}_btag_{}".format(lepton_, btag_wp_)).Clone())
      for bkg_file_ in bkg_list:
        f_bkg = ROOT.TFile.Open(os.path.join(indir, bkg_file_), "READ")
        if h_bkg is None:
          h_bkg = f_bkg.Get("{}_btag_{}".format(lepton_, btag_wp_)).Clone()
          h_bkg.SetDirectory(0)
        else:
          h_bkg.Add(f_bkg.Get("{}_btag_{}".format(lepton_, btag_wp_)).Clone())

#      h_sig = overunder_flowbin2D(h_sig)
#      h_bkg = overunder_flowbin2D(h_bkg)
      h_bkg_sqrt = h_bkg.Clone()
#      h_significance = h_sig.Clone()
      for idx_x in range(h_bkg.GetNbinsX()):
        for idx_y in range(h_bkg.GetNbinsY()):
 #         print("s/sqrt(b):", h_sig.GetBinContent(idx_x+1, idx_y+1) / (h_bkg.GetBinContent(idx_x+1, idx_y+1))**0.5)
  #        print("asymptotic:", func_asymptotic_significance(h_sig, h_bkg, [[idx_x+1, idx_y+1]]))
          h_bkg_sqrt.SetBinContent(idx_x + 1, idx_y + 1, (h_bkg.GetBinContent(idx_x + 1, idx_y + 1))**0.5)

      h_significance = h_sig.Clone()
      h_significance.Divide(h_bkg_sqrt)
      c = ROOT.TCanvas()
      h_significance.Draw("COLZ TEXT")
      c.SaveAs(os.path.join(plotdir, "significance_{}_btag_{}_{}.png".format(lepton_, btag_wp_, postfix)))
      c.SaveAs(os.path.join(plotdir, "significance_{}_btag_{}_{}.pdf".format(lepton_, btag_wp_, postfix)))
      h_sig.Draw("COLZ TEXT")
      c.SaveAs(os.path.join(plotdir, "signal_{}_btag_{}_{}.png".format(lepton_, btag_wp_, postfix)))
      c.SaveAs(os.path.join(plotdir, "signal_{}_btag_{}_{}.pdf".format(lepton_, btag_wp_, postfix)))
      h_bkg.Draw("COLZ TEXT")
      c.SaveAs(os.path.join(plotdir, "background_{}_btag_{}_{}.png".format(lepton_, btag_wp_, postfix)))
      c.SaveAs(os.path.join(plotdir, "background_{}_btag_{}_{}.pdf".format(lepton_, btag_wp_, postfix)))

if __name__ == '__main__':

  usage = 'usage: %prog[options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('--era', type=str, default='2017')
  parser.add_argument('--indir', type=str, default='./')
  parser.add_argument('--plotdir', type=str, default='plot')
  args = parser.parse_args()
  args_dict = vars(args)

  if not os.path.exists(args.plotdir):
    os.system('mkdir -p {}'.format(args.plotdir))

  samples = read_json('../../data/sample.json')
  bkg_list = []

  for file_ in os.listdir(inputFile_path[args.era]):
    fin_raw = file_.replace('.root', '')


if __name__ == '__main__':

  usage = 'usage: %prog[options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('--era', type=str, default='2017')
  parser.add_argument('--indir', type=str, default='./')
  parser.add_argument('--plotdir', type=str, default='plot')
  args = parser.parse_args()
  args_dict = vars(args)

  if not os.path.exists(args.plotdir):
    os.system('mkdir -p {}'.format(args.plotdir))

  samples = read_json('../../data/sample.json')
  bkg_list = []

  for file_ in os.listdir(inputFile_path[args.era]):
    fin_raw = file_.replace('.root', '')

if __name__ == '__main__':

  usage = 'usage: %prog[options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('--era', type=str, default='2017')
  parser.add_argument('--indir', type=str, default='./')
  parser.add_argument('--plotdir', type=str, default='plot')
  args = parser.parse_args()
  args_dict = vars(args)

  if not os.path.exists(args.plotdir):
    os.system('mkdir -p {}'.format(args.plotdir))

  samples = read_json('../../data/sample.json')
  bkg_list = []

  for file_ in os.listdir(inputFile_path[args.era]):
    fin_raw = file_.replace('.root', '')
    if 'CGToBH' not in fin_raw and 'BGToTH' not in fin_raw:
      sample_name = re.sub(r'_[0-9]]+', '', fin_raw)
    else: sample_name = fin_raw
    if sample_name not in samples: continue
    if 'Data' in samples[sample_name]['Label']: continue
    if 'Background' in samples[sample_name]['Label']: bkg_list.append(file_)

  for mass_ in [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]:
    sig_list = ['CGToBHpm_a_{}_rtt06_rtc04.root'.format(mass_)] #, 'BGToTHpm_a_{}_rtt06_rtc04.root'.format(mass_)]
    for ele_pt in [32, 35]:
      for mu_pt in [27,30]:
        calculate_significance(bkg_list, sig_list, os.path.join(args.indir, 'ele_{}_mu_{}'.format(ele_pt, mu_pt)), args.plotdir, 'm{}_ele{}_mu{}'.format(str(mass_), ele_pt, mu_pt))
    

