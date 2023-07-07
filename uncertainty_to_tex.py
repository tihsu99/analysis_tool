#usage: python3 ./uncertainty_to_tex.py --year run2 -c C --coupling_value rtc04 --mass_point 200 --group 3
import json
import argparse 

year_choices = ['run2']
channel_choices = ['C']
coupling_value_choices = ['rtu04', 'rtc04']

parser = argparse.ArgumentParser()
parser.add_argument('-y','--year',help='Years of data.',default='2017',choices=year_choices)
parser.add_argument('-c','--channel',help='Years of data.',default='ee',choices=channel_choices)
parser.add_argument('--coupling_value',help='Coupling_values',default='rtu04',choices=coupling_value_choices)
parser.add_argument('--mass_point',help='Mass point of dataset.',type=str)
parser.add_argument('--group', type = int, default = 0)
parser.add_argument('--interference', action = "store_true")
parser.add_argument('--paper', action = "store_true")
args = parser.parse_args()

Higgs = 'A'
postfix = 'pure'
if args.coupling_value == 'rtc04':
    coupling = 'tc'
else:
    coupling = 'tu'

if args.interference:
    Higgs += '_interfered_with_S0'
    postfix = 'interference'

if not args.paper :

    with open('SignalExtraction/{year}/{channel}/{coupling}/{Higgs}/{mass}/Unblind/uncertainty-{year}-{channel}-mH{mass}-{postfix}-Set{group}.json'.format(year = args.year, channel = args.channel, coupling = args.coupling_value, Higgs = Higgs, postfix = postfix, group = args.group, mass = args.mass_point)) as f:
        
        Table = json.load(f)
    nCol = len(Table.keys())  

    Latex_Lines = list()
    Latex_Lines.append(r'\begin{table}[!htpb]') 
    Latex_Lines.append(r'\begin{center}')
    Latex_Lines.append(r'\centering')
    Latex_Lines.append(r'\begin{tabular}{|' + 'l|' * nCol + '}')
    Latex_Lines.append(r'\hline')

    Groups = ['Category', '']
    Unc = r'Unc (\%)'
    Group_Name = [''] 
    for Group in Table.keys():
        if 'Experimental' in Group:
            Groups[1] = 'Exp.'
            Group_Name[0] = Group
        elif 'Modeling_Rest' in Group:
            Groups.append('Modeling')
            Group_Name.append(Group)
        elif ' Stat.' in Group or 'TotalUnc' in Group:
            continue
        elif 'BackgroundModeling' in Group:
            Group_Name.append(Group)
            Groups.append('Bkg\_Modeling')
        elif 'SignalModeling' in Group:
            Group_Name.append(Group)
            Groups.append('Sig\_Modeling')
        else:
            Group_Name.append(Group)
            Groups.append(Group)
    Groups.append(' Stat.')
    Group_Name.append(' Stat.')

    for Group in Group_Name:
        if 'TotalUnc' in Group:continue
        TotalUnc = max(Table['TotalUnc']['Up'], Table['TotalUnc']['Dn']) 
        Unct = max(Table[Group]['Up'],Table[Group]['Dn'])
        Value = Unct/TotalUnc
        Unc += ' & ' + str(int(round(Value, 2) * 100))
        
    Unc += r'\\'
    
    GroupsLine = '& '.join(Groups)
    GroupsLine = GroupsLine.replace('_', ' ')
    Latex_Lines.append(GroupsLine + r'\\')
    Latex_Lines.append(r'\hline')
    Latex_Lines.append(Unc)
    Latex_Lines.append(r'\hline')
    Latex_Lines.append(r'\end{tabular}')

    caption = r'Uncertainty table for $\mA = {mass} \GeV$ with $\rho_{{{coupling}}} = 0.4$ ({postfix}) corresponding to $S_{{{group}}}$. The value in each cell is the ratio of the corresponding uncertainty to total uncertainty in percentage.'.format(mass = args.mass_point, coupling = coupling, group = args.group, postfix = postfix)
    Latex_Lines.append(r'\caption{' + caption + '}')
    Latex_Lines.append(r'\label{{tab:unc-breakdown_mH{mass}_{coupling}_{postfix}_group{group}}}'.format(mass = args.mass_point, coupling = args.coupling_value, postfix = postfix, group = args.group))   
    Latex_Lines.append(r'\end{center}')
    Latex_Lines.append(r'\end{table}')

    with open('uncertainty-breakdown_{coupling}_mH{mass}_{year}_{channel}_{postfix}_Set{group}.tex'.format(mass = args.mass_point, year = args.year, channel = args.channel, postfix = postfix, group = args.group, coupling = args.coupling_value), 'w') as f:
        for Line in Latex_Lines:
            f.write(Line + '\n')


