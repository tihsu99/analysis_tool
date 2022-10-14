import os 
from General_Tool import CheckFile
import sys
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)

def Write_Shell(WorkDir,channel,mode,higgs,year,mass_point,coupling_value,outputdir,Masses=-1):
    if Masses!=-1:
        Script_File_path = './scripts/shell_script_{}_for_{}_{}.sh'.format(mode,channel,year) # should be relative -> But I don't understand why.
    else:
        Script_File_path = './scripts/shell_script_{}_for_{}_{}_M{}{}_{}.sh'.format(mode,channel,year,higgs,mass_point,coupling_value) # should be relative -> But I don't understand why.

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

    if mode =='Impact':
        relative_outputdir = 'SignalExtractionChecks{}_{}_M{}{}_{}'.format(year,channel,higgs,mass_point,coupling_value) # Same in Raman's code
        abs_outputdir = os.path.join(outputdir,relative_outputdir)
        
        if os.path.isdir(outputdir):
            Result_Impact = os.path.join(abs_outputdir,'impacts_t0_SignalExtractionChecks{}_{}.pdf'.format(year,channel))
            if os.path.isfile(Result_Impact):
                f.write("rm -f {}\n".format(Result_Impact))

        print('Your {} result(s) will be saved under {}\n'.format(mode,outputdir))
    if mode=='Impact':
        f.write('dirname={}\n'.format(relative_outputdir))
        f.write('year={}\n'.format(year))
        f.write('channel={}\n'.format(channel))
        datacard_location = 'datacards_ttc_{}/ttc_datacard_{}_SR_{}_{}_M{}{}_{}.txt'.format(year,year,channel,channel,higgs,mass_point,coupling_value)
        if not CheckFile(datacard_location,False,True): raise ValueError('\nMake sure {} exists. Please prepare this datacards\n'.format(datacard_location))
        f.write(datacard_location+'\n')
        f.write('start=$(date +%s)\n')
        f.write('\n\nsh runallchecks.sh $dirname $year $channel $datacard\n')
        f.write('end=$(date +%s)\n')
        f.write('echo "Elapsed Time: $(($end-$start)) seconds"\n')
        f.write('rm -ifr {}/{}\n'.format(outputdir,relative_outputdir))
        f.write('mkdir {}/{}\n'.format(outputdir,relative_outputdir))
        f.write('cp  {}/* {}/{}\n'.format(relative_outputdir,outputdir,relative_outputdir))
        f.write('rm -ifr {}\n'.format(relative_outputdir))
    elif mode=='LimitPlot':
        massess_string = ''
        if  Masses == -1:
            massess_string = mass_point
        else: 
            for m_point in  Masses:
                massess_string += '{}'.format(m_point)
        
        ##### Temporary #####

        #coupling_value = coupling_value.split('rtc')[-1]
        #####################
        datacard_location = 'datacards_ttc_{}/ttc_datacard_{}_SR_{}_{}_M{}{}_{}.txt'.format(year,year,channel,channel,higgs,mass_point,coupling_value)
        if not CheckFile(datacard_location,False,True): raise ValueError('\nMake sure {} exists. Please prepare this datacards\n'.format(datacard_location))

        f.write('python runlimits.py -c {} --coupling_value {} -y {} --Masses {} --reset_outputfiles\n'.format(channel,coupling_value,year,massess_string))
    else:pass
    f.close()

    print('A new script file is created -> {}\n'.format(Script_File_path))


