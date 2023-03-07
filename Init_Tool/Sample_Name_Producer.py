import json 
from Util.General_Tool import CheckFile
'''
You need to fill in the process name for MC sample in root file manually.

'''

def Bkg_MC_SAMPLE_NAME(year='',outputdir=''):
    SAMPLE=dict()
    SAMPLE['ttVH'] = [] # ttH + ttWH + ttZH
    SAMPLE['Nonprompt'] = [] # TTTo1L without WJets
    SAMPLE['TTTo2L'] = [] #TTTo2L
#    SAMPLE['DY'] = [] #DY
    SAMPLE['VV'] = [] #  osWW + WWdps + WZ_qcd 
    SAMPLE['VBS'] = []
#    SAMPLE['VVV'] = []
#    SAMPLE['SingleTop'] = []
    SAMPLE['ttW'] = []
#    SAMPLE['ttZ'] = []
#    SAMPLE['ttVV'] = []
#    SAMPLE['tttX'] = []
#    SAMPLE['tZq'] = []
    SAMPLE['Others'] = [] #tZq + singletop + VVV + tttX + DY + ttVV + ttZ


    #1) ttVH = ttH + ttWH + ttZH --> assign uncertainty
    #2) ttto1l --> [OK] but rename as nonprompt
    #3) TT2L [OK]
    #4) DY
    #==> Why don't we have Wjets? Is that part of non prompt?
    #5) VV = osWW + WWdps + WZ_qcd --> assign uncertainty
    #6) VBS = WpWpJJ_EWK + WpWpJJ_QCD + WLLJJ + ZZJJTo4L [OK] --> assign uncertainty
    #7) VVV = ZZZ+ WZZ + WWZ + WWW --> OK but add the uncertainty for WWW
    #8) Single top = tW + tbarW +  Why t + tbar + s-channel are not included in BDT? 
    #9) ttW 
    #10) ttZ
    #11) TTVV = ttZZ + ttWZ + ttWW --> assign uncertainty
    #12) tttX = tttW + tttt + tttj [OK]
    #13) tZq [OK]
    
    
    
    ###VBS###
    SAMPLE['VBS'].append('WpWpJJ_EWK') 
    SAMPLE['VBS'].append('WLLJJ')
    SAMPLE['VBS'].append('ZZJJTo4L')
    SAMPLE['VBS'].append('WpWpJJ_QCD')

    ### TTTo1L ###
    SAMPLE['Nonprompt'].append('TTTo1L')
    
    ### TTTo2L ###
    SAMPLE['TTTo2L'].append('TTTo2L')
    
    ### DY ###
    if year == '2016apv' or year=='2016postapv' or year =='2017' or year=='2018':
        SAMPLE['Others'].append('DYnlo')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    ### ttWtoLNu ###
    if year == '2018' or year=='2017':
        SAMPLE['ttW'].append('ttWtoLNu')
        SAMPLE['ttW'].append('ttWtoQQ')
    elif year=='2016postapv' or year=='2016apv': 
        SAMPLE['ttW'].append('ttW')
        SAMPLE['ttW'].append('ttWToQQ')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.

    ## ttVV ##
    if year =='2018' or year=='2017' or year =='2016postapv' or year =='2016apv':
        SAMPLE['Others'].append('ttWW')
        SAMPLE['Others'].append('ttWZ')
        SAMPLE['Others'].append('ttZZ')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    ### ttV ###
    if year =='2018' or year=='2017':
        SAMPLE['Others'].append('ttZ')
        SAMPLE['Others'].append('ttZtoQQ')
    elif  year =='2016postapv' or year =='2016apv':
        SAMPLE['Others'].append('ttZ')
        SAMPLE['Others'].append('ttZToQQ')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    
    ### tttX ###
    if year =='2018' or year=='2017' or year =='2016postapv' or year == '2016apv':
        SAMPLE['Others'].append('tttW')
        SAMPLE['Others'].append('tttt')
        SAMPLE['Others'].append('tttJ')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    

    ### VVV ###
    if year=='2018' or year=='2017':
        SAMPLE['Others'].append('WWW')
        SAMPLE['Others'].append('WWZ')
        SAMPLE['Others'].append('WZZ')
        SAMPLE['Others'].append('ZZZ')
    elif year=='2016postapv' or year=='2016apv':
        SAMPLE['Others'].append('www1')
        SAMPLE['Others'].append('wwz1')
        SAMPLE['Others'].append('wzz1')
        SAMPLE['Others'].append('zzz1')

    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    ### tW or tbar_W ###
    if year =='2018' or year=='2017' or year =='2016postapv'  or year =='2016apv':
        SAMPLE['Others'].append('tW')
        SAMPLE['Others'].append('tbarW')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.

    ### tt_V_H ###
    if year =='2018' or year=='2017' or year =='2016postapv' or year =='2016apv':
        SAMPLE['ttVH'].append('ttH')
        SAMPLE['ttVH'].append('ttWH')
        SAMPLE['ttVH'].append('ttZH')
    else:raise ValueError('Fix me') # -> You need to add sample by hands.
    
    ### tzq ###
    if year=='2018' or year=='2017':
        SAMPLE['Others'].append('tzq')
    elif year=='2016postapv' or year=='2016apv':
        SAMPLE['Others'].append('tZq')
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
    
    CheckFile('{}/process_name_{}.json'.format(outputdir,year),True)
    with open('{}/process_name_{}.json'.format(outputdir,year),'w') as f:

        json.dump(SAMPLE,f,indent=4)



    