else:
    Latex_Lines = []
    
    table_pure = dict() 
    for coupling in ['rtc04', 'rtu04']:
        table_pure[coupling] = dict()
        for mass in ['200', '1000']:
            table_pure[coupling][mass] = dict()
            for set in ['1', '2']:
                with open('SignalExtraction/run2/C/{coupling}/A/{mass}/Unblind/uncertainty-run2-C-mH{mass}-pure-Set{set}.json'.format(coupling = coupling, mass = mass, set = set )) as f:
                
                    table_pure[coupling][mass][int(set)] = json.load(f)
                
    table_interference = dict() 
    for coupling in ['rtc04', 'rtu04']:
        table_interference[coupling] = dict()
        for mass in ['250', '1000']:
            table_interference[coupling][mass] = dict()
            for set in ['1', '2']:
                with open('SignalExtraction/run2/C/{coupling}/A_interfered_with_S0/{mass}/Unblind/uncertainty-run2-C-mH{mass}-interference-Set{set}.json'.format(coupling = coupling, mass = mass, set = set )) as f:
                
                    table_interference[coupling][mass][int(set)] = json.load(f)
     
    TotalUnc_rtu_pure_200 = max(table_pure['rtu04']['200'][1]['TotalUnc']['Dn'],  table_pure['rtu04']['200'][1]['TotalUnc']['Up'])
    
    Stat_rtu_pure_200 = int(round(max(table_pure['rtu04']['200'][1][' Stat.']['Dn'],  table_pure['rtu04']['200'][1][' Stat.']['Up'])/TotalUnc_rtu_pure_200, 2) * 100)
    
    Total_SignalModeling_rtu_pure_200 = int(round(max(table_pure['rtu04']['200'][1]['Total_SignalModeling']['Dn'],  table_pure['rtu04']['200'][1]['Total_SignalModeling']['Up'])/TotalUnc_rtu_pure_200, 2) * 100)
    
    Total_BackgroundModeling_rtu_pure_200 = int(round(max(table_pure['rtu04']['200'][1]['Total_BackgroundModeling']['Dn'],  table_pure['rtu04']['200'][1]['Total_BackgroundModeling']['Up'])/TotalUnc_rtu_pure_200, 2) * 100)
    
    Total_Experimental_rtu_pure_200 = int(round(max(table_pure['rtu04']['200'][1]['Total_Experimental']['Dn'],  table_pure['rtu04']['200'][1]['Total_Experimental']['Up'])/TotalUnc_rtu_pure_200, 2) * 100)
    
    Flavour_Tagger_rtu_pure_200 = int(round(max(table_pure['rtu04']['200'][2]['Flavour_Tagger']['Dn'],  table_pure['rtu04']['200'][2]['Flavour_Tagger']['Up'])/TotalUnc_rtu_pure_200, 2) * 100)
    
    Nonprompt_Lepton_rtu_pure_200 = int(round(max(table_pure['rtu04']['200'][2]['Nonprompt_Lepton']['Dn'],  table_pure['rtu04']['200'][2]['Nonprompt_Lepton']['Up'])/TotalUnc_rtu_pure_200, 2) * 100) 
    
    NormttW_rtu_pure_200 = int(round(max(table_pure['rtu04']['200'][2]['NormttW']['Dn'],  table_pure['rtu04']['200'][2]['NormttW']['Up'])/TotalUnc_rtu_pure_200, 2) * 100) 
    
    

    TotalUnc_rtu_pure_1000 = max(table_pure['rtu04']['1000'][1]['TotalUnc']['Dn'],  table_pure['rtu04']['1000'][1]['TotalUnc']['Up'])
    
    Stat_rtu_pure_1000 = int(round(max(table_pure['rtu04']['1000'][1][' Stat.']['Dn'],  table_pure['rtu04']['1000'][1][' Stat.']['Up'])/TotalUnc_rtu_pure_1000, 2) * 100)
    
    Total_SignalModeling_rtu_pure_1000 = int(round(max(table_pure['rtu04']['1000'][1]['Total_SignalModeling']['Dn'],  table_pure['rtu04']['1000'][1]['Total_SignalModeling']['Up'])/TotalUnc_rtu_pure_1000, 2) * 100)
    
    Total_BackgroundModeling_rtu_pure_1000 = int(round(max(table_pure['rtu04']['1000'][1]['Total_BackgroundModeling']['Dn'],  table_pure['rtu04']['1000'][1]['Total_BackgroundModeling']['Up'])/TotalUnc_rtu_pure_1000, 2) * 100)
    
    Total_Experimental_rtu_pure_1000 = int(round(max(table_pure['rtu04']['1000'][1]['Total_Experimental']['Dn'],  table_pure['rtu04']['1000'][1]['Total_Experimental']['Up'])/TotalUnc_rtu_pure_1000, 2) * 100)
    
    Flavour_Tagger_rtu_pure_1000 = int(round(max(table_pure['rtu04']['1000'][2]['Flavour_Tagger']['Dn'],  table_pure['rtu04']['1000'][2]['Flavour_Tagger']['Up'])/TotalUnc_rtu_pure_1000, 2) * 100)
    
    Nonprompt_Lepton_rtu_pure_1000 = int(round(max(table_pure['rtu04']['1000'][2]['Nonprompt_Lepton']['Dn'],  table_pure['rtu04']['1000'][2]['Nonprompt_Lepton']['Up'])/TotalUnc_rtu_pure_1000, 2) * 100) 
    
    NormttW_rtu_pure_1000 = int(round(max(table_pure['rtu04']['1000'][2]['NormttW']['Dn'],  table_pure['rtu04']['1000'][2]['NormttW']['Up'])/TotalUnc_rtu_pure_1000, 2) * 100) 
    
    


    TotalUnc_rtu_interference_250 = max(table_interference['rtu04']['250'][1]['TotalUnc']['Dn'],  table_interference['rtu04']['250'][1]['TotalUnc']['Up'])
    
    Stat_rtu_interference_250 = int(round(max(table_interference['rtu04']['250'][1][' Stat.']['Dn'],  table_interference['rtu04']['250'][1][' Stat.']['Up'])/TotalUnc_rtu_interference_250, 2) * 100)
    
    Total_SignalModeling_rtu_interference_250 = int(round(max(table_interference['rtu04']['250'][1]['Total_SignalModeling']['Dn'],  table_interference['rtu04']['250'][1]['Total_SignalModeling']['Up'])/TotalUnc_rtu_interference_250, 2) * 100)
    
    Total_BackgroundModeling_rtu_interference_250 = int(round(max(table_interference['rtu04']['250'][1]['Total_BackgroundModeling']['Dn'],  table_interference['rtu04']['250'][1]['Total_BackgroundModeling']['Up'])/TotalUnc_rtu_interference_250, 2) * 100)
    
    Total_Experimental_rtu_interference_250 = int(round(max(table_interference['rtu04']['250'][1]['Total_Experimental']['Dn'],  table_interference['rtu04']['250'][1]['Total_Experimental']['Up'])/                                     TotalUnc_rtu_interference_250, 2) * 100)
    
    
    Flavour_Tagger_rtu_interference_250 = int(round(max(table_interference['rtu04']['250'][2]['Flavour_Tagger']['Dn'],  table_interference['rtu04']['250'][2]['Flavour_Tagger']['Up'])/TotalUnc_rtu_interference_250, 2) * 100)
    
    Nonprompt_Lepton_rtu_interference_250 = int(round(max(table_interference['rtu04']['250'][2]['Nonprompt_Lepton']['Dn'],  table_interference['rtu04']['250'][2]['Nonprompt_Lepton']['Up'])/TotalUnc_rtu_interference_250, 2) * 100) 
    
    NormttW_rtu_interference_250 = int(round(max(table_interference['rtu04']['250'][2]['NormttW']['Dn'],  table_interference['rtu04']['250'][2]['NormttW']['Up'])/TotalUnc_rtu_interference_250, 2) * 100) 
    
    

    TotalUnc_rtu_interference_1000 = max(table_interference['rtu04']['1000'][1]['TotalUnc']['Dn'],  table_interference['rtu04']['1000'][1]['TotalUnc']['Up'])
    
    Stat_rtu_interference_1000 = int(round(max(table_interference['rtu04']['1000'][1][' Stat.']['Dn'],  table_interference['rtu04']['1000'][1][' Stat.']['Up'])/TotalUnc_rtu_interference_1000, 2) * 100)
    
    Total_BackgroundModeling_rtu_interference_1000 = int(round(max(table_interference['rtu04']['1000'][1]['Total_BackgroundModeling']['Dn'],  table_interference['rtu04']['1000'][1]['Total_BackgroundModeling']['Up'])/TotalUnc_rtu_interference_1000, 2) * 100)
    Total_SignalModeling_rtu_interference_1000 = int(round(max(table_interference['rtu04']['1000'][1]['Total_SignalModeling']['Dn'],  table_interference['rtu04']['1000'][1]['Total_SignalModeling']['Up'])/TotalUnc_rtu_interference_1000, 2) * 100)
    
    Total_Experimental_rtu_interference_1000 = int(round(max(table_interference['rtu04']['1000'][1]['Total_Experimental']['Dn'],  table_interference['rtu04']['1000'][1]['Total_Experimental']['Up'])/TotalUnc_rtu_interference_1000, 2) * 100)
    
    
    Flavour_Tagger_rtu_interference_1000 = int(round(max(table_interference['rtu04']['1000'][2]['Flavour_Tagger']['Dn'],  table_interference['rtu04']['1000'][2]['Flavour_Tagger']['Up'])/TotalUnc_rtu_interference_1000, 2) * 100)
    
    Nonprompt_Lepton_rtu_interference_1000 = int(round(max(table_interference['rtu04']['1000'][2]['Nonprompt_Lepton']['Dn'],  table_interference['rtu04']['1000'][2]['Nonprompt_Lepton']['Up'])/TotalUnc_rtu_interference_1000, 2) * 100) 
    
    NormttW_rtu_interference_1000 = int(round(max(table_interference['rtu04']['1000'][2]['NormttW']['Dn'],  table_interference['rtu04']['1000'][2]['NormttW']['Up'])/TotalUnc_rtu_interference_1000, 2) * 100) 
    
    


    TotalUnc_rtc_pure_200 = max(table_pure['rtc04']['200'][1]['TotalUnc']['Dn'],  table_pure['rtc04']['200'][1]['TotalUnc']['Up'])
    
    Stat_rtc_pure_200 = int(round(max(table_pure['rtc04']['200'][1][' Stat.']['Dn'],  table_pure['rtc04']['200'][1][' Stat.']['Up'])/TotalUnc_rtc_pure_200, 2) * 100)
    
    Total_SignalModeling_rtc_pure_200 = int(round(max(table_pure['rtc04']['200'][1]['Total_SignalModeling']['Dn'],  table_pure['rtc04']['200'][1]['Total_SignalModeling']['Up'])/TotalUnc_rtc_pure_200, 2) * 100)
    
    Total_BackgroundModeling_rtc_pure_200 = int(round(max(table_pure['rtc04']['200'][1]['Total_BackgroundModeling']['Dn'],  table_pure['rtc04']['200'][1]['Total_BackgroundModeling']['Up'])/TotalUnc_rtc_pure_200, 2) * 100)
    
    Total_Experimental_rtc_pure_200 = int(round(max(table_pure['rtc04']['200'][1]['Total_Experimental']['Dn'],  table_pure['rtc04']['200'][1]['Total_Experimental']['Up'])/TotalUnc_rtc_pure_200, 2) * 100)
    
    Flavour_Tagger_rtc_pure_200 = int(round(max(table_pure['rtc04']['200'][2]['Flavour_Tagger']['Dn'],  table_pure['rtc04']['200'][2]['Flavour_Tagger']['Up'])/TotalUnc_rtc_pure_200, 2) * 100)
    
    Nonprompt_Lepton_rtc_pure_200 = int(round(max(table_pure['rtc04']['200'][2]['Nonprompt_Lepton']['Dn'],  table_pure['rtc04']['200'][2]['Nonprompt_Lepton']['Up'])/TotalUnc_rtc_pure_200, 2) * 100) 
    
    NormttW_rtc_pure_200 = int(round(max(table_pure['rtc04']['200'][2]['NormttW']['Dn'],  table_pure['rtc04']['200'][2]['NormttW']['Up'])/TotalUnc_rtc_pure_200, 2) * 100) 
    
    

    TotalUnc_rtc_pure_1000 = max(table_pure['rtc04']['1000'][1]['TotalUnc']['Dn'],  table_pure['rtc04']['1000'][1]['TotalUnc']['Up'])
    
    Stat_rtc_pure_1000 = int(round(max(table_pure['rtc04']['1000'][1][' Stat.']['Dn'],  table_pure['rtc04']['1000'][1][' Stat.']['Up'])/TotalUnc_rtc_pure_1000, 2) * 100)
    
    Total_SignalModeling_rtc_pure_1000 = int(round(max(table_pure['rtc04']['1000'][1]['Total_SignalModeling']['Dn'],  table_pure['rtc04']['1000'][1]['Total_SignalModeling']['Up'])/TotalUnc_rtc_pure_1000, 2) * 100)
    
    Total_BackgroundModeling_rtc_pure_1000 = int(round(max(table_pure['rtc04']['1000'][1]['Total_BackgroundModeling']['Dn'],  table_pure['rtc04']['1000'][1]['Total_BackgroundModeling']['Up'])/TotalUnc_rtc_pure_1000, 2) * 100)
    
    Total_Experimental_rtc_pure_1000 = int(round(max(table_pure['rtc04']['1000'][1]['Total_Experimental']['Dn'],  table_pure['rtc04']['1000'][1]['Total_Experimental']['Up'])/TotalUnc_rtc_pure_1000, 2) * 100)
    
    Flavour_Tagger_rtc_pure_1000 = int(round(max(table_pure['rtc04']['1000'][2]['Flavour_Tagger']['Dn'],  table_pure['rtc04']['1000'][2]['Flavour_Tagger']['Up'])/TotalUnc_rtc_pure_1000, 2) * 100)
    
    Nonprompt_Lepton_rtc_pure_1000 = int(round(max(table_pure['rtc04']['1000'][2]['Nonprompt_Lepton']['Dn'],  table_pure['rtc04']['1000'][2]['Nonprompt_Lepton']['Up'])/TotalUnc_rtc_pure_1000, 2) * 100) 
    
    NormttW_rtc_pure_1000 = int(round(max(table_pure['rtc04']['1000'][2]['NormttW']['Dn'],  table_pure['rtc04']['1000'][2]['NormttW']['Up'])/TotalUnc_rtc_pure_1000, 2) * 100) 
    
    


    TotalUnc_rtc_interference_250 = max(table_interference['rtc04']['250'][1]['TotalUnc']['Dn'],  table_interference['rtc04']['250'][1]['TotalUnc']['Up'])
    
    Stat_rtc_interference_250 = int(round(max(table_interference['rtc04']['250'][1][' Stat.']['Dn'],  table_interference['rtc04']['250'][1][' Stat.']['Up'])/TotalUnc_rtc_interference_250, 2) * 100)
    
    Total_SignalModeling_rtc_interference_250 = int(round(max(table_interference['rtc04']['250'][1]['Total_SignalModeling']['Dn'],  table_interference['rtc04']['250'][1]['Total_SignalModeling']['Up'])/TotalUnc_rtc_interference_250, 2) * 100)
    
    Total_BackgroundModeling_rtc_interference_250 = int(round(max(table_interference['rtc04']['250'][1]['Total_BackgroundModeling']['Dn'],  table_interference['rtc04']['250'][1]['Total_BackgroundModeling']['Up'])/TotalUnc_rtc_interference_250, 2) * 100)
    
    Total_Experimental_rtc_interference_250 = int(round(max(table_interference['rtc04']['250'][1]['Total_Experimental']['Dn'],  table_interference['rtc04']['250'][1]['Total_Experimental']['Up'])/TotalUnc_rtc_interference_250, 2) * 100)
    
    Flavour_Tagger_rtc_interference_250 = int(round(max(table_interference['rtc04']['250'][2]['Flavour_Tagger']['Dn'],  table_interference['rtc04']['250'][2]['Flavour_Tagger']['Up'])/TotalUnc_rtc_interference_250, 2) * 100)
    
    Nonprompt_Lepton_rtc_interference_250 = int(round(max(table_interference['rtc04']['250'][2]['Nonprompt_Lepton']['Dn'],  table_interference['rtc04']['250'][2]['Nonprompt_Lepton']['Up'])/TotalUnc_rtc_interference_250, 2) * 100) 
    
    NormttW_rtc_interference_250 = int(round(max(table_interference['rtc04']['250'][2]['NormttW']['Dn'],  table_interference['rtc04']['250'][2]['NormttW']['Up'])/TotalUnc_rtc_interference_250, 2) * 100) 
    
    

    TotalUnc_rtc_interference_1000 = max(table_interference['rtc04']['1000'][1]['TotalUnc']['Dn'],  table_interference['rtc04']['1000'][1]['TotalUnc']['Up'])
    
    Stat_rtc_interference_1000 = int(round(max(table_interference['rtc04']['1000'][1][' Stat.']['Dn'],  table_interference['rtc04']['1000'][1][' Stat.']['Up'])/TotalUnc_rtc_interference_1000, 2) * 100)
    
    Total_SignalModeling_rtc_interference_1000 = int(round(max(table_interference['rtc04']['1000'][1]['Total_SignalModeling']['Dn'],  table_interference['rtc04']['1000'][1]['Total_SignalModeling']['Up'])/TotalUnc_rtc_interference_1000, 2) * 100)
    
    Total_BackgroundModeling_rtc_interference_1000 = int(round(max(table_interference['rtc04']['1000'][1]['Total_BackgroundModeling']['Dn'],  table_interference['rtc04']['1000'][1]['Total_BackgroundModeling']['Up'])/TotalUnc_rtc_interference_1000, 2) * 100)
    
    Total_Experimental_rtc_interference_1000 = int(round(max(table_interference['rtc04']['1000'][1]['Total_Experimental']['Dn'],  table_interference['rtc04']['1000'][1]['Total_Experimental']['Up'])/TotalUnc_rtc_interference_1000, 2) * 100)
    
    Flavour_Tagger_rtc_interference_1000 = int(round(max(table_interference['rtc04']['1000'][2]['Flavour_Tagger']['Dn'],  table_interference['rtc04']['1000'][2]['Flavour_Tagger']['Up'])/TotalUnc_rtc_interference_1000, 2) * 100)
    
    Nonprompt_Lepton_rtc_interference_1000 = int(round(max(table_interference['rtc04']['1000'][2]['Nonprompt_Lepton']['Dn'],  table_interference['rtc04']['1000'][2]['Nonprompt_Lepton']['Up'])/TotalUnc_rtc_interference_1000, 2) * 100) 
    
    NormttW_rtc_interference_1000 = int(round(max(table_interference['rtc04']['1000'][2]['NormttW']['Dn'],  table_interference['rtc04']['1000'][2]['NormttW']['Up'])/TotalUnc_rtc_interference_1000, 2) * 100) 
    
    
    
    # Stat.
    #Total_Modeling
    #Total_Experimental
    #TotalUnc
    #Total_Background
    #Flavour_Tagger
    #Nonprompt_Lepton
    #NormttW
    Latex_Lines.append(r'\begin{table}[!htpb]')
    Latex_Lines.append(r'\begin{center}')
    caption = r'\caption{Contributions of the dominant uncertainty sources with respect to the total uncertainty given in percentages. The total background contains the uncertainties due to nonprompt background estimation, chanrge misidentification, and normalization of \ttbar, others, \VV, \ttH, and \ttW backgrounds.}'
    Latex_Lines.append(caption)
    Latex_Lines.append(r'\footnotesize')
    Latex_Lines.append(r'\begin{tabular}{c|c|c}')
    Latex_Lines.append(r'& \multicolumn{2}{c}{$\rho_{\PQt\PQu}=0.4$} \\')
    Latex_Lines.append(r'\cline{2-3}')
    Latex_Lines.append(r'& $200\GeV$ (1\TeV)        &     $250\GeV$(1\TeV) \\')
    Latex_Lines.append(r'& Without interference & With interference  \\')
    Latex_Lines.append(r'\hline')
    Latex_Lines.append(r'flavour tagger & {} ({})& {} ({})\\'.format(Flavour_Tagger_rtu_pure_200, Flavour_Tagger_rtu_pure_1000, Flavour_Tagger_rtu_interference_250, Flavour_Tagger_rtu_interference_1000))    
    Latex_Lines.append(r'nonprompt lepton &{} ({}) & {} ({})\\'.format(Nonprompt_Lepton_rtu_pure_200, Nonprompt_Lepton_rtu_pure_1000, Nonprompt_Lepton_rtu_interference_250, Nonprompt_Lepton_rtu_interference_1000))    
    Latex_Lines.append(r'\ttW background &{} ({}) & {} ({})\\'.format(NormttW_rtu_pure_200, NormttW_rtu_pure_1000, NormttW_rtu_interference_250, NormttW_rtu_interference_1000))    
    Latex_Lines.append(r'total signal modeling &{} ({}) & {} ({})\\'.format(Total_SignalModeling_rtu_pure_200,Total_SignalModeling_rtu_pure_1000, Total_SignalModeling_rtu_interference_250, Total_SignalModeling_rtu_interference_1000))    
    Latex_Lines.append(r'total background modeling&{} ({}) & {} ({})\\'.format(Total_BackgroundModeling_rtu_pure_200,Total_BackgroundModeling_rtu_pure_1000, Total_BackgroundModeling_rtu_interference_250, Total_BackgroundModeling_rtu_interference_1000))
        
    Latex_Lines.append(r'total experimental &{} ({}) & {} ({})\\'.format(Total_Experimental_rtu_pure_200, Total_Experimental_rtu_pure_1000, Total_Experimental_rtu_interference_250, Total_Experimental_rtu_interference_1000))    
    
    Latex_Lines.append(r'statistical & {} ({})& {} ({})\\'.format(Stat_rtu_pure_200, Stat_rtu_pure_1000, Stat_rtu_interference_250, Stat_rtu_interference_1000))
    Latex_Lines.append(r'& & \\') 
    Latex_Lines.append(r'& \multicolumn{2}{c}{$\rho_{\PQt\PQc}=0.4$} \\')
    Latex_Lines.append(r'\hline')
    Latex_Lines.append(r'flavour tagger & {} ({})& {} ({})\\'.format(Flavour_Tagger_rtc_pure_200, Flavour_Tagger_rtc_pure_1000, Flavour_Tagger_rtc_interference_250, Flavour_Tagger_rtc_interference_1000))    
    Latex_Lines.append(r'nonprompt lepton &{} ({}) & {} ({})\\'.format(Nonprompt_Lepton_rtc_pure_200, Nonprompt_Lepton_rtc_pure_1000, Nonprompt_Lepton_rtc_interference_250, Nonprompt_Lepton_rtc_interference_1000))    
    Latex_Lines.append(r'\ttW background &{} ({}) & {} ({})\\'.format(NormttW_rtc_pure_200, NormttW_rtc_pure_1000, NormttW_rtc_interference_250, NormttW_rtc_interference_1000))    
    Latex_Lines.append(r'total signal modeling &{} ({}) & {} ({})\\'.format(Total_SignalModeling_rtc_pure_200,Total_SignalModeling_rtc_pure_1000, Total_SignalModeling_rtc_interference_250, Total_SignalModeling_rtc_interference_1000))    
    Latex_Lines.append(r'total background modeling &{} ({}) & {} ({})\\'.format(Total_BackgroundModeling_rtc_pure_200, Total_BackgroundModeling_rtc_pure_1000, Total_BackgroundModeling_rtc_interference_250, Total_BackgroundModeling_rtc_interference_1000))    
    Latex_Lines.append(r'total experimental &{} ({}) & {} ({})\\'.format(Total_Experimental_rtc_pure_200, Total_Experimental_rtc_pure_1000, Total_Experimental_rtc_interference_250, Total_Experimental_rtc_interference_1000))    
    Latex_Lines.append(r'statistical & {} ({})& {} ({})\\'.format(Stat_rtc_pure_200, Stat_rtc_pure_1000, Stat_rtc_interference_250, Stat_rtc_interference_1000))
    Latex_Lines.append(r'\end{tabular}') 
    Latex_Lines.append(r'\label{tab:systematics}')
    Latex_Lines.append(r'\end{center}')
    Latex_Lines.append(r'\end{table}')
    with open('Table_001.tex', 'w') as f:
        for Line in Latex_Lines:
            f.write(Line + ' \n')
