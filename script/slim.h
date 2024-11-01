#include "ROOT/RDataFrame.hxx"
#include "ROOT/RVec.hxx"
#include "TCanvas.h"
#include "TH1D.h"
#include "TLatex.h"
#include "Math/Vector4D.h"
#include "Math/Vector4Dfwd.h"
#include "TStyle.h"
#include "TString.h"
#include "TVector2.h"
#include <algorithm>
#include <random>

using namespace ROOT;
using namespace std;
using namespace ROOT::VecOps;

using Vec_f = ROOT::VecOps::RVec<float>;
using Vec_i = ROOT::VecOps::RVec<int>;

TString era = "EraToBeReplaced";
std::mt19937 generator(1234); // Seed to guarantee reproducity
std::uniform_int_distribution<int> distribution(1, 1000);

// Trigger Scale Factor (Derived by ourselves)
TFile*f_trigger=TFile::Open("../../data/Trigger_scale_factor_"+era+"_summary.root");
TH2D*trigger_sf_electron_HLT_resolved = (TH2D*)f_trigger->Get("bh_Electron_scale_factor_total");
TH2D*trigger_sf_electron_HLT_boost    = (TH2D*)f_trigger->Get("boost_Electron_scale_factor_total");
TH2D*trigger_sf_muon_HLT_resolved     = (TH2D*)f_trigger->Get("bh_Muon_scale_factor_total");
TH2D*trigger_sf_muon_HLT_boost        = (TH2D*)f_trigger->Get("boost_Muon_scale_factor_total");
const float trigger_highest_pt = trigger_sf_electron_HLT_resolved->GetXaxis()->GetBinUpEdge(trigger_sf_electron_HLT_resolved->GetNbinsX());

// pileupjetid Scale Factor (Derived by JME)
// take root file from https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJetIDUL#Data_MC_Efficiency_Scale_Factors
TFile*f_pujetid=TFile::Open("../../data/PUID_106XTraining_ULRun2_EffSFandUncties_v1.root");
TString puhist = "SpecialEra";
TH2D*pujetid_sf               = (TH2D*)f_pujetid->Get("h2_eff_sfUL"+puhist+"_T");
TH2D*pujetid_sf_Systuncty     = (TH2D*)f_pujetid->Get("h2_eff_sfUL"+puhist+"_T_Systuncty");

// Btag Efficiency (Derived by ourgroup)
TFile*f_btag_efficiency=TFile::Open("../../data/BTagEfficiency_"+era+".root");
TH2D*btag_efficiency_loose_b = (TH2D*) (((TEfficiency*) f_btag_efficiency->Get("h2_LEff_b"))->CreateHistogram());
TH2D*btag_efficiency_loose_c = (TH2D*) (((TEfficiency*) f_btag_efficiency->Get("h2_LEff_c"))->CreateHistogram());
TH2D*btag_efficiency_loose_udsg = (TH2D*) (((TEfficiency*) f_btag_efficiency->Get("h2_LEff_udsg"))->CreateHistogram());
TH2D*btag_efficiency_medium_b = (TH2D*) (((TEfficiency*) f_btag_efficiency->Get("h2_MEff_b"))->CreateHistogram());
TH2D*btag_efficiency_medium_c = (TH2D*) (((TEfficiency*) f_btag_efficiency->Get("h2_MEff_c"))->CreateHistogram());
TH2D*btag_efficiency_medium_udsg = (TH2D*) (((TEfficiency*) f_btag_efficiency->Get("h2_MEff_udsg"))->CreateHistogram());
TH2D*btag_efficiency_tight_b = (TH2D*) (((TEfficiency*) f_btag_efficiency->Get("h2_TEff_b"))->CreateHistogram());
TH2D*btag_efficiency_tight_c = (TH2D*) (((TEfficiency*) f_btag_efficiency->Get("h2_TEff_c"))->CreateHistogram());
TH2D*btag_efficiency_tight_udsg = (TH2D*) (((TEfficiency*) f_btag_efficiency->Get("h2_TEff_udsg"))->CreateHistogram());
const float btag_efficiency_highest_pt  = btag_efficiency_loose_b->GetXaxis()->GetBinUpEdge(btag_efficiency_loose_b->GetNbinsX());

double delta_phi(double phi2, double phi1){
  float dphi = phi2 - phi1;
  if (fabs(dphi) > TMath::Pi()) dphi = 2*TMath::Pi() - fabs(dphi);
  return dphi;
}

int iArray(ROOT::VecOps::RVec<int> Array, int idx, int Is_pdgId = 0){
  if(idx < 0) return -99;
  int output = Array[idx];
  if(Is_pdgId == 1 and output == 5000003) return 26;
  if(Is_pdgId == 1 and output ==-5000003) return -26;
  return output;
}

float iArray(ROOT::VecOps::RVec<float> Array, int idx){
  if(idx < 0) return -99.;
  float output = Array[idx];
  return output;
}

double iArray(ROOT::VecOps::RVec<double> Array, int idx){
  if(idx < 0) return -99.;
  double output = Array[idx];
  return output;
}

template <typename T>T iArray(std::vector<T> Array, int idx, int Is_pdgId = 0){
  if(idx < 0) return T(-99);
  if(idx + 1 > Array.size()) return T(-99);
  if(Is_pdgId == 1 and Array[idx] == 5000003) return 26;
  if(Is_pdgId == 1 and Array[idx] ==-5000003) return -26;
  return Array[idx];
}

float deltaR(float eta1, float phi1, float eta2, float phi2){
  ROOT::Math::PtEtaPhiMVector p1(1.0, eta1, phi1, 0.0);
  ROOT::Math::PtEtaPhiMVector p2(1.0, eta2, phi2, 0.0);
  return ROOT::Math::VectorUtil::DeltaR(p1, p2); 
}

std::vector<int> match_idx(ROOT::VecOps::RVec<float> Input_pt, ROOT::VecOps::RVec<float> Input_eta, ROOT::VecOps::RVec<float> Input_phi, ROOT::VecOps::RVec<float> Ref_pt, ROOT::VecOps::RVec<float> Ref_eta, ROOT::VecOps::RVec<float> Ref_phi, float dr_cut, float pt_ratio_cut){

  // Function used for doing kinematic match of "Ref" particle to "Input" particle" 

  int nInput = Input_pt.size();
  int nRef   = Ref_pt.size();

  std::vector<int> match_idx;
  float dr, dr_temp, pt1, eta1, phi1, pt2, eta2, phi2;
  int idx;

  for(int i_input = 0; i_input < nInput; i_input++){

    dr = 100.;
    dr_temp = 100.;
    pt1 = Input_pt[i_input];
    eta1 = Input_eta[i_input];
    phi1 = Input_phi[i_input];
    idx  = -1;

    for(int i_ref = 0; i_ref < nRef; i_ref++){
      pt2 = Ref_pt[i_ref];
      eta2 = Ref_eta[i_ref];
      phi2 = Ref_phi[i_ref];
      dr_temp = deltaR(eta1, phi1, eta2, phi2);
      if (dr_temp < dr){
        dr = dr_temp;
        idx = i_ref;
      } 
    }
    
    if (dr < dr_cut and abs(Ref_pt[idx]-pt1)/pt1 < pt_ratio_cut){
      if (!(std::find(match_idx.begin(), match_idx.end(), idx) != match_idx.end())){
        match_idx.push_back(idx); // Matched GenLevel Object index
      } 
      else match_idx.push_back(-2); // Matched GenLevel Object but already assigned to higher Pt reco object.
    }
    else match_idx.push_back(-1); // UnMatched GenLevel Object
  }

  return match_idx;
}

