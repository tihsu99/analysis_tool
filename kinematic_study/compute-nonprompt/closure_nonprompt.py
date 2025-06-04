import ROOT
from copy import deepcopy
from array import array
import numpy as np
import os

ROOT.gROOT.SetBatch(True)

folder = '/eos/user/g/gkole/database/bHplus/16May2025/'

regions_vars = {'NonPrompt_D': ['QCD_Lepton_eta','QCD_Lepton_pt'],
                'NonPrompt_C': ['Lepton_eta','Lepton_pt']
                }

years = ['2016apv', '2016postapv', '2017', '2018']
years = ['2016apv']

# Convert Python function to ROOT callable
ROOT.gInterpreter.Declare("""
    #include <map>
    #include <string>

    std::map<std::string, TH2F*> sf_hist_map;

    double get_sf_cpp(float pt, float eta, const std::string& key) {
        auto it = sf_hist_map.find(key);
        if (it == sf_hist_map.end() || !(it->second)) return 1.0;
        TH2F* hist = it->second;
        int binx = hist->GetXaxis()->FindBin(pt);
        int biny = hist->GetYaxis()->FindBin(fabs(eta));
        double sf = hist->GetBinContent(binx, biny);
        if (sf == 0 || sf == 1) return 1.0;
        else if (abs(1-sf)<0.01) return 1.0;
        return sf/(1.0-sf);
    }
""")

#if (sf == 0 || sf == 1) return 1.0;
#else if (abs(1-sf)<0.01) return 1.0;
# Define a new column with the scale factor
def apply_sf(df, year, channel):
    # Load scale factor histogram
    key = load_sf_histogram(year, channel)
    df2 = df.Define("SF_lepton", f'get_sf_cpp(QCD_Lepton_pt, QCD_Lepton_eta, "{key}")')
    return df2

def draw_and_save(histo, name, options='COLZ', logz=True):
    canvas = ROOT.TCanvas(name, name, 800, 600)
    #histo.SetTitle('; lepton p_{T} [GeV]; lepton #eta')
    print('Drawing', histo.Integral())
    histo.Draw(options)
    #histo.SetStats(0)
    if logz:
        canvas.SetLogz()
    canvas.Modified()
    canvas.Update()
    canvas.Print(f'closure_plots/{name}.png')
    canvas.Print(f'closure_plots/{name}.pdf')
    return canvas

