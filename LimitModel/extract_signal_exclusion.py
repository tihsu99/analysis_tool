import ROOT
import os, sys
import optparse, argparse
from array import array
import pandas as pd
sys.path.append('../python')
from common import *
from scipy.interpolate import griddata
import numpy as np
import cmsstyle as CMS


CMS.SetExtraText("Preliminary")
CMS.SetEnergy("13")


############################
##  Basic Initialization  ##
############################

df_sig_xsec = pd.read_csv(
    "../data/formatted_matrix_element_level_cross_sections_with_small_rho_steps.txt",
    delim_whitespace=True,
    skiprows=2,
)

df_sig_xsec.columns = ["Mass", "rtt", "rtc", "xsec"]

df_match = pd.read_csv(
    "../data/average_matching_efficiency.txt",
    delim_whitespace = True,
    skiprows = 2
)

df_match.columns = ["Mass", "matching_eff"]

df_merged = df_sig_xsec.merge(df_match, on="Mass", how="left")
df_merged["xsec"] *= df_merged["matching_eff"] / 100.0

df_sig_xsec = df_merged.drop(columns=["matching_eff"])

column_names = [
    "Mass", "rtt", "rtc",
    "scale_unc_+", "scale_unc_-", "scale_unc_avg",
    "PDF_unc_(%)", "total_unc"
]
# Read the file while handling whitespace and missing columns
df_sig_xsec_err = pd.read_csv(
    "../data/signal_xsec_unc.txt",
    delim_whitespace=True,  # Handle white-space delimited data
    skiprows=1,             # Skip the comment row (starts with #)
    names=column_names,     # Use predefined column names
    engine="python",        # Use Python engine for complex parsing
    na_values=["..."]       # Handle potential missing values
)

df_combined = pd.merge(df_sig_xsec, df_sig_xsec_err, on = ["Mass", "rtt", "rtc"], how = "inner")
print(df_combined)

ratio = read_json("ratio.json")

def get_2DNLL(fin_name, xsec_2b = 1.0, xsec_3b = 1.0, input_x = [], input_y = [], options = dict()):
    fin = ROOT.TFile.Open(fin_name, "READ")
    t = fin.Get("limit")

    input_x = np.array(input_x)
    input_y = np.array(input_y)

    # Number of points in interpolation
    n_points = 200
    x_range = [0, xsec_2b]
    y_range = [0, xsec_3b]

    n_bins = 40

    x_array, y_array, deltaNLL = [], [], []
    for ev in t:
        x_array.append(getattr(ev, "r_2b") * xsec_2b)
        y_array.append(getattr(ev, "r_3b") * xsec_3b)
        deltaNLL.append(getattr(ev, "deltaNLL") * 2)

    n_points = 200
    points = np.array([x_array, y_array]).transpose()
    dnll = np.asarray(deltaNLL)
    # Set up grid
    grid_x, grid_y = np.mgrid[min(x_array) : max(x_array) : n_points * 1j, min(y_array) : max(y_array) : n_points * 1j]
    grid_vals = griddata(points, dnll, (grid_x, grid_y), options["strategy"])

    # Remove NANS
    grid_x = grid_x[grid_vals == grid_vals]
    grid_y = grid_y[grid_vals == grid_vals]
    grid_vals = grid_vals[grid_vals == grid_vals]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    points_iter = np.array([grid_x, grid_y]).transpose()
    grid_vals_iter = griddata(points_iter, grid_vals, (input_x, input_y), "nearest")

    return grid_vals_iter


def draw_contour2D(input_x, input_y, input_z, target_values, n_points = 200, config = dict(), cond = 500, options = dict(), param = ''):


#    ROOT.gStyle.Reset()
    ROOT.gStyle.SetTitleBorderSize(0)
    ROOT.gStyle.SetTitleAlign(23)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gROOT.SetBatch(1)
    #ROOT.gStyle.SetCanvasColor(0)
    ROOT.gStyle.SetPalette(ROOT.kLightTemperature)