std::vector<int> match_idx(ROOT::VecOps::RVec<float> Input_pt, ROOT::VecOps::RVec<float> Input_eta, ROOT::VecOps::RVec<float> Input_phi, ROOT::VecOps::RVec<float> Ref_pt, ROOT::VecOps::RVec<float> Ref_eta, ROOT::VecOps::RVec<float> Ref_phi, float dr_cut, float pt_ratio_cut, ROOT::VecOps::RVec<int> GenPart_statusFlags){

  // Function used for doing kinematic match of "Ref" particle to "Input" particle" 

  int nInput = Input_pt.size();
  int nRef   = Ref_pt.size();

  std::vector<int> match_idx;
  float dr, dr_temp, pt1, eta1, phi1, pt2, eta2, phi2;
  int idx;

  for(int i_input = 0; i_input < nInput; i_input++){

    dr = 100.;
    dr_temp = 100.;
    pt1 = Input_pt[i_input];
    eta1 = Input_eta[i_input];
    phi1 = Input_phi[i_input];
    idx  = -1;

    for(int i_ref = 0; i_ref < nRef; i_ref++){
      if(!((GenPart_statusFlags[i_ref]>>13)&1)) continue; // isLastCopy
      pt2 = Ref_pt[i_ref];
      eta2 = Ref_eta[i_ref];
      phi2 = Ref_phi[i_ref];
      dr_temp = deltaR(eta1, phi1, eta2, phi2);
      if (dr_temp < dr){
        dr = dr_temp;
        idx = i_ref;
      } 
    }
    
    if (dr < dr_cut and abs(Ref_pt[idx]-pt1)/pt1 < pt_ratio_cut){
      if (!(std::find(match_idx.begin(), match_idx.end(), idx) != match_idx.end())){
        match_idx.push_back(idx); // Matched GenLevel Object index
      } 
      else match_idx.push_back(-2); // Matched GenLevel Object but already assigned to higher Pt reco object.
    }
    else match_idx.push_back(-1); // UnMatched GenLevel Object
  }

  return match_idx;
}

std::vector<int> match_idx(ROOT::VecOps::RVec<int> Input_id, ROOT::VecOps::RVec<float> Input_pt, ROOT::VecOps::RVec<float> Input_eta, ROOT::VecOps::RVec<float> Input_phi, ROOT::VecOps::RVec<float> Ref_pt, ROOT::VecOps::RVec<float> Ref_eta, ROOT::VecOps::RVec<float> Ref_phi, float dr_cut, float pt_ratio_cut){

  // Function used for doing kinematic match of "Ref" particle to "Input" particle", dedicated for map_id_input (i.e. tightJets_id etc.)

  int nRef = Ref_pt.size();

  std::vector<int> match_idx;
  float dr, dr_temp, pt1, eta1, phi1, pt2, eta2, phi2;
  int idx, i_input;

  for(int i_input_ = 0; i_input_ < Input_id.size(); i_input_++){

    i_input = Input_id[i_input_];
    dr = 100.;
    dr_temp = 100.;
    pt1 = Input_pt[i_input];
    eta1 = Input_eta[i_input];
    phi1 = Input_phi[i_input];
    idx  = -1;

    for(int i_ref = 0; i_ref < nRef; i_ref++){
      pt2 = Ref_pt[i_ref];
      eta2 = Ref_eta[i_ref];
      phi2 = Ref_phi[i_ref];
      dr_temp = deltaR(eta1, phi1, eta2, phi2);
      if (dr_temp < dr){
        dr = dr_temp;
        idx = i_ref;
      } 
    }
    
    if (dr < dr_cut and abs(Ref_pt[idx]-pt1)/pt1 < pt_ratio_cut){
      if (!(std::find(match_idx.begin(), match_idx.end(), idx) != match_idx.end())){
        match_idx.push_back(idx); // Matched GenLevel Object index
      } 
      else match_idx.push_back(-2); // Matched GenLevel Object but already assigned to higher Pt reco object.
    }
    else match_idx.push_back(-1); // UnMatched GenLevel Object
  }

  return match_idx;
}



std::vector<int> match_idx_parton(ROOT::VecOps::RVec<int> GenPart_genPartIdxMother, ROOT::VecOps::RVec<int> GenPart_pdgId, ROOT::VecOps::RVec<int> GenPart_statusFlags){

  // Find mother particle id for genPart
  int nGenPart = GenPart_genPartIdxMother.size();
  std::vector<int> match_idx;
  int daughter_id, daughter_statusflags, mother_idx, mother_id, mother_statusflags;
  bool isdaughter_HardProcess;

  for(int index_ = 0; index_ < nGenPart; index_++){
    daughter_id = abs(iArray(GenPart_pdgId, index_));
    daughter_statusflags = GenPart_statusFlags[index_];

    isdaughter_HardProcess = (daughter_statusflags>>7)&1;
  //  if(!(isdaughter_HardProcess)){
  //    match_idx.push_back(-1);
  //    continue;
  //  }

    mother_idx = GenPart_genPartIdxMother[index_];
    mother_id  = abs(iArray(GenPart_pdgId, mother_idx));
    
    while(mother_id == daughter_id){
      mother_idx = GenPart_genPartIdxMother[mother_idx];
      mother_id  = abs(iArray(GenPart_pdgId, mother_idx));
      
    }

    if(mother_idx < 0){
      match_idx.push_back(-1);
      continue;
    }
    match_idx.push_back(mother_idx);
  }

  return match_idx;

}

