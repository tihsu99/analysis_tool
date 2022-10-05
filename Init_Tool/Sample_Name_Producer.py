import json 
'''
You need to fill in the process name for MC sample in root file manually.

'''

def Bkg_MC_SAMPLE_NAME(year=''):
    SAMPLE=dict()
    SAMPLE['DY'] = []
    SAMPLE['TTTo1L'] = []
    SAMPLE['TTTo2L'] = []
    SAMPLE['ttWtoLNu'] = []
    SAMPLE['ttVV'] = []
    SAMPLE['ttV'] = []
    SAMPLE['tttX'] = []
    SAMPLE['VVV'] = []
    SAMPLE['t_tbar_W'] = []
    SAMPLE['tt_V_H'] = []
    SAMPLE['tzq'] = []
    SAMPLE['VV'] = []

    ### TTTo1L ###
    SAMPLE['TTTo1L'].append('TTTo1L')
    
    ### TTTo2L ###
    SAMPLE['TTTo2L'].append('TTTo2L')
    
    ### DY ###
    if year == '2016apv' or year=='2016postapv' or year =='2017' or year=='2018':
        SAMPLE['DY'].append('DYnlo')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    ### ttWtoLNu ###
    if year == '2018' or year=='2017':
        SAMPLE['ttWtoLNu'].append('ttWtoLNu')
    elif year=='2016postapv' or year=='2016apv': 
        SAMPLE['ttWtoLNu'].append('ttW')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    ## ttVV ##
    if year =='2018' or year=='2017' or year =='2016postapv' or year =='2016apv':
        SAMPLE['ttVV'].append('ttWW')
        SAMPLE['ttVV'].append('ttWZ')
        SAMPLE['ttVV'].append('ttZZ')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    
    ### ttV ###
    if year =='2018' or year=='2017' or year =='2016postapv' or year =='2016apv':
        SAMPLE['ttV'].append('ttZ')
        SAMPLE['ttV'].append('ttZtoQQ')
        SAMPLE['ttV'].append('ttWtoQQ')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    
    ### tttX ###
    if year =='2018' or year=='2017' or year =='2016apv':
        SAMPLE['tttX'].append('tttW')
        SAMPLE['tttX'].append('tttt')
        SAMPLE['tttX'].append('tttJ')
    elif year == "2016postapv":
        SAMPLE['tttX'].append('tttt')
        SAMPLE['tttX'].append('tttJ')        
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    

    ### VVV ###
    if year=='2018' or year=='2017':
        SAMPLE['VVV'].append('WWW')
        SAMPLE['VVV'].append('WWZ')
        SAMPLE['VVV'].append('WZZ')
        SAMPLE['VVV'].append('ZZZ')
    elif year=='2016postapv' or year=='2016apv':
        SAMPLE['VVV'].append('www1')
        SAMPLE['VVV'].append('wwz1')
        SAMPLE['VVV'].append('wzz1')
        SAMPLE['VVV'].append('zzz1')

    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    ### tW or tbar_W ###
    if year =='2018' or year=='2017' or year =='2016postapv'  or year =='2016apv':
        SAMPLE['t_tbar_W'].append('tW')
        SAMPLE['t_tbar_W'].append('tbarW')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.

    ### tt_V_H ###
    if year =='2018' or year=='2017' or year =='2016postapv' or year =='2016apv':
        SAMPLE['tt_V_H'].append('ttH')
        SAMPLE['tt_V_H'].append('ttWH')
        SAMPLE['tt_V_H'].append('ttZH')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    
    ### tzq ###
    if year=='2018' or year=='2017':
        SAMPLE['tzq'].append('tzq')
    elif year=='2016postapv' or year=='2016apv':
        SAMPLE['tzq'].append('tZq')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    
    ### VV ###
    if year =='2018' or year=='2017':
        SAMPLE['VV'].append('osWW')
        SAMPLE['VV'].append('WWdps')
        SAMPLE['VV'].append('WZ_qcd')
    elif year=='2016apv' or year =='2016postapv':
        SAMPLE['VV'].append('zz2l')
        SAMPLE['VV'].append('wz_qcd')
        SAMPLE['VV'].append('ww')  
#        if year =='2018':
#            SAMPLE['VV'].append('WZ')          
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    
    with open('./data_info/process_name_{}.json'.format(year),'w') as f:

        json.dump(SAMPLE,f,indent=4)



    