#    ROOT.TColor.InvertPalette();
    c = ROOT.TCanvas("c","c",700, 600)
    c.SetTopMargin(0.085)
    c.SetRightMargin(0.14)
    c.SetLeftMargin(0.14)
    c.SetLogz(1)
    c.SetGrid(0,0)
    c.SetTicks(1,1)


    input_x = np.array(input_x)
    input_y = np.array(input_y)
    pred = np.array(input_z)


    

    points = np.array([input_x, input_y]).transpose()
    # Set up grid
    grid_x, grid_y = np.mgrid[min(input_x) : max(input_x) : n_points * 1j, min(input_y) : max(input_y) : n_points * 1j]
    grid_vals = griddata(points, pred, (grid_x, grid_y), options["strategy"])
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Remove NANS
    grid_x = grid_x[grid_vals == grid_vals]
    grid_y = grid_y[grid_vals == grid_vals]
    grid_vals = grid_vals[grid_vals == grid_vals]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    n_bins = 40
    # Define Profile2D histogram
    h2D = ROOT.TProfile2D("h", "h", n_bins, min(input_x),  max(input_x), n_bins, min(input_y), max(input_y))
    #h2D = ROOT.TH2D("h_converted", "h_converted", n_bins, min(input_x), max(input_x), n_bins, min(input_y), max(input_y))
    h2D.SetDirectory(0)

    for i in range(len(grid_vals)):
        # Factor of 2 comes from 2*NLL
        h2D.Fill(grid_x[i], grid_y[i], 2 * grid_vals[i])

    # Loop over bins: if content = 0 then set 999
    for ibin in range(1, h2D.GetNbinsX() + 1):
        for jbin in range(1, h2D.GetNbinsY() + 1):
            if h2D.GetBinContent(ibin, jbin) == 0:
                xc = h2D.GetXaxis().GetBinCenter(ibin)
                yc = h2D.GetYaxis().GetBinCenter(jbin)
                h2D.Fill(xc, yc, 999)
    h2D.SetContour(999)
    return_contour = dict()

    if options["mode"] == "mass":
        h2D.SetTitle("Signal Exclusion for mH^{#pm}" + f" = {cond} [GeV]")
    elif options["mode"] == "rtt":
        h2D.SetTitle("Signal Exclusion for #rho_{tt}" + f" = {cond} ")
    h2D.GetXaxis().SetTitle(options['xTitle'])
    h2D.GetYaxis().SetTitle(options['yTitle'])
    h2D.GetZaxis().SetTitle(options['zTitle'])
    h2D.Draw("COLZ")
    c.Update()

    legend = ROOT.TLegend(0.15, 0.85, 0.40, 0.9)
     

    for target_legend, target_value in target_values.items():
        return_contour[target_legend] = h2D.Clone()
        return_contour[target_legend].SetContour(2)
        return_contour[target_legend].SetContourLevel(1, target_value)
        return_contour[target_legend].SetContourLevel(0, 1e10)
        return_contour[target_legend].SetLineWidth(3)
        return_contour[target_legend].SetLineColor(ROOT.kRed)
        return_contour[target_legend].Draw("cont same")

        legend.AddEntry(return_contour[target_legend], target_legend)
    CheckDir(os.path.join(config.outdir, 'signal_exclusion'))
    if options['mode'] == 'mass':
        outputfile = os.path.join(config.outdir, 'signal_exclusion', f'exclusion_from_{param}_M{cond}')
    elif options['mode'] == 'rtt':
        outputfile = os.path.join(config.outdir, 'signal_exclusion', f'exclusion_from_{param}_rtt{cond}')
    if 'postfix' in options:
        outputfile += '_' + options['postfix']
    legend.Draw("SAME")
    c.SaveAs(outputfile + ".png")
    c.SaveAs(outputfile + ".pdf")
    c.SaveAs(outputfile + ".C")


    return_contour_graph = dict()
    for target_legend, target_value in target_values.items():
        return_contour[target_legend].Draw("cont list")
        ROOT.gPad.Update()
        contours = ROOT.gROOT.GetListOfSpecials().FindObject("contours").At(1)
        if contours:
            return_contour_graph[target_legend] = extend_graph(contours.First().Clone(), return_contour[target_legend], target_value)
        else:
            return_contour_graph[target_legend] = None
    return h2D, return_contour, return_contour_graph

