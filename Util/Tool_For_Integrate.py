import os 
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
CURRENT_WORKDIR = os.getcwd()

from Util.General_Tool import CheckDir,CheckFile

def smart_round(x,n):
  return str(Decimal(x).quantize(Decimal("0."+"0"*n),rounding=ROUND_HALF_UP))

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




def Integrate_SignalExtraction(args):
    '''
    Main function to integrate signal extraction results
    '''
    Store_Folders = WalkAndStoreAsList(storedir = args.storedir, mainFolder='SignalExtraction')
    for Folder in Store_Folders : 
        print('\nFolder which is checking currently: {Folder}'.format(Folder=Folder))
        Info = GetInformation(storedir = args.storedir, Folder = Folder)
        CopyTheResults(Info)
        WriteLatex(Info)

def WalkAndStoreAsList(storedir = '', mainFolder=''):
    
    Store_Folders = list()
    for root, _,_ in os.walk(os.path.join(storedir, mainFolder),topdown=True):
        if (len(root.split('/'))-len(storedir.split('/'))) != 7: continue
        Store_Folders.append(root)

    return Store_Folders


def GetInformation(storedir = '', Folder=''):

    Folder = Folder.replace(storedir,'')
    while Folder[0] == '/':
      Folder = Folder[1:]
    elements = Folder.split('/')
    year = elements[1]
    channel = elements[2]
    coupling = elements[3]
    higgs = elements[4]
    mA = elements[5]
    b_only_ornot = elements[6]
    
    result_folder = os.path.join(storedir, Folder,'results')
    
    #/SignalExtraction/run2/C/rtu04/A/350/s_plus_b/results
    #./SignalExtraction/run2/C/rtu04/A_interfered_with_S0/350/b_only/results/diffNuisances_run2_C_A_interfered_with_S0_350_rtu04_69_.pdf
    #./SignalExtraction/run2/C/rtu04/A_interfered_with_S0/350/b_only/results/impacts_t0_run2_C_MA_interfered_with_S0350_rtu04.pdf

    filenames = ['preFit_{channel}_log.pdf'.format(channel=channel),'postFit_{channel}_log.pdf'.format(channel=channel),'diffNuisances_{year}_{channel}_{higgs}_{mA}_{coupling}_1_.pdf'.format(channel=channel,year=year,higgs=higgs,mA=mA,coupling=coupling),'diffNuisances_{year}_{channel}_{higgs}_{mA}_{coupling}_2_.pdf'.format(channel=channel,year=year,higgs=higgs,mA=mA,coupling=coupling),'impacts_t0_{year}_{channel}_M{higgs}{mA}_{coupling}.pdf'.format(channel=channel,year=year,higgs=higgs,mA=mA,coupling=coupling)]
    
    Categorys = ['preFit','postFit','pull','impact']
    
    Info = dict()
    Info['year'] = year
    Info['channel'] = channel
    Info['coupling'] = coupling
    Info['higgs'] = higgs
    Info['mH'] = mA
    Info['b_only_ornot'] = b_only_ornot
    Info['Category'] = dict()
    for Category in Categorys:
        Info['Category'][Category] = dict()
        Info['Category'][Category]['Filenames'] = []
        Info['Category'][Category]['Exist'] = False
        Info['Category'][Category]['FinalFolder'] = ''

    for idx,filename in enumerate(filenames):
        filename = os.path.join(result_folder,filename)
        if CheckFile(filename,False,False):
            if 'preFit' in filename:
                Info['Category']['preFit']['Exist'] = True
                Info['Category']['preFit']['Filenames'].append(filename)
                Info['Category']['preFit']['FinalFolder'] = 'plots/preFit/{year}/{channel}/{coupling}/{higgs}/{mA}/{b_only_ornot}'.format(year=year,channel=channel,coupling=coupling,higgs=higgs,mA=mA,b_only_ornot=b_only_ornot)
            elif 'postFit' in filename:
                Info['Category']['postFit']['Exist'] = True
                Info['Category']['postFit']['Filenames'].append(filename)
                Info['Category']['postFit']['FinalFolder'] = 'plots/postFit/{year}/{channel}/{coupling}/{higgs}/{mA}/{b_only_ornot}'.format(year=year,channel=channel,coupling=coupling,higgs=higgs,mA=mA,b_only_ornot=b_only_ornot)
            elif 'diffNuisances' in filename:
                Info['Category']['pull']['Exist'] = True
                Info['Category']['pull']['Filenames'].append(filename)
                Info['Category']['pull']['FinalFolder'] = 'plots/pull/{year}/{channel}/{coupling}/{higgs}/{mA}/{b_only_ornot}'.format(year=year,channel=channel,coupling=coupling,higgs=higgs,mA=mA,b_only_ornot=b_only_ornot)
            elif 'impacts' in filename:
                Info['Category']['impact']['Exist'] = True
                Info['Category']['impact']['Filenames'].append(filename)
                Info['Category']['impact']['FinalFolder'] = 'plots/impact/{year}/{channel}/{coupling}/{higgs}/{mA}/{b_only_ornot}'.format(year=year,channel=channel,coupling=coupling,higgs=higgs,mA=mA,b_only_ornot=b_only_ornot)
        else:
            if idx == 0:
                print('Warning -> Folder: {result_folder} do not have preFit plot.'.format(result_folder=result_folder))
            elif idx == 1:
                print('Warning -> Folder: {result_folder} do not have postFit plot.'.format(result_folder=result_folder))
            elif idx == 2 or idx == 3 :
                print('Warning -> Folder: {result_folder} do not have diffNuisances plot.'.format(result_folder=result_folder))
            elif idx == 2 or idx == 3 :
                print('Warning -> Folder: {result_folder} do not have diffNuisances plot.'.format(result_folder=result_folder))
            else:
                print('Warning -> Folder: {result_folder} do not have impact plots.'.format(result_folder=result_folder))
    return Info

