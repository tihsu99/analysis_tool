import os 
import json
import sys
CURRENT_WORKDIR = os.getcwd()

from Util.General_Tool import CheckDir,CheckFile


def Integrate_LimitPlots(args):
    #Specific
    """
    Wanted: ./plots/limit_comparison_Merged_Limit_Plots_For_run2_rtc04_interference.pdf
    
    usage: python Results_Integrate.py --mode LimitPlots --limit_original_dir [InputFolder] (no include [merged/plots_limit]) 
    """
    
    if CheckDir(args.limit_original_dir,False):pass
    else:
        print('You should provide the input folder format like: [your/personal/limitsplots/folder]/merged/plots_limit ')
    
    if args.coupling =='rtu':
        Final_FolderOUT = "ttu_merged"
    elif args.coupling=='rtc':
        Final_FolderOUT = "ttc_merged"
    else:
        raise ValueError('No such coupling yet: {coupling}'.format(coupling=coupling))
    CheckDir(Final_FolderOUT,True)

    subFolderIN = 'merged'
    if args.interference:
        subFolderIN+= '_interference'
    
    if args.interference:
        Final_FolderOUT = os.path.join(Final_FolderOUT,"Interference")
    else:
        Final_FolderOUT = os.path.join(Final_FolderOUT,"Pure")
    
    CheckDir(Final_FolderOUT,True)

     
    for root,dirs,files in os.walk("{limit_original_dir}/{subFolderIN}/plots_limit".format(limit_original_dir=args.limit_original_dir,subFolderIN=subFolderIN),topdown=False):
        #print(root)
        AN_Folder = Final_FolderOUT
        for name in files:
            if '.pdf' in name:
                original_files = os.path.join(root,name)
                name = name
                AN_Filename = os.path.join(AN_Folder,name)
                CheckFile(AN_Filename,True,True)
                print('cp {original_files} {AN_Filename} \n'.format(original_files= original_files,AN_Filename=AN_Filename))
                os.system('cp {original_files} {AN_Filename}'.format(original_files= original_files,AN_Filename=AN_Filename))


def SearchSpecific(args):
    
    Target = 'SignalExtraction'
    coupling_value = (args.coupling_value).replace('p','')
    for subfolder in [args.year,args.channel,coupling_value]:
        Target = os.path.join(Target,subfolder)
    if args.interference:
        Target = os.path.join(Target,'A_interfered_with_S0')
    else:
        Target = os.path.join(Target,'A')
    
    Target = os.path.join(Target,args.mass)
    if args.IncludeSignal:
        Target = os.path.join(Target,'s_plus_b')
    else:
        Target = os.path.join(Target,'b_only')

    Target = os.path.join(Target,'results')
    
    if not CheckDir(Target,False,False):
        raise ValueError('No such results: {Target}'.format(Target=Target))
    
    Targets = []
    for root , dirs , files in os.walk(Target,topdown=False):
        for name in files:
            if not '.pdf' in name: continue
            Targets.append(os.path.join(root,name))
    
    return Targets


def SearchAll(Original_Folder='SignalExtraction'):
     
    Targets = []
        
    for root , dirs , files in os.walk(Original_Folder,topdown=False):
        if not 'results' in root: continue
        for name in files:
            if not '.pdf' in name: continue
            Targets.append(os.path.join(root,name))
                                    
    return Targets



def Integrate_SignalExtraction(args):
    #Specific\
    '''
    python Results_Integrate.py --WalkAll --mode SignalExtraction
    python Results_Integrate.py --mode SignalExtraction --year 2018 --channel ee --mass 350 --coupling_value rtu0p4  
    
    '''
    Main_Folder = 'Impacts_Plots'
    CheckDir(Main_Folder,True)
    
    if args.WalkAll:
        OriginalInputs = SearchAll()
    else:
        OriginalInputs = SearchSpecific(args)
    
    for Input in OriginalInputs:
        '''
        SignalExtraction/2018/C/rtu04/A_interfered_with_S0/350/s_plus_b/results/diffNuisances_2018_C_A_interfered_with_S0_350_rtu04_8_.pdf
        '''
        elements = Input.split('/')
        
        subFolders = elements[1:4]
        
        Folder_Out = Main_Folder 
        CheckDir(Folder_Out,True,True)
        for subFolder in subFolders:
            Folder_Out = os.path.join(Folder_Out,subFolder)
            CheckDir(Folder_Out,True,True)
        
        if 'diffNuisances' in Input: 
            FileName = elements[8]
        else:
            FileName = '{0}_{1}_{2}_{3}'.format(elements[4],elements[5],elements[6],elements[8])
    
        FileName = os.path.join(Folder_Out,FileName)
        
        CheckFile(FileName,True,True)

        os.system('cp {Input} {FileName}'.format(FileName=FileName,Input=Input))
    
    print('Please check the new folder: {}'.format(Main_Folder))

