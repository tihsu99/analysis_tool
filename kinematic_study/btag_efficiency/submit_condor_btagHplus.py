import os
import optparse
import sys

usage = 'python submit_condor_btagHplus.py -f destination_folder'
parser = optparse.OptionParser(usage)
parser.add_option('-f', '--folder', dest='folder', type=str, default = '', help='Please enter a destination folder')
parser.add_option('-i', '--input', dest='input', type='string', default = '', help="Please enter a txt with the location of input files")
(opt, args) = parser.parse_args()
#Insert here your uid... you can see it typing echo $uid

uid = 0
username = str(os.environ.get('USER'))
inituser = str(os.environ.get('USER')[0])
if username == 'adeiorio':
    uid = 103214

def sub_writer(infile, folder):
    f = open("condor.sub", "w")
    f.write("Proxy_filename          = x509up\n")
    f.write("Proxy_path              = /afs/cern.ch/user/" + inituser + "/" + username + "/private/$(Proxy_filename)\n")
    f.write("universe                = vanilla\n")
    f.write("x509userproxy           = $(Proxy_path)\n")
    f.write("use_x509userproxy       = true\n")
    #f.write("should_transfer_files   = YES\n")
    #f.write("when_to_transfer_output = ON_EXIT\n")
    f.write("transfer_input_files    = $(Proxy_path) \n")
    #f.write("transfer_output_remaps  = \""+ infile + "=root://eosuser.cern.ch//eos/user/"+inituser + "/" + username+"/Hplus/nosynch/" + folder + "/" + infile + " \"\n")
    f.write("+JobFlavour             = \"workday\"\n") # options are espresso = 20 minutes, microcentury = 1 hour, longlunch = 2 hours, workday = 8 hours, tomorrow = 1 day, testmatch = 3 days, nextweek     = 1 week
    f.write("executable              = btageff_producer.py\n")
    f.write("arguments               = " + infile + " " + folder + " " + " remote" + "\n")
    #f.write("input                   = input.txt\n")
    f.write("output                  = condor/output/" + infile.replace(".root", "") + ".out\n")
    f.write("error                   = condor/error/" + infile.replace(".root", "") + ".err\n")
    f.write("log                     = condor/log/" + infile.replace(".root", "") + ".log\n")

    f.write("queue\n")

if not os.path.exists("condor/output"):
    os.makedirs("condor/output")
if not os.path.exists("condor/error"):
    os.makedirs("condor/error")
if not os.path.exists("condor/log"):
    os.makedirs("condor/log")

if(uid == 0):
    print("Please insert your uid")
    exit()
if not os.path.exists("/tmp/x509up_u" + str(uid)):
    os.system('voms-proxy-init --rfc --voms cms -valid 192:00')
os.popen("cp /tmp/x509up_u" + str(uid) + " /afs/cern.ch/user/" + inituser + "/" + username + "/private/x509up")

folder = opt.folder
#Writing the configuration file
f = open(opt.input, "r")
files_list = f.read().splitlines()
print(str(len(files_list)))
for infile in files_list:
    print(infile)
    sub_writer(infile, folder)
    os.system('condor_submit condor.sub')
    #print('condor_submit condor.sub')
