
import json
from Util.General_Tool import CheckFile


def Datacard_Input_Producer(year,channel='',process=['TAToTTQ_COUPLINGVALUE_MAMASSPOINT','TTTo1L','TTTo2L','ttWtoLNu','ttVV','ttV','tttX','VVV','t_tbar_W','tt_V_H','DY','tzq'],nuisances=[]):
    Input = dict()
    
    Input['bin']=dict()
    Input['Process'] = []
    Input['Process'] = process
    if 'TAToTTQ_COUPLINGVALUE_MAMASSPOINT' in process:pass
    else:
        Input['Process'].insert(0,'TAToTTQ_COUPLINGVALUE_MAMASSPOINT')
    Input['bin']['SR_{}'.format(channel)] = len(Input['Process'])
    Input['process1'] =[]
    Input['rate'] =[]
    Input['NuisForProc'] = dict()
    N_process = len(Input['Process'])
    Input['UnclnN'] = dict()
    process = Input['Process']
    
    for idx in range(N_process):
        Input['process1'].append(idx)
        Input['rate'].append(-1)
    for nuisance in nuisances:
        nuisance=str(nuisance.split('_')[-1])
        Input['NuisForProc'][nuisance] = []
        

        lnN_nuisance = ['fake','normTTTo2L','normttWW','normttZZ','normttWZ','normttZ','normttW','normtZq','normtttX','normVVV']
        sig_nuisance = ['sigYEARpdf','sigYEARscale','sigYEARps']
        if nuisance not in lnN_nuisance:
            Input['UnclnN'][nuisance]='shape'
        if nuisance in lnN_nuisance or nuisance in sig_nuisance:
            if nuisance == 'fake':
                Input['UnclnN'][nuisance]='1.30'
                Input['NuisForProc'][nuisance].append('TTTo1L')
            elif nuisance =='normTTTo2L':
                Input['UnclnN'][nuisance]='1.061'
                Input['NuisForProc'][nuisance].append('TTTo2L')
            elif nuisance =='normTTTo1L':
                pass
                #Input['UnclnN'][nuisance]='1.061'
                #Input['NuisForProc'][nuisance].append('TTTo1L')
            elif nuisance =='normttWW':
                Input['UnclnN'][nuisance]='1.114'
                Input['NuisForProc'][nuisance].append('ttWW')
            elif nuisance =='normttZZ':
                Input['UnclnN'][nuisance]='1.087'
                Input['NuisForProc'][nuisance].append('ttZZ')
            elif nuisance =='normttWZ':
                Input['UnclnN'][nuisance]='1.106'
                Input['NuisForProc'][nuisance].append('ttWZ')
            elif nuisance =='normttZ':
                Input['UnclnN'][nuisance]='1.147'
                Input['NuisForProc'][nuisance].append('ttZ')
            elif nuisance =='normttW':
                Input['UnclnN'][nuisance]='1.112'
                Input['NuisForProc'][nuisance].append('ttWtoLNu')
            elif nuisance =='normtZq':
                Input['UnclnN'][nuisance]='1.10'
                Input['NuisForProc'][nuisance].append('tzq')
            elif nuisance =='normtttX':
                Input['UnclnN'][nuisance]='1.30'
                Input['NuisForProc'][nuisance].append('tttX')
            elif nuisance =='normVVV':
                Input['NuisForProc'][nuisance].append('VVV')
                Input['UnclnN'][nuisance]='1.20'
            elif nuisance in sig_nuisance:
                Input['NuisForProc'][nuisance].append('TAToTTQ_COUPLINGVALUE_MAMASSPOINT')
            
            else:
                raise ValueError('Fix me. ')
        for proc in process:
            if year=='2018' and nuisance =='prefire':continue
            
            if nuisance not in lnN_nuisance and nuisance not in sig_nuisance:
                if proc !='TTTo1L':
                    if channel=='ee':
                        if nuisance=='muIDYEARsys' or nuisance=='muIDYEARstat' or nuisance=='elemuTriggerYEAR' or nuisance=='dimuTriggerYEAR':continue
                        elif 'chargeflipYEAR' in nuisance and proc=='TAToTTQ_COUPLINGVALUE_MAMASSPOINT':continue 
                    elif channel=='em':
                        if nuisance=='dieleTriggerYEAR' or nuisance=='dimuTriggerYEAR' or nuisance=='chargeflipYEAR':continue
                    else:
                        if nuisance=='eleIDYEARsys' or nuisance=='eleIDYEARstat' or nuisance=='dieleTriggerYEAR' or 'chargeflipYEAR' in nuisance or nuisance=='elemuTriggerYEAR':continue
                    Input['NuisForProc'][nuisance].append(proc)
                else:pass
            else:pass
    
    CheckFile('./data_info/Datacard_Input/{}/Datacard_Input_{}.json'.format(year,channel),True)
    with open('./data_info/Datacard_Input/{}/Datacard_Input_{}.json'.format(year,channel),'w') as f:
        json.dump(Input,f,indent=4)
 
    print("Write Datacard_Input into ./data_info/Datacard_Input/{}/Datacard_Input_{}.json".format(year,channel))
    print("")
    return Input