float top_ptweight(Vec_f& genPart_pt, Vec_i& genPart_pdgId, Vec_i& genPart_status, Vec_i& genPart_statusFlags){
  
  int daughter_id, daughter_status;
  bool isdaughter_lastcopy;
  float gentoppt = 0.0, genantitoppt = 0.0, maxtoppt = 500.0, weight = 1.0, w1 = 1.0, w2 = 1.0;
  
  for(int index_ = 0; index_ < genPart_pdgId.size(); index_++){
    daughter_id     = genPart_pdgId[index_];
    daughter_status = genPart_status[index_];
    isdaughter_lastcopy    = (genPart_statusFlags[index_]>>13) & 0x1;

    if (isdaughter_lastcopy && abs(daughter_id) == 6){
      //cout << "Particle id: " << daughter_id << std::endl;
      //cout << "Particle status: " << daughter_status << std::endl;
      //cout << "Particle pt: " << genPart_pt[index_] << std::endl;
      if (daughter_id == 6){
	gentoppt = genPart_pt[index_];
	w1 = exp(0.0615 - 0.0005 * TMath::Min(gentoppt, maxtoppt));
	//cout << "w1: " << w1 << endl;
      }
      if (daughter_id == -6){
	genantitoppt = genPart_pt[index_];
	w2 = exp(0.0615 - 0.0005 * TMath::Min(genantitoppt, maxtoppt));
	//cout << "w2: " << w2 << endl;
      }
      weight = sqrt(w1*w2);
      //cout << "weight (intermediate): " << weight << endl;
      //return weight; //not correct (because you consider only one top)
    }
  }
  //cout << "weight (final): " << weight << endl;
  return weight;
}

int match_reco_parton(int Reco_index, std::vector<int> Gen_Reco_match, std::vector<int> Part_Gen_match){
  
  // Function used for mapping reco object to mother parton

  int gen_index = Gen_Reco_match[Reco_index];
  if(gen_index < 0) return -1;
  int part_index = Part_Gen_match[gen_index];
  if(part_index < 0) return -1;
  return part_index;
}

int match_parton_to_reco(int parton_pdgid,  int reco_pt_order, std::vector<int> Gen_Reco_match, std::vector<int> Part_Gen_match, std::vector<int> Part_mother_match, ROOT::VecOps::RVec<int> GenPart_pdgId){

  int parton_index, iparton;
  std::vector<int> reco_candidate;
  for(int iReco=0; iReco < Gen_Reco_match.size(); iReco++){
    iparton = match_reco_parton(iReco, Gen_Reco_match, Part_Gen_match);
    while(iparton>0){
      if (abs(GenPart_pdgId[iparton]) == parton_pdgid){
        reco_candidate.push_back(iReco);
        break;
      }
      iparton = Part_mother_match[iparton];
    }
  }
  if(reco_candidate.size() < (reco_pt_order + 1)){
    return -1;
  }
  else return reco_candidate[reco_pt_order];

}



std::vector<int> particle_cv(int iPart, std::vector<int> Part_mother_match, ROOT::VecOps::RVec<int> GenPart_pdgId){
  std::vector<int> cv;
  if (iPart < 0){
    cv.push_back(-1);
    return cv;
  }
  cv.push_back(abs(GenPart_pdgId[iPart]));
  int mother_idx = Part_mother_match[iPart];
  while(mother_idx > -1){ 
    cv.push_back(abs(GenPart_pdgId[mother_idx]));
    mother_idx = Part_mother_match[mother_idx];
  }
  cv.push_back(-1);
  return cv;
}

std::vector<int> search_parton_cv(std::vector<int> Part_mother_match, ROOT::VecOps::RVec<int> GenPart_pdgId, ROOT::VecOps::RVec<int> GenPart_statusFlags, std::vector<int> target_process){
  // input: target_process should be the vector like [5,6,50003], which indicate we are searching for the b quarks following H+ > t > b decay chain
  std::vector<int> target_parton;
  for(int iPart=0; iPart < GenPart_pdgId.size(); iPart++){
    bool Flag = true;
    bool isdaughter_prompt      = (GenPart_statusFlags[iPart]>>0)&1;
    bool isdaughter_HardProcess = (GenPart_statusFlags[iPart]>>7)&1;
    bool isdaughter_lastcopy    = (GenPart_statusFlags[iPart]>>13)&1;
  //  if(!(isdaughter_prompt && isdaughter_lastcopy)) continue;
    if(!(isdaughter_lastcopy)) continue;
    std::vector<int> cv = particle_cv(iPart, Part_mother_match, GenPart_pdgId);
    for(int itarget = 0; itarget < target_process.size(); itarget++){
      if(target_process[itarget] != cv[itarget]) Flag = false;
    }
    if(Flag) target_parton.push_back(iPart);
  }
  if(target_parton.size() == 0) target_parton.push_back(-1);
  return target_parton;
}

int MET_part_index(std::vector<int> Part_mother_match, ROOT::VecOps::RVec<int> GenPart_pdgId){
  for(int ipart = 0; ipart < GenPart_pdgId.size(); ipart++){
    int part_pdgId = abs(GenPart_pdgId[ipart]);
    int mother_pdgId = abs(iArray(GenPart_pdgId, Part_mother_match[ipart], 1));
    if(!(mother_pdgId==24)) continue;
    if((part_pdgId == 12) or (part_pdgId == 14)) return ipart;
  }
  return -1;
}

int compare_reco_to_parton(int reco_index, std::vector<int> parton_indices, ROOT::VecOps::RVec<float> Jet_eta, ROOT::VecOps::RVec<float> Jet_phi, ROOT::VecOps::RVec<float> GenPart_eta, ROOT::VecOps::RVec<float> GenPart_phi, float dr){
  if (parton_indices.size() < 1) return -2;
  if (reco_index < 0) return -1;
  float jet_eta = Jet_eta[reco_index];
  float jet_phi = Jet_phi[reco_index];
  for (int ipart = 0; ipart < parton_indices.size(); ipart++){
    float part_eta = GenPart_eta[parton_indices[ipart]];
    float part_phi = GenPart_phi[parton_indices[ipart]];
    if (deltaR(part_eta, part_phi, jet_eta, jet_phi) < dr) return 1;
  }
  return 0;
}

float MET_pz_reconstruction(float l_pt, float l_eta, float l_phi, float MET, float MET_phi){

 //////////////////////////////////////////
 // Ref: CMS-TOP-19-009 & CMS-TOP-20-007 //
 //////////////////////////////////////////
 
  float mW = 80.4;
  float Lambda = mW*mW/2. + (l_pt * MET * cos(l_phi - MET_phi));
  float l_pz = l_pt * sinh(l_eta);
  float l_E  = sqrt(l_pz*l_pz + l_pt*l_pt);
  float D = Lambda*Lambda*l_pz*l_pz + l_pt*l_pt*(Lambda*Lambda - l_E * l_E * MET * MET);
  float A = Lambda*l_pz/(l_pt*l_pt);
  if(D < 0) return A;
  else{ 
    if(abs(A + sqrt(D)/(l_pt*l_pt)) > abs(A - sqrt(D)/(l_pt*l_pt))){
      return A - sqrt(D)/(l_pt*l_pt);
    }
    else return A + sqrt(D)/(l_pt*l_pt);
  }
}




