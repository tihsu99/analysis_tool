
import json



def Datacard_Input_Producer(channel='',process=['TAToTTQ_COUPLINGVALUE_MAMASSPOINT','TTTo1L','TTTo2L','ttWtoLNu','ttVV','ttV','tttX','VVV','t_tbar_W','tt_V_H','DY','tzq'],nuisances=[]):

    Input = dict()
    
    Input['Process'] = process
    Input['process1'] =[]
    Input['rate'] =[]
    Input['NuisForProc'] = dict()
    N_process = len(process)
    Input['UnclnN'] = dict()

    
    for i in range(N_process):
        Input['process1'].append(i) 
    
    for nuisance in nuisances:
        Input['NuisForProc'][nuisance] = []
        
        if nuisance != 'fakeYEAR':
            Input['UnclnN'][nuisance]='shape'
        else:
            Input['UnclnN'][nuisance]='1.30'

        for proc in process:
            if nuisance != 'fakeYEAR':
                if proc !='TTTo1L':
                    Input['NuisForProc'][nuisance].append(proc)
                else:pass
            else:
                if proc =='TTTo1L':
                    Input['NuisForProc'][nuisance].append(proc)
                else:pass 
    for idx in range(N_process):
        Input['process1'].append(idx)
        Input['rate'].append(-1)


    return Input



with open('./data_info/nuisance_list.json') as f:

    nuisances = json.load(f)




A = Datacard_Input_Producer(nuisances=nuisances)
print(A)