def ratio_plot(histo1, histo2, name,ratio_min=-2.0, ratio_max=2.0,label1="D", label2="C"):

    h1 = histo1.GetValue()
    h2 = histo2.GetValue()
    canvas = ROOT.TCanvas(name, name, 800, 800)
    canvas.Divide(1,2)
    pad1 = canvas.cd(1)
    pad1.SetPad(0.0, 0.3, 1.0, 1.0)
    pad1.SetBottomMargin(0.02)
    pad1.SetTicks(1,1)
    pad1.SetGrid()

    # Remove stat box
    h1.SetStats(0)
    h2.SetStats(0)

    h1.SetLineColor(ROOT.kRed)
    h2.SetLineColor(ROOT.kBlue)
    h1.SetMarkerColor(ROOT.kRed)
    h2.SetMarkerColor(ROOT.kBlue)
    h1.SetMarkerStyle(20)
    h2.SetMarkerStyle(21)
    h1.SetMarkerSize(1.0)
    h2.SetMarkerSize(1.0)

    # Find max and set y-axis range
    max1 = h1.GetMaximum()
    max2 = h2.GetMaximum()
    ymax = 1.2 * max(max1, max2)
    h1.SetMaximum(ymax)
    h2.SetMaximum(ymax)

    # Draw the histogram with the higher max first
    if max1 >= max2:
        h1.Draw("E1")
        h2.Draw("E1 SAME")
    else:
        h2.Draw("E1")
        h1.Draw("E1 SAME")

    # h2.Draw("hist E1")
    # h1.Draw("hist E1 SAME")
    legend = ROOT.TLegend(0.65, 0.75, 0.88, 0.88)
    legend.AddEntry(h1, label1, "lep")
    legend.AddEntry(h2, label2, "lep")
    legend.Draw()

    pad2 = canvas.cd(2)
    pad2.SetPad(0.0, 0.0, 1.0, 0.3)
    pad2.SetTopMargin(0.02)
    pad2.SetBottomMargin(0.3)
    pad2.SetTicks(1,1)
    pad2.SetGrid()
    ratio = h1.Clone("ratio")
    ratio.Divide(h1, h2, 1.0, 1.0, "B")
    ratio.SetStats(0)
    ratio.SetLineColor(ROOT.kBlack)
    ratio.SetMarkerStyle(20)
    ratio.SetMarkerSize(1.0)
    ratio.SetTitle("")
    ratio.GetYaxis().SetTitle("D/C")
    ratio.GetYaxis().SetNdivisions(505)
    ratio.GetYaxis().SetTitleSize(0.13)
    ratio.GetYaxis().SetTitleOffset(0.4)
    ratio.GetYaxis().SetLabelSize(0.11)
    ratio.GetXaxis().SetTitleSize(0.13)
    ratio.GetXaxis().SetLabelSize(0.11)
    ratio.SetMinimum(ratio_min)
    ratio.SetMaximum(ratio_max)
    ratio.Draw("E1")

    canvas.SaveAs(f'closure_plots/{name}.png')
    canvas.SaveAs(f'closure_plots/{name}.pdf')

        # canvas = ROOT.TCanvas(name, name, 800, 600)
        # histo1.SetLineColor(ROOT.kRed)
        # histo2.SetLineColor(ROOT.kBlue)
        # histo1.SetMarkerColor(ROOT.kRed)
        # histo2.SetMarkerColor(ROOT.kBlue)
        # histo1.SetMarkerStyle(20)
        # histo2.SetMarkerStyle(21)
        # histo1.SetMarkerSize(1.0)
        # histo2.SetMarkerSize(1.0)
        # # Only set E1 for the numerator, since TRatioPlot will draw the denominator with errors
        # ratio = ROOT.TRatioPlot(histo1.GetPtr(), histo2.GetPtr(), "E1")
        # ratio.Draw("E1")
        # ratio.GetLowerRefYaxis().SetRangeUser(ratio_min, ratio_max)
        # # Draw numerator with errors on the upper pad
        # upper_pad = ratio.GetUpperPad()
        # upper_pad.cd()
        # # histo1.Draw("E1 SAME")
        # # histo1.SetOption("E1")
        # # histo2.SetOption("E1")
        # # ratio = ROOT.TRatioPlot(histo1.GetPtr(), histo2.GetPtr())
        # # ratio.Draw()
        # # ratio.GetLowerRefYaxis().SetRangeUser(ratio_min, ratio_max)
        # # # ratio.SetYAxisRange(ratio_min, ratio_max)
        # # # Add legend to the upper pad
        # # upper_pad = ratio.GetUpperPad()
        # # upper_pad.cd()
        # legend = ROOT.TLegend(0.65, 0.75, 0.88, 0.88)
        # legend.AddEntry(histo1.GetPtr(), label1, "l")
        # legend.AddEntry(histo2.GetPtr(), label2, "l")
        # legend.Draw()

        # canvas.Update()
        # canvas.Print(f'closure_plots/{name}.png')
        # canvas.Print(f'closure_plots/{name}.pdf')



def load_sf_histogram(year, channel):
    key = f"{year}_{channel}"
    filename = f"non_prompt_{year}_1b_notopcut.root"
    file = ROOT.TFile.Open(filename)
    hist = file.Get(channel)
    if not hist:
        raise RuntimeError(f"Histogram '{channel}' not found in {filename}")
    hist.SetDirectory(0)  # Detach from file
    file.Close()
    ROOT.sf_hist_map[key] = hist  # Register in global map
    return key

if not os.path.exists('closure_plots'):
    os.makedirs('closure_plots')

# input_filename = 'TTTo1L'
input_filename = "QCD"
HT_bins = ['HT50to100','HT100to200', 'HT200to300', 'HT300to500', 'HT500to700', 'HT700to1000', 'HT1000to1500', 'HT1500to2000', 'HT2000toInf']

selection = '(n_bjet_DeepB_v == 1)'

