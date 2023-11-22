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
from Util.Tool_For_SignalExtraction  import CheckAndExec,datacard2workspace,FitDiagnostics,diffNuisances,PlotPulls,Impact_doInitFit,Impact_doFits,Plot_Impacts, PlotShape,ResultsCopy, SubmitFromEOS, DrawNLL, plotCorrelationRanking, SubmitGOF, GoFPlot, FinalYieldComputation 
from Util.aux import *
from collections import OrderedDict

CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)

start = time.time()

year_choices = ['2016apv','2016postapv','2017','2018','run2']


mode_choices = ['datacard2workspace','FitDiagnostics','diffNuisances','PlotPulls','Impact_doInitFit','Plot_Impacts','Impact_doFits','PlotShape','ResultsCopy','SubmitFromEOS','DrawNLL', 'plotCorrelationRanking', 'SubmitGOF', 'GoFPlot', 'FinalYieldComputation']


parser = argparse.ArgumentParser()

parser.add_argument('-y','--year',help='Years of data.',default='2017',choices=year_choices)
parser.add_argument('-r','--region', help='Region of data', default='SR')
parser.add_argument('-c','--channel',help='Years of data.',default='ee')
parser.add_argument('--rtc', help='rtc value', default=0.4, type=float)
parser.add_argument('--rtt', help='rtt value', default=0.6, type=float)
parser.add_argument('--mass_point',help='Mass point of dataset.',type=str)
parser.add_argument('-M','--mode',default='Nothing',choices=mode_choices,help='Mode of the executation')
parser.add_argument('--unblind',action='store_true',help = 'Unblind or not.')
parser.add_argument('--dest',default='./')
parser.add_argument('--expectSignal',action="store_true")
parser.add_argument('--rMin',help='rMin values',default='-20')
parser.add_argument('--rMax',help='rMax values',default='20')
parser.add_argument('--text_y',help='y values of text in pre/post-fit plots',default=800,type=float)
parser.add_argument('--logy',help='log y in pre/post-fit plots',action='store_true')
parser.add_argument('--cminDefaultMinimizerStrategy', help='cminDefaultMinimizerStrategy: default = 0', default=0,type=int)
parser.add_argument('--cminDefaultMinimizerTolerance', help= 'default = 1.0', default=1.0, type=float)
parser.add_argument('--outdir', help='output directory', default='./', type=str)
parser.add_argument('--prefix', help='output directory', default=None, type=str)
parser.add_argument('--plotRatio', help='plot data/MC ratio in pre/post-fit plots', action="store_true")
parser.add_argument('--GoF_Algorithm', help='Goodness of Test Algorithms', choices = ['KS', 'AD', 'saturated'], default='saturated')
parser.add_argument('--correlation', help='Save correlation matrix in FigDiagnostics root file', action="store_true")
parser.add_argument('--saveNormalizations', help = 'option: --saveNormalizations', action = "store_true")
parser.add_argument('--shape_type', help = 'preFit/postFit', choices = ['preFit', 'postFit'], type = str, default = None)
parser.add_argument('--group', type = int, default = 0)
parser.add_argument('--paper', help = 'used paper style', action = "store_true")
parser.add_argument('--datacard_dir', help = 'datacard directory', default='datacards_test', type=str)
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
####### Analysis dependent bin ########
signal_process = 'bH'
higgs = 'H'
signal_param = OrderedDict()
signal_param["rtt"] = str(args.rtt).replace('.','p')
signal_param["rtc"] = str(args.rtc).replace('.','p')
signal_name_template = "CGToBHpm_a_MASS_rtt{}_rtc{}".format(signal_param["rtt"].replace('p',''), signal_param["rtc"].replace('p',''))
signal_name_template = signal_name_template.replace('MASS', args.mass_point)
datacards = "{dc_dir}/{year}/{signal}/{signal}_{year}_{region}_{channel}.txt".format(dc_dir=args.datacard_dir, year=args.year, signal=signal_name_template, region=args.region, channel=args.channel).replace('MASS', args.mass_point)
coupling_name = "rtt{}_rtc{}".format(signal_param["rtt"], signal_param["rtc"])
x_variable = 'HT'
#######################################

settings ={
    'year':args.year,
    'region':args.region,
    'channel':args.channel,
    'coupling_value': coupling_name,
    'mass':args.mass_point,
    'higgs':higgs,
    'unblind':args.unblind,
    'expectSignal':args.expectSignal,
    'rMin': args.rMin,
    'rMax': args.rMax,
    'cminDefaultMinimizerTolerance': str(args.cminDefaultMinimizerTolerance),
    'cminDefaultMinimizerStrategy': str(args.cminDefaultMinimizerStrategy),
    'outdir': args.outdir,
    'prefix': args.prefix,
    'GoF_Algorithm': args.GoF_Algorithm,
    'correlation': args.correlation,
    'saveNormalizations': args.saveNormalizations,
    'shape_type': args.shape_type,
    'paper': args.paper,
    'group': args.group,
    'signal_name': signal_name_template,
    'POI': x_variable,
    'datacard_dir': '/'.join(datacards.split('/')[:-1]),
    'datacard_name': datacards.split('/')[-1]
}

if args.mode =='PlotShape':
    settings['text_y'] = float(args.text_y)
    settings['logy'] = args.logy
    settings['plotRatio'] = ((args.plotRatio))
elif args.mode=='ResultsCopy':
    settings['dest'] = args.dest

MODE = eval(args.mode) 
CheckAndExec(MODE=MODE,datacards=datacards,settings=settings,mode=args.mode)

    
