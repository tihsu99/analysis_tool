import os 
import sys
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)
import argparse
import string
import random
from Util.General_Tool import CheckDir, CheckFile
parser = argparse.ArgumentParser()
coupling_value = []
for coupling in ['rtc','rtu','rtt']:
    for value in ['01','04','08','10']:
        coupling_value.append(coupling+value)

parser.add_argument('-i','--Job_bus_Name',type=str,default='__Default__',help='Specify the Job_bus name.')
parser.add_argument('--mode',type=str,default='r',choices=['write','append','read','reset'],help='mode to operate one Job_bus file.')
parser.add_argument('--reset_file',action="store_true",help='reset Job_bus file.')
parser.add_argument('--output_dir',default='./',help='reset Job_bus file.')
parser.add_argument('--task',type=str,default='LimitPlot',choices=['LimitPlot','Impact'],help='Task of the job.')
parser.add_argument('--channel',choices =['mm','ee','em','C'],default='C',type=str,help='channel of the job.')
parser.add_argument('--year',choices =['2016apv','2016postapv','2017','2018','run2'],default='run2',type=str,help='year of job.')
parser.add_argument('--coupling_value',choices=coupling_value,default='rtc04',help='coupling value')
parser.add_argument('--mass_point',default='300',type=str,help='mass point')
parser.add_argument("--Masses",help='List of masses point. Default list=[200,300,350,400,500,600,700]',default=[200, 300, 350, 400, 500, 600, 700],nargs='+')
parser.add_argument('--higgs',default='A',type=str,choices=['A'],help='Higgs.')
parser.add_argument('--interference',action='store_true',help='use interference sample')
parser.add_argument('--unblind',action='store_true',help='for limit unbliding')

'''
python ./Util/prepareJobs.py --mode write 
python ./Util/prepareJobs.py -i [Job_bus filename] --mode append --task LimitPlot --mass_point 200 --channel C --coupling_value rtc04 --higgs A
python ./Util/prepareJobs.py --mode --read -i [Job_bus filename]
python ./Util/prepareJobs.py --mode --reset -i [Job_bus filename]
'''
args = parser.parse_args()

if args.mode=='reset':
    
    Job_bus_name = args.Job_bus_Name
    if CheckFile(Job_bus_name,False):
        f = open(Job_bus_name,'w')
        f.write("Task,Mass_point,Coupling_value,PID,Channel,Year,sample_type,outputdir\n")
        print("Reset file -> {}".format(Job_bus_name))
        f.close()
    else:pass
else:
    if args.Job_bus_Name=='__Default__':
        
        Job_bus_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
        CheckDir('Job_bus',True)
        Job_bus_name = os.path.join('Job_bus',Job_bus_name+'.txt')

    else:
        
        #Job_bus_name = os.path.join('Job_bus',args.Job_bus_Name+'.txt')
        Job_bus_name = args.Job_bus_Name
        CheckFile(Job_bus_name,False,quiet=True)
    
    if args.mode=='write':
        if CheckFile(Job_bus_name,quiet=True):raise ValueError("\n\nFile exists! -> {} .\nIf you want to reset the file, please use --mode reset. And if you want to append another job into this bus file, please use --mode append. ".format(Job_bus_name))
        with open(Job_bus_name,'w') as f:
            f.write("Task,Mass_point,Coupling_value,PID,Channel,Year,sample_type,outputdir,unblind\n")

        print("You Job_bus file with name -> "+Job_bus_name+" is created.")
        print("Use [--mode append] and [--Job_bus_Name filename] to append the following task.")
    elif args.mode == 'append':
        if args.interference:
          sample_type = "interference"
        else:
          sample_type = "pure"
        with open(Job_bus_name,'a') as f:
            f.write("{},{},{},{},{},{},{},{},{}\n".format(args.task,args.mass_point,args.coupling_value,args.higgs,args.channel,args.year,sample_type,str(args.unblind),args.output_dir))
        print("Sequence -> {},{},{},{},{},{},{},{},{} written into {}\n".format(args.task,args.mass_point,args.coupling_value,args.higgs,args.channel,args.year,sample_type,args.output_dir,str(args.unblind),Job_bus_name))


    elif args.mode=='read':
        print("Open file -> {}".format(Job_bus_name))
        with open(Job_bus_name,'r') as f:
            for line in f.readlines():
                print(line)




