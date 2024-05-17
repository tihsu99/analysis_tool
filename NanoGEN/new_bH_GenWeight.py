import ROOT
from optparse import OptionParser 
import sys
import os
from array import array


def makehisto(list_hists, title_labels, outputname, central_hist = None, logscale = False):
    '''takes a list of histograms or a histogram and makes and stores the plot  '''
    canv = ROOT.TCanvas("c1", "L", 1200, 1200)
    if logscale:
        canv.SetLogy()
    legend = ROOT.TLegend(0.6,0.5,0.87,0.85)
    color_cnt = 2
    if type(list_hists) != type([]):
        list_hists = [list_hists]
    maxval = []
    minval = []
    
    for hist in list_hists:
      maxval.append(hist.GetMaximum())
      minval.append(hist.GetMinimum())
    ymax = max(maxval)*1.1
    ymin = min(minval)
    
    # print("interval of maxval: {}, ymax = {}".format(maxval, ymax))
    for hist in list_hists:
        legend.AddEntry(hist, hist.GetTitle(), "l")
        hist.SetTitle("{}".format(title_labels))
        hist.SetLineColorAlpha(color_cnt, 1)
        hist.SetLineWidth(2)
        hist.GetYaxis().SetTitleOffset(1.3)
        hist.GetXaxis().SetTitleOffset(1.1)
        hist.SetMaximum(ymax) # good for most plots ymax = 1.2
        hist.SetMinimum(ymin) 
        hist.SetStats(0) #stat box in top-right corner will not print
        color_cnt += 1
        hist.Draw("hist SAME")
    if central_hist:
        legend.AddEntry(central_hist, central_hist.GetTitle(), "l")
        central_hist.SetLineColor(ROOT.kBlack)
        central_hist.SetLineWidth(2)
        central_hist.Draw("hist SAME")

    legend.SetTextSize(0.02)
    # Sets the fraction of the width which the symbol in the legend takes
    #legend.SetMargin(0)
    legend.SetBorderSize(0)
    legend.Draw("SAME")
    canv.Print(f"/eos/user/{os.getenv('USER')[0]}/{os.getenv('USER')}/www/bHplus/NanoGEN/{outputname}.png")
    canv.Print(f"/eos/user/{os.getenv('USER')[0]}/{os.getenv('USER')}/www/bHplus/NanoGEN/{outputname}.pdf")

def main():
    usage = 'usage: %prog [options]'
    parser = OptionParser(usage)
    parser.add_option('-i', '--in', dest='inputfiles', help='name of input files', default=None, type='string')
    parser.add_option('-o', '--out', dest='outputfiles', help='name output files', default=None, type='string')
    (opt, args) = parser.parse_args()
    ROOT.gROOT.SetBatch(True)

    binning = array('d', [20, 35, 50, 80, 120, 160, 200, 260, 320, 450, 700, 1000] )
    binning = array('d', [2, 3, 4, 5, 6, 7, 8, 9, 10] )

    if not os.path.isfile(opt.inputfiles): 
        print(f'inputfile {opt.inputfile} does not exist!!')
    filein = ROOT.TFile.Open(opt.inputfiles)
    treein = filein.Get('Events')
    outname = opt.inputfiles.split('/')[-1].replace('.root','')
    hist_scaleup = ROOT.TH1F('scaleup','scaleup', len(binning)-1, binning)
    hist_scaledown = ROOT.TH1F('scaledown','scaledown', len(binning)-1, binning)
    hist_PSup = ROOT.TH1F('PSup','PSup', len(binning)-1, binning)
    hist_PSdown = ROOT.TH1F('PSdown','PSdown', len(binning)-1, binning)
    hist_central = ROOT.TH1F('central','central', len(binning)-1, binning)
    
    variable = 'nGenJet'
    #variable = 'Jet_pt'

    #for i in range(treein.GetEntries()):
    for i in range(10001):
        treein.GetEntry(i)
        if i%5000 == 0: print(f'processing {i}th event')
        # selection
        if treein.nGenJet < 2 and treein.nGenDressedLepton != 1: continue
        if type(getattr(treein,variable)) == type([]):
            fill_var = getattr(treein,variable)[0]
        else:
            fill_var = getattr(treein,variable)
        hist_scaleup.Fill(fill_var, max([treein.LHEScaleWeight[i] for i in range(treein.nLHEScaleWeight)]))
        hist_scaledown.Fill(fill_var, min([treein.LHEScaleWeight[i] for i in range(treein.nLHEScaleWeight)]))
        hist_PSup.Fill(fill_var, max([treein.PSWeight[i] for i in range(0,4)]))
        hist_PSdown.Fill(fill_var, min([treein.PSWeight[i] for i in range(0,4)]))
        hist_central.Fill(fill_var, 1)
    #makehisto([hist_PSup, hist_PSdown, hist_scaleup, hist_scaledown], "; Leading jet p_{T} [GeV]; Nr. Event", f"comparison_{outname}", hist_central, logscale=True)
    makehisto([hist_PSup, hist_PSdown, hist_scaleup, hist_scaledown], "; No. jets [GeV]; Nr. Event", f"comparison_{outname}_{variable}", hist_central)
    hist_pdfvarup = ROOT.TH1D('pdfvarup','pdfvarup', len(binning)-1, binning)
    hist_scalevarup = ROOT.TH1D('scalevarup','scalevarup', len(binning)-1, binning)
    hist_psvarup = ROOT.TH1D('psvarup','psvarup', len(binning)-1, binning)
    hist_pdfvardown = ROOT.TH1D('pdfvardown','pdfvardown', len(binning)-1, binning)
    hist_scalevardown = ROOT.TH1D('scalevardown','scalevardown', len(binning)-1, binning)
    hist_psvardown = ROOT.TH1D('psvardown','psvardown', len(binning)-1, binning)
    for k in range(1, hist_central.GetNbinsX()+1):
        #hist_pdfvarup.SetBinContent(k, hist_central.GetBinContent(k)*0.02)
        #hist_pdfvardown.SetBinContent(k, hist_central.GetBinContent(k)*0.01)
        hist_scalevarup.SetBinContent(k, abs(hist_scaleup.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k) if hist_central.GetBinContent(k) > 0 else 0)
        hist_scalevardown.SetBinContent(k, abs(hist_scaledown.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k) if hist_central.GetBinContent(k) > 0 else 0)
        hist_psvarup.SetBinContent(k, abs(hist_PSup.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k) if hist_central.GetBinContent(k) > 0 else 0)
        hist_psvardown.SetBinContent(k, abs(hist_PSdown.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k) if hist_central.GetBinContent(k) > 0 else 0)
    makehisto([hist_psvarup, hist_psvardown, hist_scalevarup, hist_scalevardown], "; Leading jet p_{T} [GeV]; percent var", f"percent_variation_{outname}_{variable}")

    fileout = ROOT.TFile.Open(opt.outputfiles+'.root','RECREATE')
    fileout.cd()
    hist_scalevarup.Write()
    hist_scalevardown.Write()
    hist_psvarup.Write()
    hist_psvardown.Write()
    fileout.Close()

if __name__ == "__main__":
  sys.exit(main())