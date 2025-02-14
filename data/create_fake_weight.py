import ROOT

file = "Trigger_scale_factor_2017_summary.root"
outfile = "Trigger_scale_factor_2017_test.root"

histograms = []

fin = ROOT.TFile.Open(file, "READ")
for key in fin.GetListOfKeys():
  obj = key.ReadObj()
  obj.SetDirectory(0)
  h2D = obj.Clone()
  h2D.SetDirectory(0)
  histograms.append(h2D)

fin.Close()
fout = ROOT.TFile.Open(outfile, "RECREATE")
fout.cd()
for hist in histograms:
  for x in range(1, hist.GetNbinsX() + 1):
    for y in range(1, hist.GetNbinsY() + 1):
      hist.SetBinError(x,y, hist.GetBinContent(x, y)*0.1)
  hist.Write()
fout.Close()
