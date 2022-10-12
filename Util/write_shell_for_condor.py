import os
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
parser.add_argument('--coupling_value',choices=coupling_value,default='rtc0p4')
parser.add_argument('--mass_point',default='300',type=str,choices=['200','300','350','400','500','600','700','800','900','1000'])
parser.add_argument("--Masses",help='List of masses point. Default list=[200,300,350,400,500,600,700]',default=[200, 300, 350, 400, 500, 600, 700],nargs='+')
parser.add_argument('--higgs',default='A',type=str,choices=['A'])
parser.add_argument('--mode',choices =['Impact','LimitPlot'],default='Impact',type=str)
parser.add_argument('--outputdir',help='You can specify your favoured output folder, otherwise, the results will be saved under your current workspace, i.e., {}'.format(WorkDir),default=os.path.join(WorkDir))
args = parser.parse_args()


#Script_File_path = os.path.join(os.path.join(WorkDir,'scripts'),'shell_script_{}_for_{}_{}.sh'.format(args.mode,args.channel,args.year))
Script_File_path = './scripts/shell_script_{}_for_{}_{}.sh'.format(args.mode,args.channel,args.year) # should be relative -> But I don't understand why.

if os.path.isfile(Script_File_path):
    print('Shell Script-> {} existed!\n'.format(Script_File_path))
    print('rm -f {}\n'.format(Script_File_path))
    os.system('rm -f {}'.format(Script_File_path))
else:pass

f= open(Script_File_path,'w') 

f.write('#!/bin/sh\n')
f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh \n\n')
f.write('WorkDir={}\n\n'.format(WorkDir))
f.write('\ncd $WorkDir\n\n')
f.write('cmsenv\n')
f.write('eval $(scram runtime -sh)\n')

if args.mode =='Impact':
    relative_outputdir = 'SignalExtractionChecks{}_{}_M{}{}_{}'.format(args.year,args.channel,args.higgs,args.mass_point,args.coupling_value) # Same in Raman's code
    abs_outputdir = os.path.join(args.outputdir,relative_outputdir)
    
    if os.path.isdir(args.outputdir):
        Result_Impact = os.path.join(abs_outputdir,'impacts_t0_SignalExtractionChecks{}_{}.pdf'.format(args.year,args.channel))
        if os.path.isfile(Result_Impact):
            f.write("rm -f {}\n".format(Result_Impact))

if args.mode=='Impact':
    f.write('dirname={}\n'.format(relative_outputdir))
    f.write('year={}\n'.format(args.year))
    f.write('channel={}\n'.format(args.channel))
    f.write('datacard=datacards_ttc_{}/ttc_datacard_{}_SR_{}_{}_M{}{}_{}.txt\n'.format(args.year,args.year,args.channel,args.channel,args.higgs,args.mass_point,args.coupling_value))
    f.write('start=$(date +%s)\n')
    f.write('\n\nsh runallchecks.sh $dirname $year $channel $datacard\n')
    f.write('end=$(date +%s)\n')
    f.write('echo "Elapsed Time: $(($end-$start)) seconds"\n')
    f.write('rm -ifr {}/{}\n'.format(args.outputdir,relative_outputdir))
    f.write('mkdir {}/{}\n'.format(args.outputdir,relative_outputdir))
    f.write('mv -r {} {}/{}\n'.format(relative_outputdir,args.outputdir,relative_outputdir))
    f.write('rm -ifr {}\n'.format(relative_outputdir))
elif args.mode=='LimitPlot':
    massess_string = ''
    for mass_point in  args.Masses:
        massess_string += '{} '.format(mass_point)
    ##### Temporary #####

    #coupling_value = args.coupling_value.split('rtc')[-1]
    #####################

    f.write('python runlimits.py -c {} --coupling_value {} -y {} --Masses {} --outputdir {}\n'.format(args.channel,args.coupling_value,args.year,massess_string,args.outputdir))
else:pass
f.close()

print('A new script file is created -> {}\n'.format(Script_File_path))
print('Your {} result(s) will be saved under {}\n'.format(args.mode,args.outputdir))