def extend_graph(graph, hist, threshold):

    x_array = []
    y_array = []

    if hist.GetBinContent(hist.GetNbinsX(), hist.GetNbinsY()) < threshold:
      x_array.append(hist.GetXaxis().GetBinLowEdge(hist.GetNbinsX()+1))
      y_array.append(hist.GetYaxis().GetBinLowEdge(hist.GetNbinsY()+1))
    if hist.GetBinContent(1, hist.GetNbinsY()) < threshold:
      x_array.append(hist.GetXaxis().GetBinLowEdge(1))
      y_array.append(hist.GetYaxis().GetBinLowEdge(hist.GetNbinsY()+1))

#    for bin_idx_x in range(1, hist.GetNbinsX()+1):
#      y_upper = hist.GetBinContent(bin_idx_x, hist.GetNbinsY())
#      y_lower = hist.GetBinContent(bin_idx_x, 1)
#      if y_upper < threshold:
#          x_array.append(hist.GetXaxis().GetBinCenter(bin_idx_x))
#          y_array.append(hist.GetYaxis().GetBinLowEdge(hist.GetNbinsY()+1))
#      if y_lower < threshold:
#          x_array.append(hist.GetXaxis().GetBinCenter(bin_idx_x))
#          y_array.append(hist.GetYaxis().GetBinLowEdge(1))

#    for bin_idx_y in range(1, hist.GetNbinsY()+1):
#      x_left = hist.GetBinContent(1, bin_idx_y)
#      x_right = hist.GetBinContent(hist.GetNbinsX(), bin_idx_y)
#
#      if x_left < threshold:
#          x_array.append(hist.GetXaxis().GetBinLowEdge(1))
#          y_array.append(hist.GetYaxis().GetBinCenter(bin_idx_y))
#      if x_right < threshold:
#          x_array.append(hist.GetXaxis().GetBinLowEdge(hist.GetNbinsX()+1))
#          y_array.append(hist.GetYaxis().GetBinCenter(bin_idx_y))

    for x, y in zip(x_array, y_array):
        graph.SetPoint(graph.GetN(), x, y)

    #graph.Sort(ROOT.TGraph.CompareArg)
    return graph

def draw_exclusion_line(exclusion_line, outfile_name, config):
    
    for title, line in exclusion_line["expected"].items():
      line = line["TProfile2D"]
      x_axis = line.GetXaxis()
      y_axis = line.GetYaxis()
      x_title = line.GetXaxis().GetTitle()
      y_title = line.GetYaxis().GetTitle()
      nbinX  = x_axis.GetNbins()
      nbinY  = y_axis.GetNbins()
      x_binnings = [x_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinX+1)]
      y_binnings = [y_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinY+1)]
      break

    c = CMS.cmsCanvas('', min(x_binnings), max(x_binnings), 0.1, max(y_binnings), x_title, y_title, square = CMS.kSquare, extraSpace=0.03, iPos=0, with_z_axis=False)
    c.SetLogy()
    c.SetRightMargin(0.06)
    legend = CMS.cmsLeg(0.7, 0.17, 0.85, 0.42, textSize=0.035)
    legend2 = CMS.cmsLeg(0.5, 0.17, 0.7, 0.27, textSize=0.035)

    line_idx = 0
    line_array = dict()
    for title, line in exclusion_line["expected"].items():
        line = line["TGraph"]
        if line is None: continue
        line.SetLineStyle(2)
        line.SetLineWidth(2)
        line.SetLineColor(ROOT.kBlue + 2 * line_idx)
        line.SetFillColorAlpha(ROOT.kBlue + 2 * line_idx, 0.1)
        if config.unblind:
            line_obs = exclusion_line["observed"][title]["TGraph"]
            line_obs.SetLineStyle(1)
            line_obs.SetLineWidth(2)
            line_obs.SetLineColor(ROOT.kBlue + 2 * line_idx)
            line_obs.SetFillColorAlpha(ROOT.kBlue +  2 * line_idx, 0.4)
            line_obs.Draw('F same')
            if line_idx == 0:
              legend2.AddEntry(line_obs, "observed", "F")

        line_idx += 1
        line_array[title] = line.Clone()

    line_idx = 0
    for title, line in line_array.items():
        line.Draw("same")
        if line_idx == 0:
          legend2.AddEntry(line, "expected", "L")
        legend.AddEntry(line, title, "LF")

        line_idx += 1


    legend.Draw("SAME")
    latex = ROOT.TLatex()
    latex.SetTextSize(0.05)
    latex.SetTextAlign(12)
    latex.SetNDC()
    latex.SetTextFont(42);
    latex.DrawLatex(0.3, 0.7, "excluded")
    c.Update()
    c.SaveAs(outfile_name + ".png")
    c.SaveAs(outfile_name + ".pdf")
    c.SaveAs(outfile_name + ".C")