def Integrate_LimitTables(args):
    '''
    #Input Dir: bin/2018/ee/limits_ttc_rtu1p0_asimov_extYukawa_interference.txt
    usage
    python Results_Integrate.py --mode LimitTables --year 2016apv --channel ee --coupling_value rtu0p1 
    '''
    FileIn = 'bin/{year}/{channel}/limits_ttc_{coupling_value}_asimov_extYukawa.txt'.format(year=args.year,channel=args.channel,coupling_value=args.coupling_value)
    
    if args.interference:
        FileIn = FileIn.replace('.txt','_interference.txt')
    
    if not CheckFile(FileIn,False,True):
        raise ValueError("Please check whether you have the file: {FileIn}, if not, please plot the limits first.".format(FileIn=FileIn))
    
    CheckDir('LimitsTables',True)
    TableName = os.path.join('LimitsTables',str(args.year))
    CheckDir(TableName,True)
    TableName = os.path.join(TableName,str(args.channel)) 
    CheckDir(TableName,True)
    TableName = os.path.join(TableName,str(args.coupling_value)+'.tex')
    WriteTableForAN(args=args,FileIn=FileIn,TableName=TableName)    
    



def WriteTableForAN(args,FileIn='',TableName=''):
    
    
    FileIn = open(FileIn,'r')
    records = FileIn.readlines()
    LimitTable = open(TableName,'w')
    
    if 'rtu' in args.coupling_value:
        value = (args.coupling_value.split('rtu')[-1]).replace('p','.')
        coupling_term = r'$\rho_{{tu}} = {value}$'.format(value=value)
    if 'rtc' in args.coupling_value:
        value = (args.coupling_value.split('rtc')[-1]).replace('p','.')
        coupling_term = r'$\rho_{{tc}} = {value}$'.format(value=value)

    LimitTable.write(r'\begin{table}[h!]'+'\n')
    LimitTable.write(r'\begin{center}'+'\n')
    
    if args.channel == 'C':
        channel = 'Combined channel'
    elif args.channel == 'ee':
        channel = 'double-electron channel'
    elif args.channel == 'mm':
        channel = 'double-muon channel'
    elif args.channel == 'em':
        channel = 'electron-muon channel'


    if not args.interference:
        LimitTable.write(r'\caption{{Table of limit values for {year} data in {channel} with coupling value {coupling_term}}}'.format(year=args.year,channel=channel,coupling_term=coupling_term)+'\n')
    else:
        LimitTable.write(r'\caption{{Table of limit values for year{year} in {channel}  with coupling value {coupling_term} for $A^0-H^0$ interference}}'.format(year=args.year,channel=channel,coupling_term=coupling_term)+'\n')

    if not args.interference:
        LimitTable.write(r'\label{{tab:Limits_{coupling_value}_{channel}_{year}}}'.format(coupling_value=args.coupling_value,channel=args.channel,year=args.year)+'\n')
    else:
        LimitTable.write(r'\label{{tab:Limits_{coupling_value}_{channel}_{year}_interference}}'.format(coupling_value=args.coupling_value,channel=args.channel,year=args.year)+'\n')
    LimitTable.write(r'\begin{tabular}'+'{|c|c|c|c|c|c|}\n')
    LimitTable.write(r'\hline'+'\n')
    LimitTable.write(r'Mass Point [GeV] ($m_{A^0}$) & limits at $-2\sigma$ & limits at $-1\sigma$ & limits (median) & limits at $1\sigma$ & limits at $2\sigma$ \\'+'\n') 
    
    for record in records:
        record = record.split(' ')
        record = record[1:-1]
        record = ' & '.join(record)
        record += r'\\'+'\n'
        LimitTable.write(record)         

    LimitTable.write(r'\hline'+'\n')
    LimitTable.write(r'\end{tabular}'+'\n')
    LimitTable.write(r'\end{center}'+'\n')
    LimitTable.write(r'\end{table}'+'\n')


    FileIn.close()
    LimitTable.close()









