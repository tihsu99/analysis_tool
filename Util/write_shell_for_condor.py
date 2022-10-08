import os
WorkDir = os.popen('pwd').read().split('\n')[0]

if not os.path.isdir(os.path.join(WorkDir,'scripts')):
    print('You do not have [folder]: `scripts` under your current workspace: {}'.format(WorkDir))
    os.mkdir(os.path.join(WorkDir,'scripts'))
    print('`scripts` is created under your workspace')
else:pass

coupling_value = []

for coupling in ['rtc','rtu','rtt']:
    for value in ['0p1','0p4','0p8','1p0']:
        coupling_value.append(coupling+value)


import sys
import argparse


parser = argparse.ArgumentParser()

parser.add_argument('--channel',choices =['mm','ee','em','C'],default='C',type=str)
parser.add_argument('--year',choices =['2016apv','2016postapv','2017','2018','run2'],default='run2',type=str)
parser.add_argument('--coupling_value',choices=coupling_value,default='rtc0p4')
parser.add_argument('--mass_point',default='300',type=str,choices=['200','300','350','400','500','600','700','800','900','1000'])
parser.add_argument('--higgs',default='A',type=str,choices=['A'])
parser.add_argument('--mode',choices =['Impact','LimitPlot'],default='Impact',type=str)
parser.add_argument('--outputdir',help='You can specify your favoured output folder, otherwise, the results will be saved under your current workspace, i.e., {}'.format(WorkDir),default=os.path.join(WorkDir))
args = parser.parse_args()


Script_File_path = os.path.join(os.path.join(WorkDir,'scripts'),'shell_script_{}_for_{}_{}.sh'.format(args.mode,args.channel,args.year))


if os.path.isfile(Script_File_path):
    print('Shell Script-> {} existed!\n'.format(Script_File_path))
    print('rm -f {}\n'.format(Script_File_path))
    os.system('rm -f {}'.format(Script_File_path))
else:pass


f= open(Script_File_path,'w') 
f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh \n\n')
f.write('\ncd $WorkSpace\n\n')
f.write('eval $(scram runtime -sh)')

datacards = 'datacards_ttc_{}/ttc_datacard_{}_SR_{}_{}_M{}{}_{}.txt'.format(args.year,args.year,args.channel,args.channel,args.higgs,args.mass_point,args.coupling_value)

if args.mode=='Impact':
    f.write('\n\nsource runallchecks.sh {} {} {} {}'.format(args.outputdir,args.year,args.channel,datacards))

else:pass

print('File Create -> '+Script_File_path)
