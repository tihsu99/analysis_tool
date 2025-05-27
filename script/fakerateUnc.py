import ROOT
import os
import math

# Disable GUI popups (useful for batch mode)
ROOT.gROOT.SetBatch(True)

# Set text precision for bin labels
ROOT.gStyle.SetPaintTextFormat("1.2f")  # Format: 2 decimal places

def compute_final_histogram(year):
    input_dir = "/afs/cern.ch/user/g/gkole/work/BHplus/SR_plots/Analysis/CMSSW_14_1_0_pre4/src/bHplusAnalysis/data/non-prompt-fr/"  # input directory
    hist_names = ["mu_resolved", "ele_resolved"]

    file_1b = ROOT.TFile.Open(os.path.join(input_dir, f"non_prompt_{year}_1b_notopcut.root"))
    file_2b = ROOT.TFile.Open(os.path.join(input_dir, f"non_prompt_{year}_2b_notopcut.root"))
    file_out = ROOT.TFile.Open(f"non_prompt_{year}_final_notopcut.root", "RECREATE")

    if not file_1b or file_1b.IsZombie():
        print(f"Error opening 1b file for {year}")
        return
    if not file_2b or file_2b.IsZombie():
        print(f"Error opening 2b file for {year}")
        return

    for hist_name in hist_names:
        h1b = file_1b.Get(hist_name)
        h2b = file_2b.Get(hist_name)

        if not h1b or not h2b:
            print(f"Missing histogram {hist_name} in one of the input files for {year}")
            continue

        # Clone 1b histogram to use binning and central values
        h_final = h1b.Clone(f"{hist_name}")
        h_final.SetTitle(f"{hist_name} (final)")
        h_final.Reset("ICES")  # Reset contents but keep structure

        verbose = False
        # Loop over bins
        for x in range(1, h1b.GetNbinsX() + 1):
            for y in range(1, h1b.GetNbinsY() + 1):
                val_1b = h1b.GetBinContent(x, y)
                if (verbose): print (f"Processing bin ({x}, {y}) - 1b value: {val_1b}")
                err_1b = h1b.GetBinError(x, y)
                if (verbose): print (f"Processing bin ({x}, {y}) - 1b error: {err_1b}")
                val_2b = h2b.GetBinContent(x, y)
                if (verbose): print (f"Processing bin ({x}, {y}) - 2b value: {val_2b}")

                # Error = sqrt( stat^2 + (diff)^2 )
                diff = val_1b - val_2b
                total_err = math.sqrt(err_1b**2 + diff**2)
                if (verbose): print (f"Processing bin ({x}, {y}) - total error: {total_err}")

                h_final.SetBinContent(x, y, val_1b)
                h_final.SetBinError(x, y, total_err)
                if (total_err > 1.0 or total_err < 0.0): print (total_err)

        # Write histogram to output file
        h_final.Write()
        # Plotting the histogram
        canvas = ROOT.TCanvas("c", "", 1000, 800)
        canvas.SetRightMargin(0.15)
        h_final.SetStats(0)
        h_final.Draw("COLZ TEXTE")
        output_base = f"{hist_name}_{year}"
        canvas.SaveAs(f"{output_base}.png")
        canvas.SaveAs(f"{output_base}.pdf")
        canvas.Close()
        print(f"Processed histogram {hist_name} for {year}")
    # Save and close the output file
    file_out.Write()
    print(f"Final histograms for {year} saved to non_prompt_{year}_final_notopcut.root")
    # Close all files


    file_out.Close()
    file_1b.Close()
    file_2b.Close()
    print(f"Done processing {year}")

# Run for all years
for year in ["2016apv", "2016postapv", "2017", "2018"]:
    compute_final_histogram(year)
