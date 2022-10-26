
import os 
import argparse
import pandas as pd 
parser = argparse.ArgumentParser()

parser.add_argument('--shell_script',type=str,default='__default__')

parser.add_argument('--Job_bus_Name',type=str,default='__default__')
parser.add_argument('--JobFlavour',type=str,default='nextweek',choices=['workday','tomorrow','testmatch','espresso','microcentury','longlunch','nextweek'])

args = parser.parse_args()
import os
WorkDir = os.popen('pwd').read().split('\n')[0]

if args.shell_script=='__default__' and args.Job_bus_Name=='__default__':
    raise ValueError('Please enter your exectuable shell_script path/Job bus for HTCondor.')

elif args.Job_bus_Name=='__default__':

    if not os.path.isfile(args.shell_script):
        raise ValueError('Make sure {} is existed'.format(args.shell_script))

    else:pass



    if os.path.isfile('scripts/condor.sub'):
        print('scripts/condor.sub is already existed. Will overwrite a new scripts/condor.sub.')
        os.system('rm -f scripts/condor.sub')

    else:pass

    for condor_message_dir in ['log','err','output']:
        if os.path.isdir(condor_message_dir):pass
        else:
            os.system('mkdir {}'.format(condor_message_dir))

    f = open('scripts/condor.sub','w')

    f.write('executable = {}\n'.format(args.shell_script))
    #f.write('Universe = vanilla\n')
    f.write('output =./output/$(ClusterId).$(ProcId).out\n')
    f.write('error = ./err/$(ClusterId).$(ProcId).out\n')
    f.write('log = ./log/$(ClusterId).$(ProcId).log\n')
    #f.write('should_transfer_files = YES\n')
    f.write('initialdir= {} \n'.format(WorkDir))
    f.write('when_to_transfer_output = ON_EXIT\n')
    f.write('request_cpus   = 10\n')
    f.write('+JobFlavour = "{}"\n'.format(args.JobFlavour))
    f.write('queue\n')

elif args.shell_script=='__default__':

    for condor_message_dir in ['log','err','output']:
        if os.path.isdir(condor_message_dir):pass
        else:
            os.system('mkdir {}'.format(condor_message_dir))
    df = pd.read_csv(args.Job_bus_Name,sep=',') 
    nrow = len(df.index)
    print(df)
    if os.path.isfile('scripts/condor.sub'):
        print('scripts/condor.sub is already existed. Will overwrite a new scripts/condor.sub.')
        os.system('rm -f scripts/condor.sub')

    else:pass
    f = open('scripts/condor.sub','w')


    for i_row in range(nrow):
        mode =str(df.iloc[i_row]['Task']) 
        channel = str(df.iloc[i_row]['Channel'])
        year = str(df.iloc[i_row]['Year'])
        higgs = str(df.iloc[i_row]['PID'])
        mass_point = str(df.iloc[i_row]['Mass_point'])
        coupling_value = str(df.iloc[i_row]['Coupling_value'])
        sample_type    = str(df.iloc[i_row]['sample_type']) 
        
        if sample_type == "interference":
          shell_script =  './scripts/shell_script_{}_for_{}_{}_M{}{}_{}_interference.sh'.format(mode,channel,year,higgs,mass_point,coupling_value)
        else:
          shell_script = './scripts/shell_script_{}_for_{}_{}_M{}{}_{}.sh'.format(mode,channel,year,higgs,mass_point,coupling_value) # should be relative -> But I don't understand why.
        
        f.write('executable = {}\n'.format(shell_script))
        #f.write('Universe = parallel\n')
        f.write('output =./output/$(ClusterId).$(ProcId).out\n')
        f.write('error = ./err/$(ClusterId).$(ProcId).out\n')
        f.write('log = ./log/$(ClusterId).$(ProcId).log\n')
        f.write('should_transfer_files = YES\n')
        f.write('initialdir= {} \n'.format(WorkDir))
        f.write('when_to_transfer_output = ON_EXIT\n')
        f.write('request_cpus   = 10\n')
        f.write('+JobFlavour = "{}"\n'.format(args.JobFlavour))
        f.write('queue\n\n')
    print('file -> : scripts/condor.sub is created.')
    f.close() 



else:raise ValueError('')
