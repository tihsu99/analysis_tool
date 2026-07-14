import ROOT
import os, sys, glob, fnmatch, math, re
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


def split_csv_patterns(x, default='*'):
  if x is None:
    x = default
  return [i.strip() for i in str(x).split(',') if i.strip()]


def match_any(name, patterns):
  return any(fnmatch.fnmatch(name, p) for p in patterns)


def natural_key(text):
  return [int(c) if c.isdigit() else c.lower() for c in re.split(r'([0-9]+)', text)]


def clone_hist(h, new_name=None):
  if h is None:
    return None
  if new_name is None:
    new_name = h.GetName() + '_' + str(ROOT.TUUID().AsString())
  hout = h.Clone(new_name)
  hout.SetDirectory(0)
  return hout


def get_hist(fin, name, allow_missing=False):
  h = fin.Get(name)
  if not h:
    if allow_missing:
      return None
    raise RuntimeError(f'Missing histogram: {name} in file {fin.GetName()}')
  return clone_hist(h)


def integral_with_flow(h):
  if h is None:
    return 0.
  return h.Integral(0, h.GetNbinsX()+1)


def integral_error_with_flow(h):
  if h is None:
    return 0.
  err2 = 0.
  for ibin in range(0, h.GetNbinsX()+2):
    err = h.GetBinError(ibin)
    err2 += err * err
  return math.sqrt(err2)


def make_region_hist(name, regions):
  h = ROOT.TH1F(name, "", len(regions), 0.5, len(regions)+0.5)
  h.Sumw2()
  for ibin, reg in enumerate(regions, start=1):
    h.GetXaxis().SetBinLabel(ibin, reg)
  h.GetXaxis().LabelsOption("v")
  return h


def make_ratio_line(h, name, color, lstyle=ROOT.kSolid, lwidth=4):
  ratio = clone_hist(h, name)
  ratio.SetLineColor(color)
  ratio.SetLineStyle(lstyle)
  ratio.SetLineWidth(lwidth)
  ratio.SetFillStyle(0)
  ratio.SetMarkerSize(0)
  return ratio


def discover_regions(data_info_dir, era, channel, region_patterns):
  pattern = os.path.join(
    data_info_dir,
    "Datacard_Input",
    era,
    f"Datacard_Input_*_{channel}.json"
  )
  prefix = "Datacard_Input_"
  suffix = f"_{channel}.json"

  regions = []
  for f in glob.glob(pattern):
    base = os.path.basename(f)
    if not (base.startswith(prefix) and base.endswith(suffix)):
      continue
    reg = base[len(prefix):-len(suffix)]
    if match_any(reg, region_patterns):
      regions.append(reg)
  return sorted(list(set(regions)), key=natural_key)


