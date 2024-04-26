import os
import argparse
import sys
sys.path.insert(1, '../../python')
from common import inputFile_path


def sub_writer(era, infile, outpath) :
    f = open("condor.sub", "w")
    f.write("Proxy_path              = " + os.getenv("X509_USER_PROXY") + "\n")
    f.write("universe                = vanilla\n")
    f.write("x509userproxy           = $(Proxy_path)\n")
    f.write("use_x509userproxy       = true\n")
    f.write("transfer_input_files    = $(Proxy_path), datamodel.py, treeReaderArrayTools.py \n")
    f.write("+JobFlavour             = \"workday\"\n") # options are espresso = 20 minutes, microcentury = 1 hour, longlunch = 2 hours, workday = 8 hours, tomorrow = 1 day, testmatch = 3 days, nextweek     = 1 week
    f.write("executable              = btageff_producer.py\n")
    f.write("arguments               = -i " + infile + " -o  " + outpath + " -e " + era + "\n")
    f.write("output                  = condor/output/" + infile.rsplit("/",1)[1].replace(".root", "") + ".out\n")
    f.write("error                   = condor/error/" + infile.rsplit("/",1)[1].replace(".root", "") + ".err\n")
    f.write("log                     = condor/log/" + infile.rsplit("/",1)[1].replace(".root", "") + ".log\n")

    f.write("queue\n")

if not os.path.exists("condor/output"):
    os.makedirs("condor/output")
if not os.path.exists("condor/error"):
    os.makedirs("condor/error")
if not os.path.exists("condor/log"):
    os.makedirs("condor/log")

if __name__ == "__main__":
  usage  = 'usage: %prog [options]'
  parser = argparse.ArgumentParser(description=usage)
  parser.add_argument('-e', '--era',    dest='era', help='[2016apv/2016postapv/2017/2018]', default='2018', type=str)
  parser.add_argument('-o', '--outdir', dest='out', help='ouput directory', default='./', type=str)
  parser.add_argument('-r', '--run', dest='run', help='local or condor', default='local', type=str)
  parser.add_argument("--test", action="store_true")

  args = parser.parse_args()

  outfolder = args.out
  if not os.path.exists(outfolder):
      os.makedirs(outfolder)
  era = args.era
  path    = str(inputFile_path[era])
  #print(path)
  files_list = [os.path.join(path, f) for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and f.startswith("TT") and f.endswith(".root"))]
  #print(str(len(files_list)))
  #print(files_list)
  for infile in files_list:
    print(infile)
    if args.run == "local":
        os.popen("python btageff_producer.py -i " + infile + " -o " + outfolder + " -e " + era)
        break
    elif args.run == "condor":
        if 'eos' in infile and 'root://eosuser.cern.ch//' not in infile:
            infile = 'root://eosuser.cern.ch//' + infile
        sub_writer(era, infile, outfolder)
        if not args.test:
            print ("Submitting Jobs on Condor")
            os.system('condor_submit condor.sub')