ROOT::VecOps::RVec<Float_t> top_reconstruction(float W_E, float W_px, float W_py, float W_pz, ROOT::VecOps::RVec<float> b_jet_id, ROOT::VecOps::RVec<float> tight_jet_id, ROOT::VecOps::RVec<float> Jet_pt, ROOT::VecOps::RVec<float> Jet_eta, ROOT::VecOps::RVec<float> Jet_phi, ROOT::VecOps::RVec<float> Jet_mass){

  float top_E = -1.;
  float top_px = -1.;
  float top_py = -1.;
  float top_pz = -1.;
  float top_mass = -999999.;
  float mT = 172.69; //PDG 2023
  float jet_pt, jet_eta, jet_phi, jet_mass, jet_e, jet_px, jet_py, jet_pz;
  float top_e_tmp, top_px_tmp, top_py_tmp, top_pz_tmp, top_mass_tmp;
  float H_E, H_px, H_py, H_pz;
  float H_mass = -99.;
  int b_jet_cand_idx = -1;
  int b_jet_cand_idx_Hplus = -1;
  ROOT::Math::PxPyPzEVector Wjet(W_px, W_py, W_pz, W_E);
  ROOT::Math::PtEtaPhiMVector top;

  for(int ijet = 0; ijet < b_jet_id.size(); ijet++){
    int jet_idx = b_jet_id[ijet];
    if(jet_idx < 0) continue;
    ROOT::Math::PtEtaPhiMVector jet(Jet_pt[jet_idx], Jet_eta[jet_idx], Jet_phi[jet_idx], Jet_mass[jet_idx]);
    ROOT::Math::PtEtaPhiMVector top_tmp = jet + Wjet;
    top_mass_tmp = top_tmp.M();
    if(abs(top_mass_tmp - mT) < abs(top_mass - mT)){
      top_mass = top_mass_tmp;
      b_jet_cand_idx = jet_idx;
      top = top_tmp;
    }
  }

  if(b_jet_id.size() > 1){
      for(int ijet = 0; ijet < b_jet_id.size(); ijet++){
        int jet_idx = b_jet_id[ijet];
        if(jet_idx < 0) continue;
        if(jet_idx == b_jet_cand_idx) continue;
        ROOT::Math::PtEtaPhiMVector jet(Jet_pt[jet_idx], Jet_eta[jet_idx], Jet_phi[jet_idx], Jet_mass[jet_idx]);
        ROOT::Math::PtEtaPhiMVector Hplus = top + jet;
        if(Hplus.M() > H_mass){
          H_mass = Hplus.M();
          b_jet_cand_idx_Hplus = jet_idx;

        }
      }
  }
  else{
       for(int ijet = 0; ijet < tight_jet_id.size(); ijet++){
        int jet_idx = tight_jet_id[ijet];
        if(jet_idx < 0) continue;
        if(jet_idx == b_jet_cand_idx) continue;
        ROOT::Math::PtEtaPhiMVector jet(Jet_pt[jet_idx], Jet_eta[jet_idx], Jet_phi[jet_idx], Jet_mass[jet_idx]);
        ROOT::Math::PtEtaPhiMVector Hplus = top + jet;
        if(Hplus.M() > H_mass){
          H_mass = Hplus.M();
          b_jet_cand_idx_Hplus = jet_idx;
        }
     }
  }
  ROOT::VecOps::RVec<Float_t> return_out = {(float) top.M(), (float) top.Pt(), (float) b_jet_cand_idx, (float) H_mass, (float) b_jet_cand_idx_Hplus};
  return return_out;
}



//////////////////////
//  LHE level study //
//////////////////////

int find_b_inLHE(ROOT::VecOps::RVec<float> LHEPart_pt, ROOT::VecOps::RVec<float> LHEPart_eta, ROOT::VecOps::RVec<float> LHEPart_phi, ROOT::VecOps::RVec<float> LHEPart_mass, ROOT::VecOps::RVec<int> LHEPart_pdgId, ROOT::VecOps::RVec<int> LHEPart_status, float H_mass, int mode){

  // mode 0: return b from top index
  // mode 1: return b from H   index
  // mode 2: return b from C   index

  int lepton_idx = -1;
  int neutrino_idx = -1;

  for(int iPart = 0; iPart < LHEPart_pdgId.size(); iPart++){
    if (abs(LHEPart_pdgId[iPart]) == 11 || abs(LHEPart_pdgId[iPart])==13) lepton_idx = iPart;
    if (abs(LHEPart_pdgId[iPart]) == 12 || abs(LHEPart_pdgId[iPart])==14) neutrino_idx = iPart;
  }

  if ((lepton_idx == -1) || (neutrino_idx == -1)) return -1;

  ROOT::Math::PtEtaPhiMVector lepton(LHEPart_pt[lepton_idx], LHEPart_eta[lepton_idx], LHEPart_phi[lepton_idx], LHEPart_mass[lepton_idx]);
  ROOT::Math::PtEtaPhiMVector neutrino(LHEPart_pt[neutrino_idx], LHEPart_eta[neutrino_idx], LHEPart_phi[neutrino_idx], LHEPart_mass[neutrino_idx]);
  ROOT::Math::PtEtaPhiMVector W_boson = lepton + neutrino;

  // Find b from top
  float mT = 172.69; //PDG 2023
  float inv_mass_tmp = -99;
  int b_from_top_idx = -1;

  for(int iPart = 0; iPart < LHEPart_pdgId.size(); iPart++){
    if (!(abs(LHEPart_pdgId[iPart]) == 5)) continue;
    if (LHEPart_status[iPart] == -1) continue;
    ROOT::Math::PtEtaPhiMVector b_from_top(LHEPart_pt[iPart], LHEPart_eta[iPart], LHEPart_phi[iPart], LHEPart_mass[iPart]);    
    if( abs((b_from_top + W_boson).M() - mT) < abs(inv_mass_tmp - mT) ){
      b_from_top_idx = iPart;
      inv_mass_tmp = (b_from_top + W_boson).M();
    } 
  }

  if (b_from_top_idx == -1) return -1;
  ROOT::Math::PtEtaPhiMVector b_from_top(LHEPart_pt[b_from_top_idx], LHEPart_eta[b_from_top_idx], LHEPart_phi[b_from_top_idx], LHEPart_mass[b_from_top_idx]);
  ROOT::Math::PtEtaPhiMVector top = b_from_top + W_boson;

  // Find b from H+
  inv_mass_tmp = -999999.;
  int b_from_H_idx = -1;
  for(int iPart = 0; iPart < LHEPart_pdgId.size(); iPart++){
    if (!(abs(LHEPart_pdgId[iPart]) == 5)) continue;
    if (LHEPart_status[iPart] == -1) continue;
    ROOT::Math::PtEtaPhiMVector b_from_H(LHEPart_pt[iPart], LHEPart_eta[iPart], LHEPart_phi[iPart], LHEPart_mass[iPart]);    
    if( abs((b_from_H + top).M() - H_mass) < abs(inv_mass_tmp - H_mass) ){
      b_from_H_idx = iPart;
      inv_mass_tmp = (b_from_H + top).M();
    } 
  }

  if (b_from_H_idx == -1 || (b_from_H_idx == b_from_top_idx)) return -1;
  ROOT::Math::PtEtaPhiMVector b_from_H(LHEPart_pt[b_from_H_idx], LHEPart_eta[b_from_H_idx], LHEPart_phi[b_from_H_idx], LHEPart_mass[b_from_H_idx]);
  ROOT::Math::PtEtaPhiMVector H = b_from_H + top;

  // Find b from C
  int b_from_C_idx = -1;
  int n_b_from_C = 0;
  for(int iPart = 0; iPart < LHEPart_pdgId.size(); iPart++){
    if (!(abs(LHEPart_pdgId[iPart]) == 5)) continue;
    if (LHEPart_status[iPart] == -1) continue;
    if ((iPart == b_from_H_idx) || (iPart == b_from_top_idx)) continue;
    b_from_C_idx = iPart;
    n_b_from_C += 1;
  }
  if(n_b_from_C > 1) return -1;

  if(mode == 0) return b_from_top_idx;
  else if (mode== 1) return b_from_H_idx;
  else return b_from_C_idx;
}