if __name__ == '__main__':

  parser = argparse.ArgumentParser()

  parser.add_argument('--era', default='2017', type=str)
  parser.add_argument('--region', default='*', type=str,
                      help='Wildcard region selection, comma separated')
  parser.add_argument('--channel', type=str, required=True)
  parser.add_argument('--data_info_dir', default='./data_info', type=str)
  parser.add_argument('--input_dir', default='./', type=str)
  parser.add_argument('--output_dir', default=None, type=str)

  parser.add_argument('--mass_point', default="500", type=str)
  parser.add_argument('--rtt', default="0.6", type=str)
  parser.add_argument('--rtc', default="0.4", type=str)

  parser.add_argument('--process', default=None,
                      help='Only vary these processes (wildcard/comma separated)')
  parser.add_argument('--process_blacklist', default=None,
                      help='Processes to exclude from drawing (wildcard/comma separated)')
  parser.add_argument('--background', default=None,
                      help='Only draw these backgrounds (wildcard/comma separated)')
  parser.add_argument('--nuisance', default='*', type=str,
                      help='Wildcard nuisance selection, comma separated')

  parser.add_argument("--logy", action="store_true")
  parser.add_argument("--unblind", action="store_true")
  args = parser.parse_args()

  rtc = args.rtc.replace('.', '')
  rtt = args.rtt.replace('.', '')
  mass = args.mass_point
  signal_name = 'CGToBHpm_a_{mass}_rtt{rtt}_rtc{rtc}'.format(mass=mass, rtt=rtt, rtc=rtc)

  era = args.era
  year = '2016' if '2016' in era else era
  channel = args.channel

  region_patterns = split_csv_patterns(args.region, default='*')
  nuisance_patterns = split_csv_patterns(args.nuisance, default='*')
  process_patterns = split_csv_patterns(args.process) if args.process else None
  process_blacklist_patterns = split_csv_patterns(args.process_blacklist) if args.process_blacklist else []
  background_patterns = split_csv_patterns(args.background) if args.background else None

  regions = discover_regions(args.data_info_dir, era, channel, region_patterns)
  if len(regions) == 0:
    raise RuntimeError(f'No regions found for era={era}, channel={channel}, region={args.region}')

  cprint(f"Selected regions: {regions}", "green")

  unblind_string = "unblind" if args.unblind else "blind"
  if args.output_dir is not None:
    outdir = args.output_dir
  else:
    outdir = os.path.join(args.input_dir, 'Nuisance_Variation_Plot', signal_name, era, "AllRegions", channel, unblind_string)
  CheckDir(outdir)

  # Read all region data_info first
  data_info_map = {}
  process_union = []
  nuisance_union = []

  for region in regions:
    data_info_file = os.path.join(
      args.data_info_dir,
      "Datacard_Input",
      era,
      "Datacard_Input_{region}_{channel}.json".format(region=region, channel=channel)
    )
    cprint('data_info file: {}'.format(data_info_file), 'green')
    data_info = read_json(data_info_file)
    data_info_map[region] = data_info

    for process_ in data_info["Process"]:
      if process_ == "SIGNAL":
        continue
      if background_patterns is not None and not match_any(process_, background_patterns):
        continue
      if len(process_blacklist_patterns) > 0 and match_any(process_, process_blacklist_patterns):
        continue
      if process_ not in process_union:
        process_union.append(process_)


    norm_factor_for_var = {}
    for nuisance in data_info["UnclnN"]:
      if not match_any(nuisance, nuisance_patterns):
        continue
      if not (data_info["UnclnN"][nuisance] == 'shape'):
        norm_factor_for_var[nuisance] = data_info["UnclnN"][nuisance]
      if nuisance not in nuisance_union:
        nuisance_union.append(nuisance)

  if len(process_union) == 0:
    raise RuntimeError("No processes selected after filtering.")
  if len(nuisance_union) == 0:
    cprint("Warning: no nuisances matched the wildcard selection", "yellow")

  cprint(f"Selected backgrounds: {process_union}", "green")
  cprint(f"Matched nuisances: {nuisance_union}", "green")

  # One-bin-per-region histograms
  h_bkg_map = {}
  for process_ in process_union:
    h_bkg_map[process_] = make_region_hist(f"h_{process_}", regions)

  h_data = make_region_hist("h_data", regions)
  h_up   = make_region_hist("h_up", regions)
  h_do   = make_region_hist("h_do", regions)
  h_nom  = make_region_hist("h_nom", regions)

  h_signal = make_region_hist(f"h_sig_{mass}", regions)

  other_signal_hists = {}
  other_signal_masses = [300, 500, 800, 1000]
  for mass_ in other_signal_masses:
    if int(mass_) == int(mass):
      continue
    other_signal_hists[mass_] = make_region_hist(f"h_sig_{mass_}", regions)

  # Loop regions and fill one bin each
  for ibin, region in enumerate(regions, start=1):

    distribution_file = os.path.join(
      args.input_dir,
      'FinalInputs',
      era,
      signal_name,
      "TMVApp_{region}_{channel}.root".format(region=region, channel=channel)
    )
    cprint('root file: {}'.format(distribution_file), 'green')

    fin = ROOT.TFile.Open(distribution_file, 'READ')
    if not fin or fin.IsZombie():
      raise RuntimeError(f"Cannot open ROOT file {distribution_file}")

    data_info = data_info_map[region]

    nominal_total = 0.
    nominal_error2 = 0.
    nominal_proc_yields = {}

    # fill nominal background stacks
    for process_ in process_union:
      htmp = get_hist(fin, "bH{era}_{process}".format(era=era, process=process_), allow_missing=True)
      y = integral_with_flow(htmp)
      yerr = integral_error_with_flow(htmp)
      nominal_proc_yields[process_] = y
      nominal_total += y
      nominal_error2 += yerr * yerr

      h_bkg_map[process_].SetBinContent(ibin, y)
      h_bkg_map[process_].SetBinError(ibin, yerr)

    h_nom.SetBinContent(ibin, nominal_total)
    h_nom.SetBinError(ibin, math.sqrt(nominal_error2))

    # data
    if args.unblind:
      hobs = get_hist(fin, "bH{era}_data_obs".format(era=era), allow_missing=True)
      yobs = integral_with_flow(hobs)
      h_data.SetBinContent(ibin, yobs)
      h_data.SetBinError(ibin, math.sqrt(yobs) if yobs > 0 else 0.)

    # signal
    hsig2b = get_hist(fin, "bH{era}_{process}_2b".format(era=era, process=signal_name), allow_missing=True)
    hsig3b = get_hist(fin, "bH{era}_{process}_3b".format(era=era, process=signal_name), allow_missing=True)
    ysig = integral_with_flow(hsig2b) + integral_with_flow(hsig3b)
    h_signal.SetBinContent(ibin, 10. * ysig)
    h_signal.SetBinError(ibin, 0.)

    for mass_ in other_signal_hists:
      other_signal_name = 'CGToBHpm_a_{mass}_rtt{rtt}_rtc{rtc}'.format(mass=mass_, rtt=rtt, rtc=rtc)
      ho2b = get_hist(fin, "bH{era}_{process}_2b".format(era=era, process=other_signal_name), allow_missing=True)
      ho3b = get_hist(fin, "bH{era}_{process}_3b".format(era=era, process=other_signal_name), allow_missing=True)
      yother = integral_with_flow(ho2b) + integral_with_flow(ho3b)
      other_signal_hists[mass_].SetBinContent(ibin, 10. * yother)
      other_signal_hists[mass_].SetBinError(ibin, 0.)

    # combine nuisance variations in quadrature
    sum_up2 = 0.
    sum_do2 = 0.

    region_nuisances = []
    for nuisance in data_info["UnclnN"]:
