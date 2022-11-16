'''
Step0
Step1
    #python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode datacard2workspace --coupling_value rtu04 --mass_point 800 
    #This would give your the workspace root file of datacards.
Step2    
    #python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode FitDiagnostics --coupling_value rtu04 --mass_point 800 
Step3    
    #python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode preFitPlot --coupling_value rtu04 --mass_point 800 
    #python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode postFitPlot --coupling_value rtu04 --mass_point 800 
Step4    
    #python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode diffNuisances --coupling_value rtu04 --mass_point 800 
Step5    
    #python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode PlotPulls --coupling_value rtu04 --mass_point 800 
Step6    
    #python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode Impact_doInitFit --coupling_value rtu04 --mass_point 800 
Step7    
    #python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode Impact_doFits --coupling_value rtu04 --mass_point 800 
Step8    
    #python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode Plot_Impacts --coupling_value rtu04 --mass_point 800 
'''
import os 
import sys
from Util.General_Tool import CheckDir,CheckFile
import argparse
import time
from Util.Tool_For_SignalExtraction  import CheckAndExec,datacard2workspace,FitDiagnostics,diffNuisances,PlotPulls,Impact_doInitFit,Impact_doFits,Plot_Impacts,postFitPlot,preFitPlot,ResultsCopy
from Util.aux import *


CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)

start = time.time()

channel_choices = ['ee','em','mm','C']
year_choices = ['2016apv','2016postapv','2017','2018','run2']

coupling_value_choices = []

for coupling in ['rtc','rtu','rtt']:
    for value in ['01','04','08','10']:
        coupling_value_choices.append(coupling+value)


mode_choices = ['datacard2workspace','FitDiagnostics','diffNuisances','PlotPulls','Impact_doInitFit','Plot_Impacts','Impact_doFits','postFitPlot','preFitPlot','ResultsCopy']


parser = argparse.ArgumentParser()

parser.add_argument('-y','--year',help='Years of data.',default='2017',choices=year_choices)
parser.add_argument('-c','--channel',help='Years of data.',default='ee',choices=channel_choices)
parser.add_argument('--coupling_value',help='Coupling_values',default='rtu04',choices=coupling_value_choices)
parser.add_argument('--mass_point',help='Mass point of dataset.',type=str)
parser.add_argument('-M','--mode',default='Nothing',choices=mode_choices,help='Mode of the executation')
parser.add_argument('--unblind',action='store_true',help = 'Unblind or not.')
parser.add_argument('--dest',default='./')
parser.add_argument('--expectSignal',action="store_true")
parser.add_argument('--rMin',help='rMin values',default='-20')
parser.add_argument('--rMax',help='rMax values',default='20')
parser.add_argument('--text_y',help='y values of text in pre/post-fit plots',default=800,type=float)
parser.add_argument('--interference',help ='If you want to calculate for interference samples, then activate this option.',action="store_true")

args = parser.parse_args()

'''
if 'rtc' in args.coupling_value:
    signal_process = 'ttc'
elif 'rtu' in args.coupling_value:
    signal_process = 'ttu'
elif 'rtt' in args.coupling_value:
    signal_process = 'ttt'
else:raise ValueError("No such coupling value: {}".format(args.coupling_value))
'''
signal_process = 'ttc'

higgs = 'A'



datacards = 'datacards_{year}_{signal_process}/{signal_process}_{coupling_value}_datacard_{year}_SR_{channel}_{channel}_M{higgs}{mass}.txt'.format(year = args.year,signal_process=signal_process,coupling_value=args.coupling_value,channel=args.channel,higgs=higgs,mass=args.mass_point)

if args.interference:
    higgs += '_interfered_with_S0'
    datacards = './datacards_{year}_ttc/ttc_{coupling_value}_datacard_{year}_SR_{channel}_{channel}_MA{mass}_MS{mass2}.txt'.format(year = args.year, coupling_value=args.coupling_value,channel=args.channel,higgs=higgs,mass=args.mass_point,mass2=str(int(args.mass_point)-50))

settings ={
    'year':args.year,
    'channel':args.channel,
    'coupling_value':args.coupling_value,
    'mass':args.mass_point,
    'mass2':str(int(args.mass_point)-50),
    'higgs':higgs,
    'unblind':args.unblind,
    'expectSignal':args.expectSignal,
    'rMin': args.rMin,
    'rMax': args.rMax,
    'interference' : args.interference
}

if args.mode =='preFitPlot' or args.mode =='postFitPlot':
    settings['text_y'] = float(args.text_y)
elif args.mode=='ResultsCopy':
    settings['dest'] = args.dest

MODE = eval(args.mode) 
CheckAndExec(MODE=MODE,datacards=datacards,settings=settings,mode=args.mode)



    
