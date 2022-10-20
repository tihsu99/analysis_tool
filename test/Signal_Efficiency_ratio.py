import os
import sys
CURRENT_WORKDIR =  os.getcwd()
import sys
sys.path.append(CURRENT_WORKDIR)
from Util.General_Tool import CheckFile
import ROOT
from array import array
import pandas as pd
from ROOT.TColor import *




### Setting for input files
InputFolder = '/eos/cms/store/group/phys_top/ExtraYukawa/BDT/BDT_output/with_scale_unc/2018/'
subFolder_Format = 'ttc_a_rtc{}_MA{}' # coupling, mass_points
FileNames_Format = 'TMVApp_{}_{}.root' #Mass,channel
###
### Setting for parameters
coupling_values = ['01','04','08','10']
#coupling_values = ['01']
mass_points = [200,300,350,400,500,600,700]
channels = ['ee','em','mm']
###

points = len(mass_points)
x_mass = array('d',mass_points)
df = pd.read_fwf('./ttc_cross_sections.txt')
print(df[(df.rhotu==0.0) & (df.rhott==0.0) & (df.PID=='a0')])

df_a0_rtc = df[(df.rhotu==0.0) & (df.rhott==0.0) & (df.PID=='a0')]


Eff = dict()

for channel in channels:
    Eff[channel] = dict()
    
    for coupling_value in coupling_values:
        Eff[channel][coupling_value] = array('d')
        for mass_point in mass_points:
            
            File_path = os.path.join(InputFolder,subFolder_Format.format(coupling_value,mass_point))
            condor_outputpath= os.path.join(File_path,'condor_output')
            File_path = os.path.join(File_path,FileNames_Format.format(mass_point,channel))
            if CheckFile(File_to_check=File_path,quiet=True):pass
            else: raise ValueError("{} doesn't exist!".format(File_path))
            xs = float(df_a0_rtc[(df.rhotc==float(coupling_value)*0.1) & (df.Mass==int(mass_point))].cross_section)
            out = os.popen('cat {} | grep xs:{}'.format(condor_outputpath,xs)).read()

            TotalNumberInNtuple = int(out.split('xs:{}'.format(xs))[1].split(', eff_N:')[1].split('\n')[0])
            F = ROOT.TFile(File_path,"read")
            Signal = F.Get("ttc2018_TAToTTQ_rtc{}_MA{}".format(coupling_value,mass_point))
            NumberofEventsInBDT = Signal.Integral()

            Signal_Efficiency = NumberofEventsInBDT/TotalNumberInNtuple

            Eff[channel][coupling_value].append(Signal_Efficiency)


for channel in channels:
    c = ROOT.TCanvas("c","c",600,600)

    graph = dict()
    mg = ROOT.TMultiGraph()
    leg = ROOT.TLegend(.1,.2,.1,.2)
    leg.SetMargin(0.4)
    leg.SetBorderSize(0);
    leg.SetFillColor(0);
    leg.SetTextFont(42);
    leg.SetTextSize(0.03);
    c= ROOT.TCanvas()
    c.cd()
    c.Clear()
    colors = [3,4,5,6]
    c.SetLogy()

    minimum =1
    for idx,coupling_value in enumerate(coupling_values):
        print('coupling_value: {} , {}'.format(coupling_value,Eff[channel][coupling_value]))
        for value in Eff[channel][coupling_value]:
            if minimum > value:
                minimum = value
        
        g = ROOT.TGraph(points,x_mass,Eff[channel][coupling_value])
        g.SetTitle(channel+'_'+coupling_value)    
        g.SetMarkerStyle(21+idx);
        g.SetLineColor(colors[idx])
        mg.Add(g)
        leg.AddEntry(g, "#rho_{tc}=%s"%(coupling_value),"L")

    mg.SetTitle("Signal Efficiency;Mass[GeV];Signal Efficiency")
    mg.Draw("ALP");
    leg.Draw("same")

    c.Update()
    c.SaveAs("./test/{}_signal_efficiency.png".format(channel))
    c.Close()
    del c