#      if not (data_info["UnclnN"][nuisance] == 'shape'):
#        continue
      if not match_any(nuisance, nuisance_patterns):
        continue
      region_nuisances.append(nuisance)

    for nuisance in region_nuisances:

      nuisance_name = nuisance.replace('YEAR', year).replace('ERA', era).replace('CHANNEL', channel).replace('REGION', region)

      total_up = 0.
      total_do = 0.

      for process_ in process_union:

        nominal_yield = nominal_proc_yields[process_]
        vary_this_process = False

        if nuisance in data_info["NuisForProc"]:
          if process_ in data_info["NuisForProc"][nuisance]:
            vary_this_process = True

        if process_patterns is not None:
          vary_this_process = vary_this_process and match_any(process_, process_patterns)

        if vary_this_process:

          if nuisance in norm_factor_for_var:
            scale = float(norm_factor_for_var[nuisance]) - 1.0
            print(scale)
            yup = nominal_yield * (1. + scale)
            ydo = nominal_yield * (1. - scale)
          else:
            hup_tmp = get_hist(fin, "bH{era}_{process}_{nui}Up".format(
              era=era, process=process_, nui=nuisance_name
            ), allow_missing=True)
            hdo_tmp = get_hist(fin, "bH{era}_{process}_{nui}Down".format(
              era=era, process=process_, nui=nuisance_name
            ), allow_missing=True)

            yup = integral_with_flow(hup_tmp) if hup_tmp else nominal_yield
            ydo = integral_with_flow(hdo_tmp) if hdo_tmp else nominal_yield
        else:
          yup = nominal_yield
          ydo = nominal_yield

        total_up += yup
        total_do += ydo

      # compare to nominal and combine in quadrature
      diff_up = total_up - nominal_total
      diff_do = total_do - nominal_total

      above = max(diff_up, diff_do, 0.)
      below = max(-diff_up, -diff_do, 0.)

      sum_up2 += above * above
      sum_do2 += below * below

    total_sigma_up = math.sqrt(sum_up2)
    total_sigma_do = math.sqrt(sum_do2)

    total_up_combined = nominal_total + total_sigma_up
    total_do_combined = max(0., nominal_total - total_sigma_do)

    h_up.SetBinContent(ibin, total_up_combined)
    h_up.SetBinError(ibin, 0.)

    h_do.SetBinContent(ibin, total_do_combined)
    h_do.SetBinError(ibin, 0.)

    fin.Close()

  # draw
  canvas = DataMCCanvas(" ", " ", Lumi[era])
  canvas.legend.setPosition(0.35, 0.72, 0.92, 0.90)
  canvas.raxis.SetNdivisions(101)
  canvas.rlimits = (0.8, 1.2)
  canvas.legend.SetTextSize(0.018)
  canvas.legend.SetX2(0.95)
  canvas.ytitle = "Events/region"
  canvas.rtitle = "Ratio"
  canvas.yaxis.SetMaxDigits(4)

  for process_ in process_union:
    color = Color_Dict_ref[process_] if process_ in Color_Dict_ref else ROOT.kGray+1
    canvas.addStacked(
      h_bkg_map[process_],
      title="%s[%.0f]" % (process_, h_bkg_map[process_].Integral()),
      color=color,
      opt='F'
    )

  if args.unblind:
    canvas.addObs(h_data, title="data")

  #canvas.addSignal(h_signal, title=f"Sig [{mass}GeV]", color=ROOT.kBlue, lwidth=4)

  icolor = [ROOT.kRed-6, ROOT.kMagenta-3, ROOT.kGreen-6, ROOT.kBlue-7]
  idx = 0