//////////
//  HT  //
//////////

float HT_(ROOT::VecOps::RVec<Int_t> jetid, ROOT::VecOps::RVec<float> jetpt)
{
  float ht=0.;
  for (int i=0; i<jetid.size();i++)
  {if(jetid[i]<0) continue;
    ht+=jetpt[jetid[i]];
  }
  return ht;
}

ROOT::VecOps::RVec<Int_t> select_btag_jet_wo_lepton_dr_cut(ROOT::VecOps::RVec<Int_t> Jet_jetId, ROOT::VecOps::RVec<Int_t> Jet_puId, ROOT::VecOps::RVec<Float_t> Jet_pt, ROOT::VecOps::RVec<Float_t> Jet_eta, ROOT::VecOps::RVec<Float_t> Jet_btagDeepFlavB){
  ROOT::VecOps::RVec<Int_t> return_id;
  float eta_cut = 2.4;
  if ((era == "2017") || (era == "2018")) eta_cut = 2.5;
  
  float btag_cut_medium = 0.3040; //2017
  if(era == "2016apv") btag_cut_medium = 0.2598;
  else if (era == "2016postapv") btag_cut_medium = 0.2489;
  else if (era == "2018") btag_cut_medium = 0.2783;



  for(int i = 0; i < Jet_jetId.size(); i++){
    if(abs(Jet_eta[i]) > eta_cut) continue;
    if(Jet_pt[i] < 30) continue;
    if((Jet_pt[i] < 50) && !(Jet_puId[i] == 7)) continue;
    if(!(Jet_jetId[i] == 6)) continue;
    if(Jet_btagDeepFlavB[i] > btag_cut_medium) return_id.push_back(i);
  }

  return return_id;
}

///////////////
//  BTag SF  //
///////////////

ROOT::VecOps::RVec<Int_t> reselect_btag_jet(ROOT::VecOps::RVec<Int_t> jetid){
  ROOT::VecOps::RVec<Int_t> return_id;
  for(int i = 0; i < jetid.size(); i++){
    if (jetid[i] < 0) continue;
    return_id.push_back(jetid[i]);
  }
  return return_id;
}


float btag_SF(ROOT::VecOps::RVec<Int_t> tight_jet_id, ROOT::VecOps::RVec<Int_t> b_jet_id, ROOT::VecOps::RVec<float> btag_sf, ROOT::VecOps::RVec<Int_t> jethadflav, ROOT::VecOps::RVec<float> Jet_pt, ROOT::VecOps::RVec<float> Jet_eta, int wp, ROOT::VecOps::RVec<float> btag_sf_var, int variation){
  float sf = 1.0;
  int hadflav, idx;
  bool isbtag;
  float efficiency, pt, eta;
  for(int i=0; i < tight_jet_id.size(); i++){
    idx = tight_jet_id[i];
    if(idx<0) continue;
    isbtag = false;
    pt     = std::min(Jet_pt[idx],btag_efficiency_highest_pt);
    eta    = Jet_eta[idx];
    for(int j=0; j < b_jet_id.size(); j++){
      if (b_jet_id[j] == idx){
        isbtag = true;
	continue;
      }
    }
    
    if(jethadflav[idx] == 5){
      if(wp == 1) efficiency = btag_efficiency_loose_b->GetBinContent(btag_efficiency_loose_b->FindBin(pt, abs(eta)));
      if(wp == 2) efficiency = btag_efficiency_medium_b->GetBinContent(btag_efficiency_medium_b->FindBin(pt, abs(eta)));
      if(wp == 3) efficiency = btag_efficiency_tight_b->GetBinContent(btag_efficiency_tight_b->FindBin(pt, abs(eta)));
    }
    else if(jethadflav[idx] == 4){
      if(wp == 1) efficiency = btag_efficiency_loose_c->GetBinContent(btag_efficiency_loose_c->FindBin(pt, abs(eta)));
      if(wp == 2) efficiency = btag_efficiency_medium_c->GetBinContent(btag_efficiency_medium_c->FindBin(pt, abs(eta)));
      if(wp == 3) efficiency = btag_efficiency_tight_c->GetBinContent(btag_efficiency_tight_c->FindBin(pt, abs(eta)));
    }
    else{
      if(wp == 1) efficiency = btag_efficiency_loose_udsg->GetBinContent(btag_efficiency_loose_udsg->FindBin(pt, abs(eta)));
      if(wp == 2) efficiency = btag_efficiency_medium_udsg->GetBinContent(btag_efficiency_medium_udsg->FindBin(pt, abs(eta)));
      if(wp == 3) efficiency = btag_efficiency_tight_udsg->GetBinContent(btag_efficiency_tight_udsg->FindBin(pt, abs(eta)));
    }

    if(isbtag){
      if(variation == 0) sf *= btag_sf[idx]; // nominal
      else if (variation == 1){  // flav udsg vary
	if((jethadflav[idx] == 5) || (jethadflav[idx] == 4)) sf *= btag_sf[idx];
        else {sf *= btag_sf_var[idx];}
      }
      else{ // flav c & b vary
        if((jethadflav[idx] == 5) || (jethadflav[idx] == 4)) sf *= btag_sf_var[idx];
	else {sf *= btag_sf[idx];};
      }
    }      
    else{
      if(variation == 0) sf *= (1.0 - (btag_sf[idx]*efficiency))/(1.0 - efficiency);
      else if (variation == 1){
        if((jethadflav[idx] == 5) || (jethadflav[idx] == 4)) sf *= (1.0 - (btag_sf[idx]*efficiency))/(1.0 - efficiency);
	else {sf *= (1.0 - (btag_sf_var[idx]*efficiency))/(1.0 - efficiency);}
      }
      else{
        if((jethadflav[idx] == 5) || (jethadflav[idx] == 4)) sf *= (1.0 - (btag_sf_var[idx]*efficiency))/(1.0 - efficiency);
        else {sf *= (1.0 - (btag_sf[idx]*efficiency))/(1.0 - efficiency);}
      }
    }
  }
  return sf;
}

