
import os 
import argparse
parser = argparse.ArgumentParser()

parser.add_argument('--shell_script',type=str,default='_default')

args = parser.parse_args()

if args.shell_script=='_default':
    raise ValueError('Please enter your exectuable shell_script path for HTCondor.')

elif not os.path.isfile(args.shell_script):
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

import os
WorkDir = os.popen('pwd').read().split('\n')[0]
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
f.write('+JobFlavour = "tomorrow"\n')
f.write('queue\n')



