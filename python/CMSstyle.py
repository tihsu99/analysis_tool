from ROOT import *

def SetStyle(gPad, era='2016APV'):
	latex = TLatex();
	latex.SetNDC()
	l = gPad.GetLeftMargin();
	t = gPad.GetTopMargin();
	r = gPad.GetRightMargin();
	b = gPad.GetBottomMargin();
	#CMS text
	cmsText = "CMS";
	cmsTextFont = 60;
	cmsTextSize = 0.6;
	cmsTextOffset = 0.1;
	
	relPosX = 0.12;
	relPosY = 0.035;
	
	# extra 
	extraText = "  Preliminary 2017";
        if era == "2016APV":
                extraText = "  Preliminary 2016(APV)"; 
        if era == "2016postAPV":
                extraText = "  Preliminary 2016(postAPV)";
        if era == "2017":
                extraText = "  Preliminary 2017";
        if era == "2018":
                extraText = "  Preliminary 2018";
        if era == "2016merged":
                extraText = "  Preliminary 2016";
	#extraText = "";
	extraOverCmsTextSize = 0.76;
	extraTextFont = 52
	
	lumiText = "41.5 fb^{-1} (13 TeV)";
        if era == "2016APV":
                lumiText = "19.5 fb^{-1} (13 TeV)"; 
        if era == "2016postAPV":
                lumiText = "16.8 fb^{-1} (13 TeV)";
        if era == "2017":
                lumiText = "41.5 fb^{-1} (13 TeV)";
        if era == "2018":
                lumiText = "59.8 fb^{-1} (13 TeV)";
        if era == "2016merged":
                lumiText = "36.3 fb^{-1} (13 TeV)";
	lumiTextSize = 0.5;
	lumiTextOffset = 0.2;
	relExtraDY = 1.2;
	
	
	latex.SetTextAngle(0);
	latex.SetTextColor(kBlack);
	extraTextSize = extraOverCmsTextSize * cmsTextSize;
	latex.SetTextFont(42);

	latex.SetTextFont(42);
	latex.SetTextAlign(31);
	latex.SetTextSize(lumiTextSize * t);
	latex.DrawLatex(1 - r, 1 - t + lumiTextOffset * t, lumiText);
	
	latex.SetTextFont(cmsTextFont);
	latex.SetTextAlign(11);
	latex.SetTextSize(cmsTextSize * t);
	latex.DrawLatex(l, 1 - t + lumiTextOffset * t, cmsText);
	
	posX_ = 0
	posX_ = l + relPosX * (1 - l - r);
	posY_ = 1 - t - relPosY * (1 - t - b);
	posX_ = l + relPosX * (1 - l - r);
	posY_ = 1 - t + lumiTextOffset * t;
	alignX_ = 1;
	alignY_ = 1;
	align_ = 10 * alignX_ + alignY_;
	latex.SetTextFont(extraTextFont);
	latex.SetTextSize(extraTextSize * t);
	latex.SetTextAlign(align_);
	latex.DrawLatex(posX_, posY_, extraText);
	latex.SetTextAlign(31);
	latex.SetTextSize(lumiTextSize * t);
	return gPad

def addChannelText(gPad, channel='mm'):
        latex = TLatex();
        # cmsTextFont = 60;
        cmsTextSize = 0.6;
        latex.SetNDC()
        # latex.SetTextFont(42) #cmsTextFont)
        posX_ = 0.19
        posY_ = 0.55
        channelText = " "
        if channel == "mm":
                channelText = "\mu\mu"
        elif channel == "ee":
                channelText = "ee"
        else:
                channelText = "e\mu"
        latex.DrawLatex(posX_, posY_, channelText)
        latex.SetTextSize(cmsTextSize)
        return gPad
