import sys, ROOT, os

ROOT.gROOT.SetBatch(True)
#sys.argv.append( '-b-' )

from ROOT import TFile, TH1F, gDirectory, TCanvas, TPad, TProfile,TGraph, TGraphAsymmErrors,THStack
from ROOT import TH1D, TH1, TH1I
from ROOT import gStyle
from ROOT import gROOT
from ROOT import TStyle
from ROOT import TLegend
from ROOT import TMath
from ROOT import TPaveText
from ROOT import TLatex


mass = '700'
particle = 'a' #or s0
coupling = 'rtc'
cval = "04"
chan = "mm"
year = "2018"

colors=[4,3,2,1,6,9,41,46,30,12,28,20,32]
gStyle.SetOptTitle(0)
gStyle.SetOptStat(0)
gStyle.SetTitleOffset(0.8,"Y");
#gStyle.SetTitleOffset(1.9,"X");
gStyle.SetLineWidth(3)
gStyle.SetFrameLineWidth(2); 

leg = TLegend(0.2, 0.70, 0.89, 0.89)#,NULL,"brNDC");
leg.SetHeader("m_{A}="+mass+" GeV")
leg.SetBorderSize(0)
leg.SetNColumns(2)
leg.SetLineColor(1)
leg.SetLineStyle(1)
leg.SetLineWidth(1)
leg.SetFillColor(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.04)

c = TCanvas("c1", "c1",0,0,500,500)
c.SetBottomMargin(0.15)
#c.SetLogy()
#c.SetLogx()
c.cd()
inputfile={}
inputfilelist = {}
histo={}
histonames = {}
couplist = ['01','04','08','10']
for i in range(0,4):
    inputdir = '/eos/cms/store/group/phys_top/ExtraYukawa/BDT/BDT_output_meng/'+year+'/ttc_'+particle+'_'+coupling+couplist[i]+'_M'+particle.upper()+mass
    inputfilelist[i] = inputdir+'/TMVApp_'+mass+'_'+chan+'.root'
    histonames[i] = 'ttc'+year+'_TAToTTQ_'+coupling+couplist[i]+'_M'+particle.upper()+mass
legendtext=[ 'rtc0.1','rtc0.4','rtc0.8','rtc1.0']
for i in range(len(inputfilelist)):
    print(inputfilelist[i])
    inputfile[i] = TFile(inputfilelist[i])
    histo[i] = inputfile[i].Get(histonames[i])
    histo[i].Rebin(10)
#    histo[i].SetMarkerColor(colors[i])
    histo[i].SetLineColor(colors[i])
    histo[i].SetLineWidth(2)
    if i == 0:
        histo[i].GetXaxis().SetTitle("BDT discriminant")
        histo[i].GetYaxis().SetTitle("N_{evts} (normalized to 1)")
        histo[i].DrawNormalized("HIST C")
    else:
        histo[i].DrawNormalized("HIST SAME C")
    leg.AddEntry(histo[i],legendtext[i],"L")


c.Draw()
pt = TPaveText(0.01,0.92,0.95,0.96,"brNDC")
pt.SetBorderSize(0)
pt.SetTextAlign(12)
pt.SetFillStyle(0)
pt.SetTextFont(42)
pt.SetTextSize(0.046)
#text = pt.AddText(0.12,0.35,"CMS Internal                     36 fb^{-1} (2016) ")
#text = pt.AddText(0.12,0.35,"CMS Internal         ")#            41.5 fb^{-1} (2017) ")
#text = pt.AddText(0.12,0.35,"CMS Internal                     59.6 fb^{-1} (2018) ")
#text = pt.AddText(0.6,0.5,"41.5 fb^{-1} (2017) ")
pt.Draw()
leg.Draw()
c.SaveAs(year+'_'+mass+".png") 
c.SaveAs(year+'_'+mass+".pdf") 
    

#leg.Draw()