def CopyTheResults(Info=dict()):

    for category in Info['Category'].keys():
        if Info['Category'][category]['Exist']:
            CheckDir(Info['Category'][category]['FinalFolder'],True,False)
            for filename in Info['Category'][category]['Filenames']:
                os.system('cp {filename} {folder}'.format(filename=filename,folder=Info['Category'][category]['FinalFolder'])) 
                if category == 'impact':
                    filename = filename.split('/')[-1]
                    filename = os.path.join(Info['Category'][category]['FinalFolder'],filename)
                    filename_multiple  = filename.replace('.pdf','_%d.pdf')
                    os.system('pdfseparate  {filename} {filename_multiple}'.format(filename=filename,filename_multiple=filename_multiple))


def WriteLatex(Info=dict()):

    for category in Info['Category'].keys():
        if Info['Category'][category]['Exist']:
            if category == 'postFit':continue
            tex_Folder = Info['Category'][category]['FinalFolder'].replace('plots/','sub_tex/')
            CheckDir(tex_Folder,True,False)
            latex = open(os.path.join(tex_Folder,'Fig.tex'),'w')
            if Info['year'] == 'run2':
                year = 'the full Run 2'
            else:
                year = 'full {year}'.format(year=Info['year'])
            if Info['channel'] == 'ee':
                channel = 'the $\Pe\Pe$ channel'
            elif Info['channel'] == 'em':
                channel = 'the $\Pe\PGm$ channel'
            elif Info['channel'] == 'mm':
                channel = 'the $\PGm\PGm$ channel'
            else:
                channel = 'all channels'
            if Info['higgs'] == 'A':
                interfered_postfix = ''
            else:
                interfered_postfix = ' with $\PA-\PH$ interference'
            
            if Info['b_only_ornot'] == 'b_only':
                unblind_postfix = 'background-only Asimov fit'
            elif Info['b_only_ornot'] == 'Unblind':
                unblind_postfix = 'unblind result'
            else:
                unblind_postfix = 'signal + background Asimov fit'


            if 'rtu' in Info['coupling']:
                value = int(Info['coupling'].split('rtu')[-1])*0.1
                coupling = r'$\rho_{tu}'+'={value}$'.format(value=value)
            elif 'rtc' in Info['coupling']:
                value = int(Info['coupling'].split('rtc')[-1].replace('p','.'))*0.1
                coupling = r'$\rho_{tc}'+'={value}$'.format(value=value)
            
            latex.write(r'\begin{figure}[!h]'+'\n')
            latex.write(r'\centering'+'\n')
            if category == 'impact':
                latex.write(r'\includegraphics[width=0.82475\textwidth]{{{Folder}/impacts_t0_{year}_{channel}_M{higgs}{mH}_{coupling}_1.pdf}}'.format(Folder=Info['Category'][category]['FinalFolder'],year=Info['year'],channel=Info['channel'],higgs=Info['higgs'],mH=Info['mH'],coupling=Info['coupling'])+'\n')
                latex.write(r'\includegraphics[width=0.82475\textwidth]{{{Folder}/impacts_t0_{year}_{channel}_M{higgs}{mH}_{coupling}_2.pdf}}'.format(Folder=Info['Category'][category]['FinalFolder'],year=Info['year'],channel=Info['channel'],higgs=Info['higgs'],mH=Info['mH'],coupling=Info['coupling'])+'\n')
                latex.write(r'\caption{{Impact distribution of the nuisance parameters for {unblind_postfix} of {year} dataset in {channel} with \mA={mH}\GeV and {coupling} {interfered_postfix} (pages 1 and 2).}}'.format(year=year,channel=channel,coupling=coupling,interfered_postfix=interfered_postfix,mH=Info['mH'],unblind_postfix=unblind_postfix)+'\n')
                latex.write(r'\label{{fig:asimov_impact_{year}_{channel}_{coupling}_{b_only_ornot}_{higgs}_{mH}}}'.format(year=Info['year'],channel=Info['channel'],higgs=Info['higgs'],mH=Info['mH'],coupling=Info['coupling'],b_only_ornot=Info['b_only_ornot'])+'\n')

            elif category =='preFit':
                Folder = Info['Category'][category]['FinalFolder']
                latex.write(r'\includegraphics[width=0.45\textwidth]{{{Folder}/preFit_{channel}_log.pdf}}'.format(Folder=Folder,channel=Info['channel'])+'\n')
                Folder = Folder.replace('preFit','postFit')
                latex.write(r'\includegraphics[width=0.45\textwidth]{{{Folder}/postFit_{channel}_log.pdf}}'.format(Folder=Folder,channel=Info['channel'])+'\n')
                latex.write(r'\caption{{Pre-fit(left) and  post-fit(right) BDT variable with {year} data for the {unblind_postfix} for {coupling} in {channel} for \mA={mH}\GeV {interfered_postfix}}}'.format(year=year,channel=channel,coupling=coupling,interfered_postfix=interfered_postfix,mH=Info['mH'],unblind_postfix=unblind_postfix) +'\n') 

                latex.write(r'\label{{fig:prefit_{year}_{channel}_{coupling}_{b_only_ornot}_{higgs}_{mH}}}'.format(year=Info['year'],channel=Info['channel'],higgs=Info['higgs'],mH=Info['mH'],coupling=Info['coupling'],b_only_ornot=Info['b_only_ornot'])+'\n')
            elif category =='pull':
                latex.write(r'\includegraphics[width=0.73\textwidth]{{{Folder}/diffNuisances_{year}_{channel}_{higgs}_{mH}_{coupling}_1_.pdf}}'.format(Folder=Info['Category'][category]['FinalFolder'],year=Info['year'],channel=Info['channel'],higgs=Info['higgs'],mH=Info['mH'],coupling=Info['coupling'])+'\n')
                latex.write(r'\includegraphics[width=0.73\textwidth]{{{Folder}/diffNuisances_{year}_{channel}_{higgs}_{mH}_{coupling}_2_.pdf}}'.format(Folder=Info['Category'][category]['FinalFolder'],year=Info['year'],channel=Info['channel'],higgs=Info['higgs'],mH=Info['mH'],coupling=Info['coupling'])+'\n')
                latex.write('\caption{{Pulls for each of the nuisance parameters for the {unblind_postfix} of {year} dataset for {coupling} in {channel} for \mA={mH}\GeV {interfered_postfix}.}}'.format(year=year,channel=channel,coupling=coupling,interfered_postfix=interfered_postfix,mH=Info['mH'],unblind_postfix=unblind_postfix)+'\n')
                latex.write(r'\label{{fig:asimov_pull_{year}_{channel}_{coupling}_{b_only_ornot}_{higgs}_{mH}}}'.format(year=Info['year'],channel=Info['channel'],higgs=Info['higgs'],mH=Info['mH'],coupling=Info['coupling'],b_only_ornot=Info['b_only_ornot'])+'\n')

            latex.write(r'\end{figure}'+'\n')

            latex.close()


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
    ''' Will be updated later
    if args.unblind:
        FileIn = FileIn.replace('.txt','_unblind.txt')
    '''
    CheckDir('LimitsTables',True)
    TableName = os.path.join('LimitsTables',str(args.year))
    CheckDir(TableName,True)
    TableName = os.path.join(TableName,str(args.channel)) 
    CheckDir(TableName,True)
    TableName = os.path.join(TableName,str(args.coupling_value)+'.tex')
    if(args.interference):
      TableName = TableName.replace('.tex','_interference.tex')
    if args.unblind:
      TableName = TableName.replace('.tex','_unblind.tex')

    WriteTableForAN(args=args,FileIn=FileIn,TableName=TableName)    
    