//////////////////
//  Trigger SF  //
//////////////////

float trigger_SF(float pt, float eta, int boost_region, int resolved_region, float variation)
{
  if(pt > trigger_highest_pt) pt = trigger_highest_pt-1.0;
  float trigger_weight = 1.0;
  float central_weight = 1.0;
  float weight_error   = 1.0;

  if((boost_region == -1) && (resolved_region == 1)){
    central_weight = trigger_sf_muon_HLT_resolved->GetBinContent(trigger_sf_muon_HLT_resolved->FindBin(pt, abs(eta)));
    weight_error   = trigger_sf_muon_HLT_resolved->GetBinError(trigger_sf_muon_HLT_resolved->FindBin(pt, abs(eta)));
    trigger_weight *= (central_weight + variation*weight_error);
  }
  else if((boost_region == -1) && (resolved_region == 2)){
    central_weight = trigger_sf_electron_HLT_resolved->GetBinContent(trigger_sf_electron_HLT_resolved->FindBin(pt, abs(eta)));
    weight_error   = trigger_sf_electron_HLT_resolved->GetBinError(trigger_sf_electron_HLT_resolved->FindBin(pt, abs(eta)));
    trigger_weight *= (central_weight + variation*weight_error);
  }
  else if((resolved_region == -1) && (boost_region == 1)){
    central_weight = trigger_sf_muon_HLT_boost->GetBinContent(trigger_sf_muon_HLT_boost->FindBin(pt, abs(eta)));
    weight_error   = trigger_sf_muon_HLT_boost->GetBinError(trigger_sf_muon_HLT_boost->FindBin(pt, abs(eta)));
    trigger_weight *= (central_weight + variation*weight_error);
  }
  else if((resolved_region == -1) && (boost_region == 2)){
    central_weight = trigger_sf_electron_HLT_boost->GetBinContent(trigger_sf_electron_HLT_boost->FindBin(pt, abs(eta)));
    weight_error   = trigger_sf_electron_HLT_boost->GetBinError(trigger_sf_electron_HLT_boost->FindBin(pt, abs(eta)));
    trigger_weight *= (central_weight + variation*weight_error);
   }
  return trigger_weight;
}

//////////////////
//  Pileupjetid SF  //
//////////////////

float pujetid_SF(ROOT::VecOps::RVec<float> tight_jet_id, ROOT::VecOps::RVec<float> Jet_pt, ROOT::VecOps::RVec<float> Jet_eta, ROOT::VecOps::RVec<int> Jet_genJetIdx, int boost_region, int resolved_region, float variation)
{
  float jet_pt, jet_eta;
  float pujetid_weight = 1.0;
  float central_weight = 1.0;
  float weight_error   = 1.0;
  
  for(int ijet = 0; ijet < tight_jet_id.size(); ijet++){
    int jet_idx = tight_jet_id[ijet];
    if(jet_idx < 0) continue;
    jet_pt = Jet_pt[jet_idx];
    jet_eta = Jet_eta[jet_idx];
    if (Jet_genJetIdx[jet_idx] == -1) continue;
    // cout << "Jet_genJetIdx[jet_idx]: " << Jet_genJetIdx[jet_idx] << endl;
    // cout << "jet_pt : " << jet_pt <<  endl;
    // cout << "jet_eta: " << jet_eta <<  endl;
    if(jet_pt > 50.0 || jet_pt < 20) pujetid_weight *= 1.0;

    else{
      central_weight = pujetid_sf->GetBinContent(pujetid_sf->FindBin(jet_pt, abs(jet_eta)));
      // cout << "central_weight: " << central_weight << endl;
      weight_error   = pujetid_sf_Systuncty->GetBinContent(pujetid_sf_Systuncty->FindBin(jet_pt, abs(jet_eta)));
      pujetid_weight *= (central_weight + variation*weight_error);
      // cout << "pujetid_weight: " << pujetid_weight << endl;
    }
  }
  return pujetid_weight;
}


///////////////
//  deltaR  //
//////////////