#  for mass_ in sorted(other_signal_hists.keys()):
#    canvas.addSignal(
#      other_signal_hists[mass_],
#      title=f"Sig [{mass_}GeV]",
#      color=icolor[idx % len(icolor)],
#      lwidth=3,
#      lstyle=9
#    )
#    idx += 1

  canvas.addSignal(h_up, title="VarUp[%.0f]" % (h_up.Integral()), color=ROOT.kRed)
  canvas.addSignal(h_do, title="VarDown[%.0f]" % (h_do.Integral()), color=ROOT.kOrange)
  canvas.addExtraRatio(make_ratio_line(h_up, "h_up_ratio", ROOT.kRed), drawOpt="HIST")
  canvas.addExtraRatio(make_ratio_line(h_do, "h_do_ratio", ROOT.kOrange), drawOpt="HIST")

  canvas.addText('Channel: {}'.format(channel), 0.18, 0.82, 0.35, 0.85, size=0.02, align=12)
  canvas.addText('Regions: {}'.format(','.join(regions[:4]) + ('...' if len(regions) > 4 else '')), 0.18, 0.79, 0.60, 0.82, size=0.02, align=12)
  canvas.addText('Nuisance: {}'.format(args.nuisance), 0.18, 0.76, 0.60, 0.79, size=0.019, align=12)

  canvas.applyStyles()

  tag = re.sub(r'[^A-Za-z0-9_*.-]+', '_', args.nuisance.replace(',', '__'))
  if args.logy:
    canvas.printWeb(os.path.join(outdir), f"RegionSummary_{tag}_log", logy=True)
  else:
    canvas.printWeb(os.path.join(outdir), f"RegionSummary_{tag}", logy=False)

