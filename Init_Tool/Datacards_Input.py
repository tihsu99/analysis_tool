
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
        nuisance=nuisance.split('_')[-1].strip()
        print(nuisance)
        Input['NuisForProc'][nuisance] = []
        
        if year=='2016apv' or year=='2016postapv':
            lnN_nuisance =  ["fakeYEAR","normTTTo2L","normOthers","normVV","normVBS","normttVH","normttW","lumi2016","lumiCorrFullRun2","lumiCorr1718"]
        else:
            lnN_nuisance =  ["fakeYEAR","normTTTo2L","normOthers","normVV","normVBS","normttVH","normttW","lumiYEAR","lumiCorrFullRun2","lumiCorr1718"]

        sig_nuisance = ['sigpdf','sigscale','sigps']
        
        if nuisance not in lnN_nuisance:
            Input['UnclnN'][nuisance]='shape'
        else:pass
        if nuisance in lnN_nuisance or nuisance in sig_nuisance:
            if nuisance == 'fakeYEAR':
                if "2016apv" in year:
                  Input['UnclnN'][nuisance]='1.27'
                if "2016postapv" in year:
                  Input['UnclnN'][nuisance]='1.15'
                if "2017" in year:
                  Input['UnclnN'][nuisance]='1.11'
                if "2018" in year:
                  Input['UnclnN'][nuisance]='1.10'
                Input['NuisForProc'][nuisance].append('Nonprompt')
            elif nuisance == 'lumiYEAR' or nuisance == 'lumi2016':
                if "2016" in year:
                    Input['UnclnN'][nuisance] = '1.01'
                elif "2017" in year:
                    Input['UnclnN'][nuisance] = '1.02'
                elif "2018" in year:
                    Input['UnclnN'][nuisance] = '1.015'
                else:raise ValueError("No such year: {year}".format(year=year))
                for proc in process:
                    if proc !='Nonprompt':
                        Input['NuisForProc'][nuisance].append(proc)
                    else:pass 
            elif nuisance == 'lumiCorrFullRun2' :
                if "2016" in year:
                    Input['UnclnN'][nuisance] = '1.006'
                elif "2017" in year:
                    Input['UnclnN'][nuisance] = '1.009'
                elif "2018" in year:
                    Input['UnclnN'][nuisance] = '1.020'
                else:raise ValueError("No such year: {year}".format(year=year))
                for proc in process:
                    if proc !='Nonprompt':
                        Input['NuisForProc'][nuisance].append(proc)
                    else:pass 
            elif nuisance == 'lumiCorr1718':
                print(nuisance)
                if "2017" == year:
                    Input['UnclnN'][nuisance] = '1.006'
                elif "2018" ==  year:
                    Input['UnclnN'][nuisance] = '1.002'
                else:raise ValueError("No such year: {year}".format(year=year))
                for proc in process:
                    if proc !='Nonprompt':
                        Input['NuisForProc'][nuisance].append(proc)
                    else:pass 
            elif nuisance =='normTTTo2L':
                Input['UnclnN'][nuisance]='1.061'
                Input['NuisForProc'][nuisance].append('TTTo2L')
            elif nuisance =='normOthers':
                Input['UnclnN'][nuisance]='1.30'
                Input['NuisForProc'][nuisance].append('Others')
            elif nuisance =='normSingleTop':
                Input['UnclnN'][nuisance]='1.054'
                Input['NuisForProc'][nuisance].append('SingleTop')
            elif nuisance =='normDY':
                Input['NuisForProc'][nuisance].append('DY')
                Input['UnclnN'][nuisance]='1.003'
            elif nuisance =='normVV':
                Input['NuisForProc'][nuisance].append('VV')
                Input['UnclnN'][nuisance]='1.051'
            elif nuisance =='normVBS':
                Input['NuisForProc'][nuisance].append('VBS')
                Input['UnclnN'][nuisance]='1.30'
            elif nuisance =='normttVV':
                Input['UnclnN'][nuisance]='1.18'
                Input['NuisForProc'][nuisance].append('ttVV')
            elif nuisance =='normttVH':
                Input['NuisForProc'][nuisance].append('ttVH')
                Input['UnclnN'][nuisance]='1.50'
            elif nuisance =='normttZ':
                Input['UnclnN'][nuisance]='1.147'
                Input['NuisForProc'][nuisance].append('ttZ')
            elif nuisance =='normttW':
                Input['UnclnN'][nuisance]='1.107'
                Input['NuisForProc'][nuisance].append('ttW')
            elif nuisance =='normtZq':
                Input['UnclnN'][nuisance]='1.10'
                Input['NuisForProc'][nuisance].append('tZq')
            elif nuisance =='normtttX':
                Input['UnclnN'][nuisance]='1.30'
                Input['NuisForProc'][nuisance].append('tttX')
            elif nuisance =='normVVV':
                Input['NuisForProc'][nuisance].append('VVV')
                Input['UnclnN'][nuisance]='1.20'

            elif nuisance in sig_nuisance:
                Input['NuisForProc'][nuisance].append('TAToTTQ_COUPLINGVALUE_MAMASSPOINT')
            
            else:
                print(repr(nuisance))
                raise ValueError('No such nuisance: {nuisance}'.format(nuisance=nuisance))
        for proc in process:
            if nuisance not in lnN_nuisance and nuisance not in sig_nuisance:
                if 'fakeYEAR' in nuisance:
                  if proc == 'Nonprompt':
                    Input['NuisForProc'][nuisance].append(proc)
                elif proc !='Nonprompt':
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

