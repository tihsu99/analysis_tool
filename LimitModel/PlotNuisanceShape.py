import ROOT
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import json
import argparse
sys.path.append('../python')
from common import *
from plotstyle import *
import numpy as np
from termcolor import cprint
def CheckDir(path):
  if not os.path.exists(path):
    os.system('mkdir -p {}'.format(path))

if __name__ == '__main__':

  parser = argparse.ArgumentParser()

  parser.add_argument('--era', default = '2017', type = str)
  parser.add_argument('--region', type = str)
  parser.add_argument('--channel', type = str)
  parser.add_argument('--data_info_dir', default = './data_info', type = str)
  parser.add_argument('--input_dir',     default = './',          type = str)
  parser.add_argument('--mass_point',    default = "500",         type = str)
  parser.add_argument('--rtt',           default = "0.6",         type = str)
  parser.add_argument('--rtc',           default = "0.4",         type = str) 
  parser.add_argument('--process',       default = None)
  parser.add_argument('--process_blacklist',       default = None)
  parser.add_argument("--logy",          action  = "store_true")
  parser.add_argument("--unblind", action = "store_true")
  parser.add_argument("--background", default = None)
  args = parser.parse_args()

  rtc = args.rtc.replace('.', '')
  rtt = args.rtt.replace('.', '')
  mass = args.mass_point
  signal_name = 'CGToBHpm_a_{mass}_rtt{rtt}_rtc{rtc}'.format(mass = mass, rtt = rtt, rtc = rtc)
  channel = args.channel
  region  = args.region
  era     = args.era
  year    = '2016' if '2016' in era else era
  unblind_string = "unblind" if args.unblind else "blind"
  outdir  = os.path.join(args.input_dir, 'Nuisance_Variation_Plot', signal_name, era, region, channel, unblind_string)
  CheckDir(outdir)

  data_info_file = os.path.join(args.data_info_dir, "Datacard_Input", args.era, "Datacard_Input_{region}_{channel}.json".format(region=args.region, channel=args.channel))
  distribution_file = os.path.join(args.input_dir, 'FinalInputs', era, signal_name, "TMVApp_{region}_{channel}.root".format(region = region, channel = channel))

  cprint('data_info file: {}'.format(data_info_file), 'green')
  cprint('root file: {}'.format(distribution_file), 'green')

  data_info = read_json(data_info_file)

  fin = ROOT.TFile.Open(distribution_file, 'READ')

  DrawNominal = False

  # Nominal Plot

  for nuisance in data_info["UnclnN"]:
    if not(data_info["UnclnN"][nuisance] == 'shape'): continue

    canvas = DataMCCanvas(" ", " ", Lumi[era])
    canvas.legend.setPosition(0.35, 0.77, 0.8, 0.9)
    canvas.raxis.SetNdivisions(101)
    #canvas.SetLogy()
    canvas.rlimits = (0.8, 1.2)
    canvas.legend.SetTextSize(0.018)
    canvas.legend.SetX2(0.95)
    canvas.ytitle = "Events/bin"

    nuisance_name = nuisance.replace('YEAR', year).replace('ERA', era).replace('CHANNEL', channel).replace('REGION', region)

    # Nominal process
    for process_ in data_info["Process"]:

      if args.background is not None and not (process_ == args.background): continue
      if process_ == "SIGNAL": continue
      if (args.process_blacklist is not None) and (process_ == args.process_blacklist): continue
      histo = fin.Get("bH{era}_{process}".format(era = era, process = process_)).Clone()
      print("bH{era}_{process}".format(era = era, process = process_), histo.GetBinLowEdge(3), histo.GetBinLowEdge(4),  histo.GetBinLowEdge(1),  histo.GetBinLowEdge(2))
      canvas.addStacked(histo, title = "%s[%.0f]"%(process_, histo.Integral()), color = Color_Dict_ref[process_], opt = 'F')
    if args.unblind:
      histo = fin.Get("bH{era}_data_obs".format(era=era))
      canvas.addObs(histo, title = "data")
    # Get variation
    h_up = None
    h_down = None
    for process_ in data_info["Process"]:
      if (args.process_blacklist is not None) and (process_ == args.process_blacklist): continue
      if args.background is not None and not (process_ == args.background): continue
      if process_ == "SIGNAL": continue
      if process_ in data_info["NuisForProc"][nuisance] and not (args.process is not None and not process_ == args.process):
        h_up_tmp = fin.Get("bH{era}_{process}_{nui}Up".format(era=era, process=process_,nui=nuisance_name)).Clone()
        h_do_tmp = fin.Get("bH{era}_{process}_{nui}Down".format(era=era, process=process_,nui=nuisance_name)).Clone()
      else:
        h_up_tmp = fin.Get("bH{era}_{process}".format(era=era, process=process_))
        h_do_tmp = fin.Get("bH{era}_{process}".format(era=era, process=process_))
      if h_up is None:
        h_up = h_up_tmp.Clone()
        h_do = h_do_tmp.Clone()
      else:
        h_up.Add(h_up_tmp)
        h_do.Add(h_do_tmp)

    canvas.rtitle = str("Data/Pred.")
    canvas.yaxis.SetMaxDigits(4)

    print("bH{era}_{process}".format(era=era, process=signal_name))
    signal_histo = fin.Get("bH{era}_{process}_2b".format(era=era, process=signal_name)).Clone()
    signal_histo_3b = fin.Get("bH{era}_{process}_3b".format(era=era, process=signal_name)).Clone()
    signal_histo.Add(signal_histo_3b)
    signal_histo.Scale(10)

    if "SIGNAL" in data_info["NuisForProc"][nuisance]:
      h_up_tmp = fin.Get("bH{era}_{process}_2b_{nui}Up".format(era=era, process   = signal_name, nui=nuisance_name)).Clone()
      h_do_tmp = fin.Get("bH{era}_{process}_2b_{nui}Down".format(era=era, process = signal_name, nui=nuisance_name)).Clone()
      h_up_tmp.Add(fin.Get("bH{era}_{process}_3b_{nui}Up".format(era=era, process   = signal_name, nui=nuisance_name)).Clone())
      h_do_tmp.Add(fin.Get("bH{era}_{process}_3b_{nui}Down".format(era=era, process = signal_name, nui=nuisance_name)).Clone())

      h_up_tmp.Scale(10)
      h_do_tmp.Scale(10)
      canvas.addSignal(h_up_tmp, title = "Sig_up", color=ROOT.kGreen+1, lwidth = 1) 
      canvas.addSignal(h_do_tmp, title = "Sig_down", color=ROOT.kGreen-1, lwidth = 1) 

    canvas.addSignal(signal_histo, title = f"Sig [{mass}GeV]", color=ROOT.kBlue, lwidth = 4) 
    canvas.addText('Region: {}'.format(region), 0.18, 0.79, 0.3, 0.82, size=0.02, align=12)
    canvas.addText('Channel: {}'.format(channel), 0.18, 0.76, 0.3, 0.79, size=0.02, align=12)


    icolor = [ROOT.kRed-6, ROOT.kMagenta-3, ROOT.kGreen-6, ROOT.kBlue - 7]
    for imass, mass_ in enumerate([300, 500, 800, 1000]):
        if int(mass_) == int(mass): continue
        other_signal_name = 'CGToBHpm_a_{mass}_rtt{rtt}_rtc{rtc}'.format(mass = mass_, rtt = rtt, rtc = rtc)
        other_signal_histo = fin.Get("bH{era}_{process}_2b".format(era=era, process=other_signal_name)).Clone()
        other_signal_histo_3b = fin.Get("bH{era}_{process}_3b".format(era=era, process=other_signal_name)).Clone()
        other_signal_histo.Add(other_signal_histo_3b)
        other_signal_histo.Scale(10)
        canvas.addSignal(other_signal_histo, title = f"Sig [{mass_}GeV]", color = icolor[imass], lwidth = 3, lstyle = 9)

    if not DrawNominal:
      canvas.applyStyles()
      if args.logy:
        canvas.printWeb(os.path.join(outdir), "PreFit_log", logy = True)
      else:
        canvas.printWeb(os.path.join(outdir), "PreFit", logy = args.logy)

    canvas.addSignal(h_up, title = "VarUp[%.0f]"%(h_up.Integral()), color = ROOT.kRed)
    canvas.addSignal(h_do, title = "VarDown[%.0f]"%(h_do.Integral()), color = ROOT.kOrange)
    canvas.addText('Var: {}'.format(nuisance_name), 0.18, 0.73, 0.3, 0.76, size=0.019, align=12)
    canvas.applyStyles()
    if args.logy:
      canvas.printWeb(os.path.join(outdir), "{nuisance}_log".format(nuisance = nuisance_name), logy = True)
    else:
      canvas.printWeb(os.path.join(outdir), "{nuisance}".format(nuisance = nuisance_name), logy = args.logy)



  fin.Close()

