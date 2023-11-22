from ROOT import *
from array import array
import os 
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-y','--year',help='Years of data.',default='2018')
parser.add_argument('--coupling1',default='rtc0p4')
parser.add_argument('--coupling2',default='rtc0p1')
parser.add_argument('--channel',default='mm')


args = parser.parse_args()
channel = args.channel


year = args.year
coupling1 = args.coupling1
coupling2 = args.coupling2





File_deno = 'bin/limits_ttc{}_{}_{}_asimov_extYukawa.txt'.format(year,channel,coupling1)
File_nomi = 'bin/limits_ttc{}_{}_{}_asimov_extYukawa.txt'.format(year,channel,coupling2)


with open(File_nomi,'r') as f:
    nomi_lines = f.readlines()
with open(File_deno,'r') as f:
    deno_lines = f.readlines()


nomi = nomi_lines[0].rstrip().split(' ')
deno = deno_lines[0].rstrip().split(' ')

outputdir = '/eos/user/z/zhenggan/www/run2/{}'.format(year)

root_outputdir = '/afs/cern.ch/user/z/zhenggan/public/ExtraYukawa/ttc/Limit_Ratio'

print('Limit ratio for rtc0p1/rtc0p4 for {}: '.format(channel))

c = TCanvas("c","c",600,600)

x = array('d')
y = array('d')

for n_masspoints in range(len(nomi_lines)): 
    
    mass = float(nomi_lines[n_masspoints].rstrip().split(' ')[1])
    
    ratio = float(nomi_lines[n_masspoints].rstrip().split(' ')[4])/float(deno_lines[n_masspoints].rstrip().split(' ')[4])

    

    x.append(mass)
    y.append(ratio)


g = TGraph(len(nomi_lines),x,y)
g.SetTitle("Limit Ratio of {}/{} for {} channel in {}".format(coupling2,coupling1,channel,year))
g.GetXaxis().SetTitle("Mass[GeV]")
g.SetName("LimitRatio")
g.Draw("AC*")
rootfiles = os.path.join(root_outputdir,'LimitRatio_{}to{}_{}_{}.root'.format(coupling2,coupling1,year,channel))

f = TFile(rootfiles,'RECREATE')
f.cd()
g.Write()

f.Close()

c.Update()
c.SaveAs(os.path.join(outputdir,"LimitRatio_{}to{}_{}_{}.pdf".format(coupling2,coupling1,year,channel)))
c.Close()
