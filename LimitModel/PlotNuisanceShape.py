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
  parser.add_argument("--logy",          action  = "store_true")
  args = parser.parse_args()

  rtc = args.rtc.replace('.', '')
  rtt = args.rtt.replace('.', '')
  mass = args.mass_point
  signal_name = 'CGToBHpm_a_{mass}_rtt{rtt}_rtc{rtc}'.format(mass = mass, rtt = rtt, rtc = rtc)
  channel = args.channel
  region  = args.region
  era     = args.era
  year    = '2016' if '2016' in era else era
  outdir  = os.path.join(args.input_dir, 'Nuisance_Variation_Plot', signal_name, era, region, channel)
  CheckDir(outdir)

  data_info_file = os.path.join(args.data_info_dir, "Datacard_Input", args.era, "Datacard_Input_{region}_{channel}.json".format(region=args.region, channel=args.channel))
  distribution_file = os.path.join(args.input_dir, 'FinalInputs', era, signal_name, "TMVApp_{region}_{channel}.root".format(region = region, channel = channel))

  cprint('data_info file: {}'.format(data_info_file), 'green')
  cprint('root file: {}'.format(distribution_file), 'green')

  data_info = read_json(data_info_file)

  fin = ROOT.TFile.Open(distribution_file, 'READ')



  # Nominal Plot
  for nuisance in data_info["UnclnN"]:
    if not(data_info["UnclnN"][nuisance] == 'shape'): continue

    canvas = DataMCCanvas(" ", " ", Lumi[era])
    canvas.legend.setPosition(0.35, 0.77, 0.8, 0.9)
    canvas.raxis.SetNdivisions(101)
    #canvas.SetLogy()
    canvas.rlimits = (0.9, 1.1)
    canvas.legend.SetTextSize(0.015)
    canvas.legend.SetX2(0.95)
    canvas.ytitle = "Events/bin"

    nuisance_name = nuisance.replace('YEAR', year).replace('ERA', era).replace('CHANNEL', channel)

    # Nominal process
    for process_ in data_info["Process"]:
      if process_ == "SIGNAL": continue
      histo = fin.Get("bH{era}_{process}".format(era = era, process = process_)).Clone()
      canvas.addStacked(histo, title = "%s[%.0f]"%(process_, histo.Integral()), color = Color_Dict_ref[process_], opt = 'F')

    # Get variation
    h_up = None
    h_down = None
    for process_ in data_info["Process"]:
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
    
    canvas.addSignal(h_up, title = "%s[%.0f]"%(nuisance_name, h_up.Integral()), color = ROOT.kRed)
    canvas.addSignal(h_do, title = "%s[%.0f]"%(nuisance_name, h_do.Integral()), color = ROOT.kOrange)
    canvas.rtitle = str("variation")
    canvas.yaxis.SetMaxDigits(4)

    canvas.applyStyles()
    if args.logy:
      canvas.printWeb(os.path.join(outdir), "{nuisance}_log".format(nuisance = nuisance_name), logy = True)
    else:
      canvas.printWeb(os.path.join(outdir), "{nuisance}".format(nuisance = nuisance_name), logy = args.logy)



  fin.Close()