ROOT::VecOps::RVec<Float_t> Diobject_kinematic(float l1_pt, float l1_eta, float l1_phi, float l1_mass, ROOT::VecOps::RVec<Float_t> Jet_pt, ROOT::VecOps::RVec<Float_t> Jet_eta, ROOT::VecOps::RVec<Float_t> Jet_phi, ROOT::VecOps::RVec<Float_t> Jet_mass, ROOT::VecOps::RVec<Float_t> Jet_FlavB, ROOT::VecOps::RVec<Int_t> tight_jet_id, ROOT::VecOps::RVec<Int_t> b_jet_id, float MET_phi){

  float deltaR_lb[3] = {-99., -99., -99.};
  float deltaR_b1b2 = -99.;
  float deltaR_b2b3 = -99.;
  float deltaR_b1b3 = -99.;

  float non_b_j1_pt = -99.;
  float non_b_j1_eta = -99.;
  float non_b_j1_phi = -99.;
  float non_b_j1_mass = -99.;
  float non_b_j1_FlavB = -99.;
  float deltaR_non_b_l = -99.;


  float bjet_pt[3]   = {-99., -99., -99.};
  float bjet_eta[3]  = {-99., -99., -99.};
  float bjet_phi[3]  = {-99., -99., -99.};
  float bjet_mass[3] = {-99., -99., -99.};
  float bjet_FlavB[3]  = {-99., -99., -99.};

  int b_jet_idx = 0;
  bool is_btag;
  std::vector<int> new_b_id;
  int non_b_jet_idx = -1;
  int jet_idx;

  float inv_mass_lb[3] = {-99., -99., -99.};
  float inv_mass_b1b2 = -99.;
  float inv_mass_b2b3 = -99.;
  float inv_mass_b1b3 = -99.;
  float inv_mass_non_b_l = -99.;
  float inv_mass_lb1b2 = -99.;
  float inv_mass_lb2b3 = -99.;
  float inv_mass_lb1b3 = -99.;



  float delta_phi_l_met = fabs(delta_phi(l1_phi, MET_phi));

  ROOT::Math::PtEtaPhiMVector lepton(l1_pt, l1_eta, l1_phi, l1_mass);
  ROOT::Math::PtEtaPhiMVector bjet[3];
  ROOT::Math::PtEtaPhiMVector non_b_jet;

  for(int idx; idx < tight_jet_id.size(); idx++){
    jet_idx = tight_jet_id[idx];
    if(jet_idx < 0) continue;
    is_btag = (std::find(b_jet_id.begin(), b_jet_id.end(), jet_idx) != b_jet_id.end());
    if((is_btag) && (b_jet_idx < 3)){
      bjet[b_jet_idx] = ROOT::Math::PtEtaPhiMVector(Jet_pt[jet_idx], Jet_eta[jet_idx], Jet_phi[jet_idx], Jet_mass[jet_idx]);

      bjet_pt[b_jet_idx]   = bjet[b_jet_idx].Pt();
      bjet_eta[b_jet_idx]  = bjet[b_jet_idx].Eta();
      bjet_phi[b_jet_idx]  = bjet[b_jet_idx].Phi();
      bjet_mass[b_jet_idx] = bjet[b_jet_idx].M();

      bjet_FlavB[b_jet_idx]  = Jet_FlavB[jet_idx];

      deltaR_lb[b_jet_idx] = ROOT::Math::VectorUtil::DeltaR(bjet[b_jet_idx], lepton);
      inv_mass_lb[b_jet_idx] = (lepton + bjet[b_jet_idx]).M(); 
      b_jet_idx += 1;
      new_b_id.push_back(jet_idx);
    }  
    else if(non_b_jet_idx < 0){
      non_b_jet     = ROOT::Math::PtEtaPhiMVector(Jet_pt[jet_idx], Jet_eta[jet_idx], Jet_phi[jet_idx], Jet_mass[jet_idx]);
      non_b_j1_pt   = non_b_jet.Pt();
      non_b_j1_eta  = non_b_jet.Eta();
      non_b_j1_phi  = non_b_jet.Phi();
      non_b_j1_mass = non_b_jet.M();
      non_b_j1_FlavB  = Jet_FlavB[jet_idx];
      deltaR_non_b_l = ROOT::Math::VectorUtil::DeltaR(non_b_jet, lepton);
      inv_mass_non_b_l = (non_b_jet + lepton).M();
      non_b_jet_idx = jet_idx;
    }  
  }

  if(new_b_id.size() > 1){
    deltaR_b1b2 = ROOT::Math::VectorUtil::DeltaR(bjet[0], bjet[1]);
    inv_mass_b1b2 = (bjet[0] + bjet[1]).M();
    inv_mass_lb1b2 = (lepton + bjet[0] + bjet[1]).M();
    if (new_b_id.size() > 2){
      deltaR_b1b3 = ROOT::Math::VectorUtil::DeltaR(bjet[0], bjet[2]);
      deltaR_b2b3 = ROOT::Math::VectorUtil::DeltaR(bjet[1], bjet[2]);
      inv_mass_b1b3 = (bjet[0] + bjet[2]).M();
      inv_mass_b2b3 = (bjet[1] + bjet[2]).M();
      inv_mass_lb1b3 = (bjet[0] + bjet[2] + lepton).M();
      inv_mass_lb2b3 = (bjet[1] + bjet[2] + lepton).M();
    }
  }

  ROOT::VecOps::RVec<Float_t> final_return = {deltaR_lb[0], deltaR_lb[1], deltaR_lb[2], deltaR_b1b2, deltaR_b2b3, deltaR_b1b3, deltaR_non_b_l, non_b_j1_pt, non_b_j1_eta, non_b_j1_phi, non_b_j1_mass, bjet_pt[0], bjet_eta[0], bjet_phi[0], bjet_mass[0], bjet_pt[1], bjet_eta[1], bjet_phi[1], bjet_mass[1], bjet_pt[2], bjet_eta[2], bjet_phi[2], bjet_mass[2], bjet_FlavB[0], bjet_FlavB[1], bjet_FlavB[2], non_b_j1_FlavB, inv_mass_b1b2, inv_mass_b2b3, inv_mass_b1b3, inv_mass_lb1b2, inv_mass_lb2b3, inv_mass_lb1b3, inv_mass_non_b_l, delta_phi_l_met, inv_mass_lb[0], inv_mass_lb[1], inv_mass_lb[2]};

  return final_return; 


}

vector<float> SoftMax(vector<float> inV){
  vector<float> outV;
  float sum = 0.;
  for(int i = 0; i < inV.size(); i++){
    sum += exp(inV[i]);
  }
  for(int i =0; i < inV.size(); i++){
    if(sum > 0) outV.push_back((exp(inV[i])/sum));
    else outV.push_back(0.0);
  }
  return outV;
}

int ArgMax(vector<float> inV){
  int index = -1;
  float current_max = -999999.;
  for(int i = 0; i < inV.size(); i++){
    if(inV[i] > current_max){
      current_max = inV[i];
      index = i;
    }
  }
  return index;
}



///////////////////////
//  PDF Uncertainty  //
///////////////////////

float PDF_Uncertainty(ROOT::VecOps::RVec<Float_t> LHEPdfWeight){

  float rms_hes = 0;
  for(int i = 1; i < 101; i++){
    if (!(abs(LHEPdfWeight[i]) < 2)) rms_hes += 1;
    else rms_hes += pow((LHEPdfWeight[i] - LHEPdfWeight[0]) , 2);
  } 

  float alpha_var = (LHEPdfWeight[102] - LHEPdfWeight[101])/2.;
  if (abs(alpha_var) > 10) alpha_var = 0.05;
  return sqrt(rms_hes + alpha_var*alpha_var);
}

int Assign_Train_Label(float prob_2b, float prob_3b, int num_b){
  int assign_train = 0;
  int random_number = distribution(generator);

  if(num_b > 2){
    if((random_number / 1000.) < prob_3b) assign_train = 1;
  }
  else if(num_b == 2){
    if((random_number / 1000.) < prob_2b) assign_train = 1;
  }
  return assign_train;
}

