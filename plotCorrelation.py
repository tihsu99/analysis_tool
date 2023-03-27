import os
import ROOT
import json
import matplotlib.pyplot as plt
import numpy as np


def plotCorrelation(FitDiagnostics_file='', outputdir='', impacts_json = ''):

    inFile = ROOT.TFile.Open(FitDiagnostics_file ,"READ")

    Impact_Rank = 30
    Corr_Rank= 15
    CorrelationMatrix = inFile.Get('covariance_fit_s')

    with open(impacts_json) as f:
        data = json.load(f)

    POIs = [ele['name'] for ele in data['POIs']]
    POI = POIs[0]


    Params = data['params']
    print('Start to ranking impacts')
    Params.sort(key = lambda x: abs(x['impact_%s' % POI]), reverse = True)


    Impact_Rank_Top_param = []
    for idx, param in enumerate(Params):
        if idx > Impact_Rank: break
        paramInfo = dict()
        paramInfo['Name'] = param['name']
        paramInfo['bin'] = -1
        Impact_Rank_Top_param.append(paramInfo)
    print('Start to retrieve correlation information for nuisance')

    for paramInfo in Impact_Rank_Top_param:
        for ibin in range(CorrelationMatrix.GetNbinsX()):
            if CorrelationMatrix.GetXaxis().GetBinLabel(ibin+1) == paramInfo['Name']:
                paramInfo['bin'] = ibin+1
                
    print('Plotting')
    for idx,paramInfo in enumerate(Impact_Rank_Top_param):
        
        Correlation = []

        for ibin in range(CorrelationMatrix.GetNbinsX()):
            Info = {}
            Info['name'] = CorrelationMatrix.GetXaxis().GetBinLabel(ibin+1) 
            Info['correlation'] = CorrelationMatrix.GetBinContent(paramInfo['bin'], ibin+1)
            Correlation.append(Info)



        Correlation.sort(key = lambda x: abs(x['correlation']), reverse = True)
        Correlation = Correlation[:Corr_Rank]
        correlation_array = []
        name_array = []
        for corr in Correlation:
            correlation_array.append(corr['correlation'])
            name_array.append(corr['name'])

        ypos = np.arange(len(Correlation))
        plt.rcdefaults()
        fig, ax = plt.subplots()
        fig.set_size_inches(20.5, 10.5)
        ax.barh(ypos, np.array(correlation_array), align = 'center')
        ax.set_yticks(ypos)

        ax.set_yticklabels(name_array)
        
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(10) 
        ax.invert_yaxis()
        ax.set_xlabel('Correlation')
        ax.set_title('Correlation Ranking for %s' %paramInfo['Name'])
        
        output = os.path.join(outputdir, 'ImpactRank%s_CorrelationFor-%s.png'%(idx+1,  paramInfo['Name']))
        
        fig.savefig(output, dpi=100)
        print('\033[1;33m* Please check plot: \033[4m{}\033[0;m'.format(output))

