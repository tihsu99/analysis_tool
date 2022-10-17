import os
import sys
import pandas as pd
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)
from Util.Tool_for_write_shell import Write_Shell
WorkDir = os.popen('pwd').read().split('\n')[0]
if not os.path.isdir(os.path.join(WorkDir,'scripts')):
    print('You do not have [folder]: `scripts` under your current workspace: {}'.format(WorkDir))
    os.mkdir(os.path.join(WorkDir,'scripts'))
    print('`scripts` is created under your workspace')
else:pass

coupling_value = []

for coupling in ['rtc','rtu','rtt']:
    for value in ['01','04','08','10']:
        coupling_value.append(coupling+value)


import sys
import argparse


parser = argparse.ArgumentParser()

parser.add_argument('--channel',choices =['mm','ee','em','C'],default='C',type=str)
parser.add_argument('--year',choices =['2016apv','2016postapv','2017','2018','run2'],default='run2',type=str)
parser.add_argument('--coupling_value',choices=coupling_value,default='rtc04')
parser.add_argument("--Masses",help='List of masses point. Default list=[200,300,350,400,500,600,700]',nargs='+',default='default')
parser.add_argument("--mass_point",default='300')
parser.add_argument('--higgs',default='A',type=str,choices=['A'])
parser.add_argument('--task',choices =['Impact','LimitPlot'],default='Impact',type=str)
parser.add_argument('--outputdir',help='You can specify your favoured output folder, otherwise, the results will be saved under your current workspace, i.e., {}'.format(WorkDir),default=os.path.join(WorkDir))
parser.add_argument('--Job_bus_Name',type=str,default='__default__')
args = parser.parse_args()


#Script_File_path = os.path.join(os.path.join(WorkDir,'scripts'),'shell_script_{}_for_{}_{}.sh'.format(args.mode,args.channel,args.year))

if args.Job_bus_Name=='__default__':
    Write_Shell(WorkDir=WorkDir,channel=args.channel,mode=args.task,higgs=args.higgs,year=args.year,mass_point=args.mass_point,coupling_value=args.coupling_value,outputdir=args.outputdir,Masses=args.Masses)
else:
    #data = pd.read_csv(args.Job_bus_file,sep=",",header)
    df = pd.read_csv(args.Job_bus_Name,sep=',')
    nrow = len(df.index)

    for i_row in range(nrow):
        Write_Shell(WorkDir=WorkDir,channel=str(df.iloc[i_row]['Channel']),mode=str(df.iloc[i_row]['Task']),higgs=str(df.iloc[i_row]['PID']),year=str(df.iloc[i_row]['Year']),mass_point=str(df.iloc[i_row]['Mass_point']),coupling_value=str(df.iloc[i_row]['Coupling_value']),outputdir=str(df.iloc[i_row]['outputdir']))
    
    #print(data.loc[0,["Task"]])