float METXYCorr_Met_MetPhi(double uncormet, double uncormet_phi, int runnb, int npv, TString year="EraToBeReplaced"){
  if(npv>100) npv=100; // in nanoAOD, npv must be taken from PV_npvs
  TString runera = "";
  bool isMC = true;
  if(runnb > 10) isMC = false; 
  if(isMC && year == "2016apv") runera = "yUL2016MCAPV";
  else if(isMC && year == "2016postapv") runera = "yUL2016MCnonAPV";
  else if(isMC && year == "2017") runera = "yUL2017MC";
  else if(isMC && year == "2018") runera = "yUL2018MC";
  // UL 2018 data
  else if(!isMC && runnb >=315252 && runnb <=316995) runera = "yUL2018A";
  else if(!isMC && runnb >=316998 && runnb <=319312) runera = "yUL2018B";
  else if(!isMC && runnb >=319313 && runnb <=320393) runera = "yUL2018C";
  else if(!isMC && runnb >=320394 && runnb <=325273) runera = "yUL2018D";
  // UL 2017 data
  else if(!isMC && runnb >=297020 && runnb <=299329) runera = "yUL2017B";
  else if(!isMC && runnb >=299337 && runnb <=302029) runera = "yUL2017C";
  else if(!isMC && runnb >=302030 && runnb <=303434) runera = "yUL2017D";
  else if(!isMC && runnb >=303435 && runnb <=304826) runera = "yUL2017E";
  else if(!isMC && runnb >=304911 && runnb <=306462) runera = "yUL2017F";
  // UL 2016 data
  else if(!isMC && runnb >=272007 && runnb <=275376) runera = "yUL2016B";
  else if(!isMC && runnb >=275657 && runnb <=276283) runera = "yUL2016C";
  else if(!isMC && runnb >=276315 && runnb <=276811) runera = "yUL2016D";
  else if(!isMC && runnb >=276831 && runnb <=277420) runera = "yUL2016E";
  else if(!isMC && ((runnb >=277772 && runnb <=278768) || runnb==278770)) runera = "yUL2016F";
  else if(!isMC && ((runnb >=278801 && runnb <=278808) || runnb==278769)) runera = "yUL2016Flate";
  else if(!isMC && runnb >=278820 && runnb <=280385) runera = "yUL2016G";
  else if(!isMC && runnb >=280919 && runnb <=284044) runera = "yUL2016H";
  else {
    //Couldn't find data/MC era => no correction applied
    return uncormet_phi;
  }

  double METxcorr(0.),METycorr(0.);
  //UL2017
  if(runera=="yUL2017B") METxcorr = -(-0.211161*npv +0.419333);
  if(runera=="yUL2017B") METycorr = -(0.251789*npv +-1.28089);
  if(runera=="yUL2017C") METxcorr = -(-0.185184*npv +-0.164009);
  if(runera=="yUL2017C") METycorr = -(0.200941*npv +-0.56853);
  if(runera=="yUL2017D") METxcorr = -(-0.201606*npv +0.426502);
  if(runera=="yUL2017D") METycorr = -(0.188208*npv +-0.58313);
  if(runera=="yUL2017E") METxcorr = -(-0.162472*npv +0.176329);
  if(runera=="yUL2017E") METycorr = -(0.138076*npv +-0.250239);
  if(runera=="yUL2017F") METxcorr = -(-0.210639*npv +0.72934);
  if(runera=="yUL2017F") METycorr = -(0.198626*npv +1.028);
  if(runera=="yUL2017MC") METxcorr = -(-0.300155*npv +1.90608);
  if(runera=="yUL2017MC") METycorr = -(0.300213*npv +-2.02232);
  //UL2018
  if(runera=="yUL2018A") METxcorr = -(0.263733*npv +-1.91115);
  if(runera=="yUL2018A") METycorr = -(0.0431304*npv +-0.112043);
  if(runera=="yUL2018B") METxcorr = -(0.400466*npv +-3.05914);
  if(runera=="yUL2018B") METycorr = -(0.146125*npv +-0.533233);
  if(runera=="yUL2018C") METxcorr = -(0.430911*npv +-1.42865);
  if(runera=="yUL2018C") METycorr = -(0.0620083*npv +-1.46021);
  if(runera=="yUL2018D") METxcorr = -(0.457327*npv +-1.56856);
  if(runera=="yUL2018D") METycorr = -(0.0684071*npv +-0.928372);
  if(runera=="yUL2018MC") METxcorr = -(0.183518*npv +0.546754);
  if(runera=="yUL2018MC") METycorr = -(0.192263*npv +-0.42121);
  //UL2016
  if(runera=="yUL2016B") METxcorr = -(-0.0214894*npv +-0.188255);
  if(runera=="yUL2016B") METycorr = -(0.0876624*npv +0.812885);
  if(runera=="yUL2016C") METxcorr = -(-0.032209*npv +0.067288);
  if(runera=="yUL2016C") METycorr = -(0.113917*npv +0.743906);
  if(runera=="yUL2016D") METxcorr = -(-0.0293663*npv +0.21106);
  if(runera=="yUL2016D") METycorr = -(0.11331*npv +0.815787);
  if(runera=="yUL2016E") METxcorr = -(-0.0132046*npv +0.20073);
  if(runera=="yUL2016E") METycorr = -(0.134809*npv +0.679068);
  if(runera=="yUL2016F") METxcorr = -(-0.0543566*npv +0.816597);
  if(runera=="yUL2016F") METycorr = -(0.114225*npv +1.17266);
  if(runera=="yUL2016Flate") METxcorr = -(0.134616*npv +-0.89965);
  if(runera=="yUL2016Flate") METycorr = -(0.0397736*npv +1.0385);
  if(runera=="yUL2016G") METxcorr = -(0.121809*npv +-0.584893);
  if(runera=="yUL2016G") METycorr = -(0.0558974*npv +0.891234);
  if(runera=="yUL2016H") METxcorr = -(0.0868828*npv +-0.703489);
  if(runera=="yUL2016H") METycorr = -(0.0888774*npv +0.902632);
  if(runera=="yUL2016MCnonAPV") METxcorr = -(-0.153497*npv +-0.231751);
  if(runera=="yUL2016MCnonAPV") METycorr = -(0.00731978*npv +0.243323);
  if(runera=="yUL2016MCAPV") METxcorr = -(-0.188743*npv +0.136539);
  if(runera=="yUL2016MCAPV") METycorr = -(0.0127927*npv +0.117747);

  double CorrectedMET_x = uncormet *cos(uncormet_phi)+METxcorr;
  double CorrectedMET_y = uncormet *sin(uncormet_phi)+METycorr;
  double CorrectedMET = sqrt(CorrectedMET_x*CorrectedMET_x+CorrectedMET_y*CorrectedMET_y);
  double CorrectedMETPhi;
  if(CorrectedMET_x==0 && CorrectedMET_y>0) CorrectedMETPhi = TMath::Pi();
  else if(CorrectedMET_x==0 && CorrectedMET_y<0 )CorrectedMETPhi = -TMath::Pi();
  else if(CorrectedMET_x >0) CorrectedMETPhi = TMath::ATan(CorrectedMET_y/CorrectedMET_x);
  else if(CorrectedMET_x <0&& CorrectedMET_y>0) CorrectedMETPhi = TMath::ATan(CorrectedMET_y/CorrectedMET_x) + TMath::Pi();
  else if(CorrectedMET_x <0&& CorrectedMET_y<0) CorrectedMETPhi = TMath::ATan(CorrectedMET_y/CorrectedMET_x) - TMath::Pi();
  else CorrectedMETPhi =0;

  return CorrectedMETPhi;
}