def analysis(config):

    unique_masses = df_sig_xsec["Mass"].unique()
    
    info_dict = dict()

    for mass_ in unique_masses:
      if str(mass_) not in ratio: continue
      info_dict[mass_] = dict()
      unique_rtt_rtc = df_sig_xsec[df_sig_xsec["Mass"] == int(mass_)][["rtt", "rtc", "xsec"]]
      coupling_list = []
      xsec2b_list   = []
      xsec3b_list   = []
      rtt_list      = []
      rtc_list      = []
      limit_list    = []

      limit_1D_dc = os.path.join(config.outdir, f"bin/run2/{config.region}/{config.channel}/limits_bH_rtt0p6_rtc0p4_asimov_extYukawa_MH{mass_}.txt")
      limit = float([iline.rstrip() for iline in open (limit_1D_dc)][0].split(' ')[4])

      if config.unblind:
          limit_unblind = float([iline.rstrip() for iline in open (limit_1D_dc)][0].split(' ')[7])

      for _, coupling_ in unique_rtt_rtc.iterrows():
          coupling = tuple(["%.2f"%coupling_["rtt"], "%.2f"%coupling_["rtc"]])
          info_dict[mass_][coupling] = dict()

          info_dict[mass_][coupling]["xsec"] = coupling_["xsec"]
          info_dict[mass_][coupling]["xsec_2b"] = coupling_["xsec"] * ratio[str(mass_)] / (1.0 + ratio[str(mass_)])
          info_dict[mass_][coupling]["xsec_3b"] = coupling_["xsec"] * 1.0 / (1.0 + ratio[str(mass_)])
          info_dict[mass_][coupling]["ratio"] = ratio[str(mass_)]
          info_dict[mass_][coupling]["limit_on_signal_strength"] =  limit / coupling_["xsec"]
          if config.unblind:
              info_dict[mass_][coupling]["observed_limit_on_signal_strength"] = limit_unblind / coupling_["xsec"]
          
          coupling_list.append(coupling)
          xsec2b_list.append(info_dict[mass_][coupling]["xsec_2b"])
          xsec3b_list.append(info_dict[mass_][coupling]["xsec_3b"])
          rtt_list.append(float(coupling[0]))
          rtc_list.append(float(coupling[1]))
          limit_list.append(limit / coupling_["xsec"] )

      #plot_options = {"strategy": "linear", "mode": "mass", "xTitle": "#rho_{tt}", "yTitle": "#rho_{tc}", "zTitle": "95% C.L. on #mu = #sigma/#sigma_{theory}"}
      #h2D, contour = draw_contour2D(rtt_list, rtc_list, limit_list, target_values = {"exclusion": 1.0}, config = config, n_points = 200, cond = mass_, options = plot_options)

      #xsec_2b_unit = ratio[str(mass_)] / (1.0 + ratio[str(mass_)])
      #xsec_3b_unit = 1.0 / (1.0 + ratio[str(mass_)])
      
      #NLL_file = os.path.join(config.outdir,  f"2DNLL/higgsCombinerun2_C_C_MH{mass_}_rtt0p6_rtc0p4_asimov_extYukawa_2DNLL.MultiDimFit.mH120.root")
      #fit_options = {"strategy": "cubic"}
      #output = get_2DNLL(NLL_file, xsec_2b = xsec_2b_unit, xsec_3b = xsec_3b_unit, input_x = xsec2b_list, input_y = xsec3b_list, options = fit_options)
      #h2D, contour = draw_contour2D(rtt_list, rtc_list, output, target_values = {"exclusion": 5.99}, config = config, n_points = 200, cond = mass_, options = plot_options, param = "NLL")
      #for idx, rtt_ in enumerate(rtt_list):
      #    rtc_ = rtc_list[idx]
      #    coupling_ = tuple(["%.2f"%rtt_, "%.2f"%rtc_]) 
      #    info_dict[mass_][coupling_]["NLL"] = output[idx]


    exclusion_line_signal_strength = dict()
    exclusion_line_NLL             = dict()
    exclusion_line_signal_strength["expected"] = dict()
    exclusion_line_signal_strength["observed"]  = dict()


    for rtt_ in ["1.00", "0.60", "0.40", "0.30", "0.20"]:
      rtc_list   = []
      mass_list  = []
      limit_list = []
      NLL_list   = []
      limit_list_observed = []
      for mass_ in info_dict:
          for coupling_ in info_dict[mass_]:
              rtt_coupling = coupling_[0]
              rtc_coupling = coupling_[1]
              if not (rtt_ == rtt_coupling): continue
              mass_list.append(float(mass_))
              rtc_list.append(float(rtc_coupling))
              limit_list.append(float(info_dict[mass_][coupling_]["limit_on_signal_strength"]))
              limit_list_observed.append(float(info_dict[mass_][coupling_]["observed_limit_on_signal_strength"]))
              #NLL_list.append(float(info_dict[mass_][coupling_]["NLL"]))
    
      plot_options = {"strategy": "linear", "mode": "rtt", "xTitle": "m_{H^{#pm}} [GeV]", "yTitle": "#rho_{tc}", "zTitle": "95% C.L. on #mu = #sigma/#sigma_{theory}"}
      h2D, contour, contour_graph = draw_contour2D(mass_list, rtc_list, limit_list, target_values = {"exclusion": 1.0}, config = config, n_points = 200, cond = rtt_, options = plot_options, param = 'signal_strength')
      exclusion_line_signal_strength["expected"]["#rho_{tt} = " + rtt_] = {"TProfile2D": contour["exclusion"], "TGraph": contour_graph["exclusion"]}
      if config.unblind:
          plot_options = {"strategy": "linear", "mode": "rtt", "xTitle": "m_{H^{#pm}} [GeV]", "yTitle": "#rho_{tc}", "zTitle": "95% C.L. on #mu = #sigma/#sigma_{theory}", 'postfix': 'unblind'}
          h2D, contour, contour_graph =  draw_contour2D(mass_list, rtc_list, limit_list_observed, target_values = {"exclusion": 1.0}, config = config, n_points = 200, cond = rtt_, options = plot_options, param = 'signal_strength')
          exclusion_line_signal_strength["observed"]["#rho_{tt} = " + rtt_] = {"TProfile2D": contour["exclusion"], "TGraph": contour_graph["exclusion"]}

    #  _, contour_NLL = draw_contour2D(mass_list, rtc_list, NLL_list, target_values = {"exclusion": 5.99}, config = config, n_points = 200, cond = rtt_, options = plot_options, param = 'NLL')
    #  exclusion_line_NLL["#rho_{tt} = " + rtt_] = contour_NLL["exclusion"]
      
    draw_exclusion_line(exclusion_line_signal_strength, os.path.join(config.outdir, "signal_exclusion", "exclusion_summary_rtt_signal_strength"), config = config)
    #draw_exclusion_line(exclusion_line_NLL, os.path.join(config.outdir, "signal_exclusion", "exclusion_summary_rtt_NLL"))




if __name__ == "__main__":
    usage = "python ..."
    parser = argparse.ArgumentParser(description = usage)
    parser.add_argument('--outdir', default = './', type = str)
    parser.add_argument('--region', default = 'C',  type = str)
    parser.add_argument('--channel', default= 'C',  type = str)
    parser.add_argument('--unblind', action = 'store_true')
    args = parser.parse_args()

    analysis(args)
