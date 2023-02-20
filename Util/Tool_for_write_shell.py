import os 
from General_Tool import CheckFile
import sys
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)

def Write_Shell(WorkDir,channel,mode,higgs,year,mass_point,coupling_value,sample_type,outputdir,Masses=-1,unblind = False):
    if unblind:
        unblind_post_fix = "unblind"
    else:
        unblind_post_fix = "blind"
    if Masses!=-1:
        Script_File_path = './scripts/shell_script_{}_for_{}_{}_{}.sh'.format(mode,channel,year,unblind_post_fix) # should be relative -> But I don't understand why.
    else:
        Script_File_path = './scripts/shell_script_{}_for_{}_{}_M{}{}_{}_{}.sh'.format(mode,channel,year,higgs,mass_point,coupling_value,unblind_post_fix) # should be relative -> But I don't understand why.

    if sample_type == "interference":
      Script_File_path = Script_File_path.replace(".sh","_interference.sh")

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
        f.write("datacard={}".format(datacard_location)+'\n')
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
        if "rtc" in coupling_value:
            signal_process_name = "ttc"
        elif "rtu" in coupling_value:
            signal_process_name = "ttu"
        elif "rtt" in coupling_value:
            signal_process_name = "ttt"
        else:raise ValueError("No such channel: {}".format(signal_process_name))
        signal_process_name = "ttc"
        
        
        #datacards_run2_ttu/ttu_rtu04_datacard_run2_SR_em_em_MA200.txt
        if sample_type == "interference":
          datacard_location = 'datacards_{year}_{sig}/{sig}_{cp_value}_datacard_{year}_SR_{channel}_{channel}_MA{Mass}_MS{Mass_S}.txt'.format(year=year,sig=signal_process_name,channel=channel,Mass = mass_point,Mass_S = str(int(mass_point)-50),cp_value = coupling_value)
        else:
          datacard_location = 'datacards_{year}_{sig}/{sig}_{cp_value}_datacard_{year}_SR_{channel}_{channel}_M{H}{Mass}.txt'.format(year=year,sig=signal_process_name,channel=channel,H=higgs,Mass = mass_point,cp_value = coupling_value)
        if not CheckFile(datacard_location,False,True): raise ValueError('\nMake sure {} exists. Please prepare this datacards\n'.format(datacard_location))
        if unblind:
            unblind_command = "--unblind"
        else:
            unblind_command = ""

        if sample_type == "interference":
          f.write('python runlimits.py -c {} --coupling_value {} -y {} --Masses {} --interference --reset_outputfiles {}\n'.format(channel,coupling_value,year,massess_string,unblind_command))
        else:
          f.write('python runlimits.py -c {} --coupling_value {} -y {} --Masses {} --reset_outputfiles {}\n'.format(channel,coupling_value,year,massess_string,unblind_command))
    else:pass
    f.close()

    print('A new script file is created -> {}\n'.format(Script_File_path))


