import ROOT
import os
import math

# Disable GUI popups (useful for batch mode)
ROOT.gROOT.SetBatch(True)

# Set text precision for bin labels
ROOT.gStyle.SetPaintTextFormat("1.2f")  # Format: 2 decimal places

def compute_final_histogram(year):
    input_dir = "./"  # input directory
    # hist_names = ["mu_resolved", "ele_resolved"]

    file_1b_ele = ROOT.TFile.Open(os.path.join(input_dir, f"non_prompt_{year}_1b_notopcut.root"))
    file_2b_ele = ROOT.TFile.Open(os.path.join(input_dir, f"non_prompt_{year}_2b_notopcut.root"))

    file_1b_mu = ROOT.TFile.Open(os.path.join(input_dir, f"fr2d_mu_resolved_{year}_1b_notopcut.root"))
    file_2b_mu = ROOT.TFile.Open(os.path.join(input_dir, f"fr2d_mu_resolved_{year}_2b_notopcut.root"))

    # Output file
    outdir = "../../data/non-prompt-fr/"
    file_out = ROOT.TFile.Open(os.path.join(outdir, f"non_prompt_{year}_final_notopcut.root"), "RECREATE")

    if not (file_1b_ele or file_1b_mu or file_1b_ele.IsZombie() or file_1b_mu.IsZombie()):
        print(f"Error opening 1b file for {year}")
        return
    if not (file_2b_ele or file_1b_mu or file_2b_ele.IsZombie() or file_2b_mu.IsZombie()):
        print(f"Error opening 2b file for {year}")
        return

    # For electrons
    hist_name = "ele_resolved"
    h1b = file_1b_ele.Get(hist_name)
    h2b = file_2b_ele.Get(hist_name)
    if not h1b or not h2b:
        print(f"Missing histogram {hist_name} in one of the input files for {year}")
    else:
        h_final = h1b.Clone(f"{hist_name}")
        h_final.SetTitle(f"{hist_name} (final)")
        h_final.Reset("ICES")
        verbose = False
        for x in range(1, h1b.GetNbinsX() + 1):
            for y in range(1, h1b.GetNbinsY() + 1):
                val_1b = h1b.GetBinContent(x, y)
                err_1b = h1b.GetBinError(x, y)
                val_2b = h2b.GetBinContent(x, y)
                diff = val_1b - val_2b
                total_err = math.sqrt(err_1b**2 + diff**2)
                h_final.SetBinContent(x, y, val_1b)
                h_final.SetBinError(x, y, total_err)
        h_final.Write()
        canvas = ROOT.TCanvas("c_ele", "", 1000, 800)
        canvas.SetRightMargin(0.15)
        h_final.SetStats(0)
        h_final.Draw("COLZ TEXTE")
        output_base = f"{hist_name}_{year}"
        canvas.SaveAs(f"{output_base}.png")
        canvas.SaveAs(f"{output_base}.pdf")
        canvas.Close()
        print(f"Processed histogram {hist_name} for {year}")

    # For muons
    hist_name = "mu_resolved"
    h1b = file_1b_mu.Get(hist_name)
    h2b = file_2b_mu.Get(hist_name)
    if not h1b or not h2b:
        print(f"Missing histogram {hist_name} in one of the input files for {year}")
    else:
        h_final = h1b.Clone(f"{hist_name}")
        h_final.SetTitle(f"{hist_name} (final)")
        h_final.Reset("ICES")
        verbose = False
        for x in range(1, h1b.GetNbinsX() + 1):
            for y in range(1, h1b.GetNbinsY() + 1):
                val_1b = h1b.GetBinContent(x, y)
                err_1b = h1b.GetBinError(x, y)
                val_2b = h2b.GetBinContent(x, y)
                diff = val_1b - val_2b
                total_err = math.sqrt(err_1b**2 + diff**2)
                h_final.SetBinContent(x, y, val_1b)
                h_final.SetBinError(x, y, total_err)
        h_final.Write()
        canvas = ROOT.TCanvas("c_mu", "", 1000, 800)
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
    file_1b_ele.Close()
    file_2b_ele.Close()
    file_1b_mu.Close()
    file_2b_mu.Close()
    print(f"Done processing {year}")

# Run for all years
for year in ["2016apv" , "2016postapv", "2017", "2018"]:
    compute_final_histogram(year)