for year in years:
    for channel in ['mu_resolved', 'ele_resolved']:
        print(f"Processing {year} for {channel}")
        # Input file and tree
        # input_fileC = f"{folder}/NonPrompt_C/{year}/NonPrompt_C_default/{channel}/{input_filename}.root"
        # input_fileD = f"{folder}/NonPrompt_D/{year}/NonPrompt_D_default/{channel}/{input_filename}.root"
        input_fileC = [f"{folder}/NonPrompt_C/{year}/NonPrompt_C_default/{channel}/{input_filename}_{HT_bins[i]}.root" for i in range(len(HT_bins))]
        input_fileD = [f"{folder}/NonPrompt_D/{year}/NonPrompt_D_default/{channel}/{input_filename}_{HT_bins[i]}.root" for i in range(len(HT_bins))]
        # print (input_fileC)
        # print (input_fileD)

        tree_name = "Events"

        # Create RDataFrame
        dfC = ROOT.RDataFrame(tree_name, input_fileC)
        dfD = ROOT.RDataFrame(tree_name, input_fileD)

        df2 = apply_sf(dfD, year, channel)

        # Output file
        output_file = f"{input_filename}_{year}_{channel}_sf.root"
        # Save the new tree with the scale factor applied
        df2.Snapshot("Events", output_file)
        # Define the histogram model: (nbins, xmin, xmax)
        # hist_pt = ROOT.RDF.TH1DModel("lep_pt", ";lepton p_{T} [GeV];Events", 50, 0, 500)
        # Example: variable bin edges for lepton pt
        pt_bins = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380, 390, 400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500], dtype=float)
        hist_pt = ROOT.RDF.TH1DModel("lep_pt", ";lepton p_{T} [GeV];Events", len(pt_bins)-1, array('d', pt_bins))
        hist_eta = ROOT.RDF.TH1DModel("lep_eta", "; lepton #eta ;Events", 24, -2.4, 2.4)
        hist_metpt = ROOT.RDF.TH1DModel("met_pt", ";MET p_{T} [GeV];Events", 50, 0, 500)
        hist_SF = ROOT.RDF.TH1DModel("SF_lepton", ";SF;Events", 50, 0, 10)
        df2 = df2.Define("total_weight", "weight_n_Norm * SF_lepton")

        hist_lepetaD = df2.Filter(selection).Histo1D(hist_eta, "QCD_Lepton_eta", "total_weight")
        hist_lepetaC = dfC.Filter(selection).Histo1D(hist_eta, "Lepton_eta", 'weight_n_Norm')

        hist_lepptD_woW = dfD.Filter(selection).Histo1D(hist_pt, "QCD_Lepton_pt", "weight_n_Norm")
        hist_lepptD = df2.Filter(selection).Histo1D(hist_pt, "QCD_Lepton_pt", "total_weight")
        hist_lepptC = dfC.Filter(selection).Histo1D(hist_pt, "Lepton_pt", 'weight_n_Norm')

        hist_metptD = df2.Filter(selection).Histo1D(hist_metpt, "bh_met", "total_weight")
        hist_metptC = dfC.Filter(selection).Histo1D(hist_metpt, "bh_met", 'weight_n_Norm')

        draw_and_save(hist_lepetaD, f"lep_eta_{year}_{channel}_D", 'hist')
        draw_and_save(hist_lepetaC, f"lep_eta_{year}_{channel}_C", 'hist')

        draw_and_save(hist_lepptD_woW, f"lep_pt_{year}_{channel}_D_woW", 'hist')
        draw_and_save(hist_lepptD, f"lep_pt_{year}_{channel}_D", 'hist')
        draw_and_save(hist_lepptC, f"lep_pt_{year}_{channel}_C", 'hist')
        draw_and_save(hist_metptD, f"met_pt_{year}_{channel}_D", 'hist')
        draw_and_save(hist_metptC, f"met_pt_{year}_{channel}_C", 'hist')

        draw_and_save(df2.Histo1D(hist_SF, "SF_lepton"), f"lep_sf_{year}_{channel}", 'hist')
        print('histlepetaD', type(hist_lepetaD))
        print('histlepetaC', type(hist_lepetaC))
        ratio_plot(hist_lepetaD, hist_lepetaC, f"lep_eta_{year}_{channel}_ratio", -2.0, 6.0)
        ratio_plot(hist_lepptD, hist_lepptC, f"lep_pt_{year}_{channel}_ratio", 0.0, 4.0)
        ratio_plot(hist_metptD, hist_metptC, f"met_pt_{year}_{channel}_ratio",0.0, 2.0)
        #ratio_lepeta = ROOT.TRatioPlot(hist_lepetaD.GetPtr(), hist_lepetaC.GetPtr())
        #ratio_leppt = ROOT.TRatioPlot(hist_lepptD.GetPtr(), hist_lepptC.GetPtr())
