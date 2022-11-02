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
from Util.Tool_For_SignalExtraction  import CheckAndExec,datacard2workspace,FitDiagnostics,diffNuisances,PlotPulls,Impact_doInitFit,Impact_doFits,Plot_Impacts,postFitPlot,preFitPlot


CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)

start = time.time()

channel_choices = ['ee','em','mm','C']
year_choices = ['2016apv','2016postapv','2017','2018','run2']

coupling_value_choices = []

for coupling in ['rtc','rtu','rtt']:
    for value in ['01','04','08','10']:
        coupling_value_choices.append(coupling+value)


mode_choices = ['datacard2workspace','FitDiagnostics','diffNuisances','PlotPulls','Impact_doInitFit','Plot_Impacts','Impact_doFits','postFitPlot','preFitPlot']


parser = argparse.ArgumentParser()

parser.add_argument('-y','--year',help='Years of data.',default='2017',choices=year_choices)
parser.add_argument('-c','--channel',help='Years of data.',default='ee',choices=channel_choices)
parser.add_argument('--coupling_value',help='Coupling_values',default='rtu04',choices=coupling_value_choices)
parser.add_argument('--mass_point',help='Mass point of dataset.',type=str)
parser.add_argument('-M','--mode',default='Nothing',choices=mode_choices,help='Mode of the executation')
parser.add_argument('--unblind',action='store_true',help = 'Unblind or not.')
parser.add_argument('--outputdir',default='./')
parser.add_argument('--expectSignal',action="store_true")
args = parser.parse_args()

if 'rtc' in args.coupling_value:
    signal_process = 'ttc'
elif 'rtu' in args.coupling_value:
    signal_process = 'ttu'
elif 'rtt' in args.coupling_value:
    signal_process = 'ttt'
else:raise ValueError("No such coupling value: {}".format(args.coupling_value))
signal_process = 'ttc'

higgs = 'A'

datacards = 'datacards_{year}_{signal_process}/{signal_process}_{coupling_value}_datacard_{year}_SR_{channel}_{channel}_M{higgs}{mass}.txt'.format(year = args.year,signal_process=signal_process,coupling_value=args.coupling_value,channel=args.channel,higgs=higgs,mass=args.mass_point)


settings ={
        'year':args.year,
        'channel':args.channel,
        'coupling_value':args.coupling_value,
        'mass':args.mass_point,
        'higgs':higgs,
        'unblind':args.unblind,
        'expectSignal':args.expectSignal
        }


MODE = eval(args.mode) 
CheckAndExec(MODE=MODE,datacards=datacards,settings=settings,mode=args.mode)



    
