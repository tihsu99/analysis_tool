import argparse
import ROOT
import os 
import sys
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)
from collections import OrderedDict
import numpy as np
from array import array
parser = argparse.ArgumentParser()
channel_choices=['C','ee','em','mm']
year_choices=['2016apv','2016postapv','2017','2018','run2']

couplingvalue_choices = []
for coupling in ['rtc','rtu','rtt']:
    for value in ['0p1','0p4','0p8','1p0']:
        couplingvalue_choices.append(coupling+value)


parser.add_argument('-y','--year',help='year',default='run2', choices=year_choices)
parser.add_argument('-c','--channel',help='channel',default='C',choices=channel_choices)
parser.add_argument('--coupling_values',help='coupling value [rtc0p4/rtu0p4/...]',default=['rtc0p1','rtc0p4','rtc1p0'], nargs='+')

parser.add_argument("--plot_y_max",help='Plot Only',default=1000,type=float)
parser.add_argument("--plot_y_min",help='Plot Only',default=0.1,type=float)

parser.add_argument("--First_dir", help='First directory for comparison',default='./')
parser.add_argument("--Second_dir",help='Second directory for comparison', default='./') 
parser.add_argument("--First_label", default='Approval')
parser.add_argument("--Second_label", default='New algo')

parser.add_argument("--interference", action="store_true")
parser.add_argument("--paper", action="store_true")
parser.add_argument("--AN", action="store_true")

args = parser.parse_args()


color = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen-2]
#./bin/2018/C/limits_ttc_rtu0p8_asimov_extYukawa.txt

year = args.year
channel = args.channel
coupling_values = args.coupling_values
First_limit = dict()
Second_limit = dict()
First_exp = dict()
Second_exp = dict()
ratio = dict()
Masses = []

for coupling_value in coupling_values:
  First_limit[coupling_value] = os.path.join(args.First_dir, 'bin/{year}/{channel}/limits_ttc_{coupling_value}_asimov_extYukawa.root'.format(year=year,channel=channel,coupling_value=coupling_value))
  Second_limit[coupling_value] = os.path.join(args.Second_dir, 'bin/{year}/{channel}/limits_ttc_{coupling_value}_asimov_extYukawa.root'.format(year=year,channel=channel,coupling_value=coupling_value))

  if args.interference:
    First_limit[coupling_value] = First_limit[coupling_value].replace(".root","_interference.root")
    Second_limit[coupling_value] = Second_limit[coupling_value].replace(".root", "_interference.root")
 
  First_File_per_coupling_value = ROOT.TFile(First_limit[coupling_value],'READ')
  Second_File_per_coupling_value = ROOT.TFile(Second_limit[coupling_value],'READ')

  First_exp[coupling_value] = First_File_per_coupling_value.Get('expmed')
  Second_exp[coupling_value] = Second_File_per_coupling_value.Get('expmed')

  nbins = First_exp[coupling_value].GetN()
  ratio_ = []
  for i in range(nbins):
    ratio_.append(Second_exp[coupling_value].GetY()[i]/First_exp[coupling_value].GetY()[i])
  ratio[coupling_value] = ratio_

for i in range(nbins):
  Masses.append(Second_exp[coupling_values[0]].GetX()[i])

c = ROOT.TCanvas()
c.SetTopMargin(0.085)
c.SetLeftMargin(0.12)

pad1 = ROOT.TPad('pad1','',0.00, 0.22, 0.99, 0.99)
pad2 = ROOT.TPad('pad2','',0.00, 0.00, 0.99, 0.22)
pad1.SetBottomMargin(0.01);
pad1.SetTicks(1,1)
pad2.SetTopMargin(0.035);
pad2.SetBottomMargin(0.45);
pad2.SetTicks(1,1)
pad1.Draw()
pad2.Draw()


pad2.cd()
ratio_TGraph = dict()