def WriteTableForAN(args,FileIn='',TableName=''):
    
    
    FileIn = open(FileIn,'r')
    records = FileIn.readlines()
    LimitTable = open(TableName,'w')
    
    if 'rtu' in args.coupling_value:
        value = int((args.coupling_value.split('rtu')[-1]).replace('p','.'))*0.1
        coupling_term = r'$\rho_{{tu}} = {value}$'.format(value=value)
    if 'rtc' in args.coupling_value:
        value = (args.coupling_value.split('rtc')[-1]).replace('p','.')
        coupling_term = r'$\rho_{{tc}} = {value}$'.format(value=value)

    LimitTable.write(r'\begin{table}[h!]'+'\n')
    LimitTable.write(r'\begin{center}'+'\n')
    
    if args.channel == 'C':
        channel = 'the combined channel'
    elif args.channel == 'ee':
        channel = '\Pe\Pe channel'
    elif args.channel == 'mm':
        channel = '\PGm\PGm channel'
    elif args.channel == 'em':
        channel = '\Pe\PGm channel'
    
    if args.unblind:
        unblind_postfix = ' unblinding '
    else:
        unblind_postfix = ''
    
    if not args.interference:
        LimitTable.write(r'\caption{{Table of limit values for {year}{unblind_postfix}data in {channel} with coupling value {coupling_term}}}'.format(year=args.year,channel=channel,coupling_term=coupling_term, unblind_postfix=unblind_postfix)+'\n')
    else:
        LimitTable.write(r'\caption{{Table of limit values for {year}{unblind_postfix}data in {channel}  with coupling value {coupling_term} for $\PA-\PH$ interference}}'.format(year=args.year,channel=channel,coupling_term=coupling_term,unblind_postfix=unblind_postfix)+'\n')
    
    if args.unblind:
        unblind_postfix = 'Unblinding'
    else:
        unblind_postfix = ''
    if not args.interference:
        LimitTable.write(r'\label{{tab:{unblind_postfix}Limits_{coupling_value}_{channel}_{year}}}'.format(coupling_value=args.coupling_value,channel=args.channel,year=args.year,unblind_postfix=unblind_postfix)+'\n')
    else:
        LimitTable.write(r'\label{{tab:{unblind_postfix}Limits_{coupling_value}_{channel}_{year}_interference}}'.format(coupling_value=args.coupling_value,channel=args.channel,year=args.year,unblind_postfix=unblind_postfix)+'\n')
    if args.unblind:
        LimitTable.write(r'\begin{tabular}'+'{|c|c|c|c|c|c|c|}\n')
    else:
        LimitTable.write(r'\begin{tabular}'+'{|c|c|c|c|c|c|}\n')
    LimitTable.write(r'\hline'+'\n')
    if args.unblind:
        LimitTable.write(r'Mass Point [GeV] (\mA) & exp-limit ($-2\sigma$) & exp-limit ($-1\sigma$) & exp-limit (median) & exp-limit ($1\sigma$) & exp-limit ($2\sigma$) & obs-limit \\'+'\n')
    else:
        LimitTable.write(r'Mass Point [GeV] (\mA) & exp-limit ($-2\sigma$) & exp-limit ($-1\sigma$) & exp-limit (median) & exp-limit ($1\sigma$) & exp-limit ($2\sigma$) \\'+'\n')
    
    for record in records:
        record = record.split(' ')
        record = record[1:]
        record = [smart_round(float(i),3) for i in record]
        record[0] = str(int(float(record[0])))
        record = ' & '.join(record)
        record += r'\\'+'\n'
        LimitTable.write(record)         

    LimitTable.write(r'\hline'+'\n')
    LimitTable.write(r'\end{tabular}'+'\n')
    LimitTable.write(r'\end{center}'+'\n')
    LimitTable.write(r'\end{table}'+'\n')


    FileIn.close()
    LimitTable.close()









