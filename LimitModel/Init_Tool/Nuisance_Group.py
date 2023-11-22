import json

from Util.General_Tool import CheckFile

def DefineGroup(outputdir = './'):
    ### These sets should be associated with Init_Tool/Nuisance_Producer.py
    Set1 = ['Total_Experimental', 'Total_SignalModeling', 'Total_BackgroundModeling']
    Set2 = ['Flavour_Tagger', 'Nonprompt_Lepton', 'NormttW', 'Experimental_Rest', 'Modeling_Rest']
    #Total Background Modeling: norm_XX
    #Total Signal Modeling: sig_XX
    #Total Experimental: All experimental nuisances sources (see AN)
    #Flavour_Tagger: ctag
    #NormttW
    #Nonprompt_Lepton
    
    #Set2 = ['Total_Background', 'Modeling', 'Flavour_Tagger', 'Experimental'] 
    #Set3 = ['Nonpormpt_Lepton', 'Flavour_Tagger', 'NormttW', 'Modeling', 'Experimental']
    
    CheckFile('{outputdir}/group_set1.json'.format(outputdir = outputdir), True) 
    CheckFile('{outputdir}/group_set2.json'.format(outputdir = outputdir), True) 
    #CheckFile('{outputdir}/group_set3.json'.format(outputdir = outputdir), True) 
    
    with open('{outputdir}/group_set1.json'.format(outputdir = outputdir), 'w') as f:
        json.dump(Set1, f, indent =4 ) 
    with open('{outputdir}/group_set2.json'.format(outputdir = outputdir), 'w') as f:
        json.dump(Set2, f, indent =4 ) 
    #with open('{outputdir}/group_set3.json'.format(outputdir = outputdir), 'w') as f:
    #    json.dump(Set3, f, indent =4 ) 
        
        
        