mg2 = ROOT.TMultiGraph("mg2",'mg2')
mg2.SetTitle(";m_{A} [GeV];new/approv.")
for idx, coupling_value in enumerate(coupling_values):
  ratio_TGraph[coupling_value] = ROOT.TGraph(nbins, array('d', Masses), array('d', ratio[coupling_value]))
  ratio_TGraph[coupling_value].SetLineStyle(2)
  ratio_TGraph[coupling_value].SetLineWidth(2)
  ratio_TGraph[coupling_value].SetLineColor(color[idx])
  mg2.Add(ratio_TGraph[coupling_value],'L')
mg2.GetYaxis().SetNdivisions(4)
mg2.GetYaxis().SetTitleOffset(0.3)
mg2.GetYaxis().SetTitleSize(0.14)
mg2.GetYaxis().SetLabelSize(0.1)
mg2.GetXaxis().SetTitleSize(0.14)
mg2.GetXaxis().SetLabelSize(0.1)
mg2.GetYaxis().SetLimits(0.75,1.25)
mg2.Draw('same')

pad1.cd()

leg = ROOT.TLegend(.15, .60, .40, .85);
leg.SetBorderSize(0);
leg.SetFillColorAlpha(0,0.0);
leg.SetShadowColor(0);
leg.SetTextFont(42);
leg.SetTextSize(0.03)

pad1.SetLogy()
mg =ROOT.TMultiGraph("mg","mg")
mg.SetTitle(";m_{A} [GeV];95% CL upper limit on #mu=#sigma/#sigma_{theory}")
for idx, coupling_value in enumerate(coupling_values):

  if 'rtc' in coupling_value :
    value = coupling_value.split('rtc')[-1]
    value = int(value.replace('p',''))*0.1
    prefix = '#rho_{tc} = %.1f'%(value)
    coupling_type = 'rtc'
  elif 'rtu' in coupling_value :
    value = coupling_value.split('rtu')[-1]
    value = int(value.replace('p',''))*0.1
    prefix = '#rho_{tu} = %.1f'%(value)
    coupling_type = 'rtu'
  Limit_Name = prefix

  First_exp[coupling_value].SetLineWidth(2)
  First_exp[coupling_value].SetLineColor(color[idx])
  mg.Add(First_exp[coupling_value],"L")
  leg.AddEntry(First_exp[coupling_value], Limit_Name + " Expected (approv.)",'L')
  Second_exp[coupling_value].SetLineStyle(2)
  Second_exp[coupling_value].SetLineWidth(2)
  Second_exp[coupling_value].SetLineColor(color[idx])
  leg.AddEntry(Second_exp[coupling_value], Limit_Name + " Expected (new.)",'L')
  mg.Add(Second_exp[coupling_value],"L")
mg.SetMinimum(args.plot_y_min);
mg.SetMaximum(args.plot_y_max);
#mg.GetYaxis().SetLimits(0.1, 1000)
mg.Draw('same')
leg.Draw('same')
pad1.Update()
import CMS_lumi
CMS_lumi.writeExtraText = 1
if args.paper:
   CMS_lumi.extraText = ""
   CMS_lumi.relPosY = 0.045
   CMS_lumi.relPosX = 0.06
else:
   CMS_lumi.extraText = "Preliminary"
   CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
   iPos = 11
   if( iPos==0 ): CMS_lumi.relPosX = 0.12
   iPeriod=year

   CMS_lumi.CMS_lumi(pad1, iPeriod, iPos, 0.09)
c.Update()

#line = ROOT.TLine(pad1.GetUxmin(),1.0,pad1.GetUxmax(),1.0);
#line.SetLineColor(ROOT.kRed)
#line.SetLineWidth(2)
#line.Draw('same ')

interference_text = 'pure'
if args.interference:
  interference_text = 'interference'
os.system('mkdir -p plot')
c.SaveAs('plot/comparison_limit_%s_%s_%s_%s.png'%(year,channel,coupling_type, interference_text))
c.SaveAs('plot/comparison_limit_%s_%s_%s_%s.pdf'%(year,channel,coupling_type, interference_text))


