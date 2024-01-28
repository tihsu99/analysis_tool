#include "ROOT/RDataFrame.hxx"
#include "ROOT/RVec.hxx"
#include "TCanvas.h"
#include "TH1D.h"
#include "TLatex.h"
#include "Math/Vector4D.h"
#include "Math/Vector4Dfwd.h"
#include "TStyle.h"
#include "TString.h"


using namespace ROOT;
using namespace std;
using namespace ROOT::VecOps;

TString era = "EraToBeReplaced";

// Trigger Scale Factor
TFile*f_trigger=TFile::Open("../../data/Trigger_scale_factor_"+era+".root");
TH2D*trigger_sf_electron_HLT_resolved = (TH2D*)f_trigger->Get("bh_Electron_scale_factor");
TH2D*trigger_sf_electron_HLT_boost    = (TH2D*)f_trigger->Get("boost_Electron_scale_factor");
TH2D*trigger_sf_muon_HLT_resolved     = (TH2D*)f_trigger->Get("bh_Muon_scale_factor");
TH2D*trigger_sf_muon_HLT_boost        = (TH2D*)f_trigger->Get("boost_Muon_scale_factor");
const float trigger_highest_pt = trigger_sf_electron_HLT_resolved->GetXaxis()->GetBinUpEdge(trigger_sf_electron_HLT_resolved->GetNbinsX());


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

std::vector<int> match_idx(int nInput, ROOT::VecOps::RVec<float> Input_pt, ROOT::VecOps::RVec<float> Input_eta, ROOT::VecOps::RVec<float> Input_phi, int nRef, ROOT::VecOps::RVec<float> Ref_pt, ROOT::VecOps::RVec<float> Ref_eta, ROOT::VecOps::RVec<float> Ref_phi, float dr_cut, float pt_ratio_cut){

  // Function used for doing kinematic match of "Ref" particle to "Input" particle" 

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
      dr_temp = sqrt((eta1-eta2)*(eta1-eta2) + (phi1-phi2)*(phi1-phi2));
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

std::vector<int> match_idx(int nInput, ROOT::VecOps::RVec<float> Input_pt, ROOT::VecOps::RVec<float> Input_eta, ROOT::VecOps::RVec<float> Input_phi, int nRef, ROOT::VecOps::RVec<float> Ref_pt, ROOT::VecOps::RVec<float> Ref_eta, ROOT::VecOps::RVec<float> Ref_phi, float dr_cut, float pt_ratio_cut, ROOT::VecOps::RVec<int> GenPart_statusFlags){

  // Function used for doing kinematic match of "Ref" particle to "Input" particle" 

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
      if(!((GenPart_statusFlags[i_ref]>>13)&1)) continue;
      pt2 = Ref_pt[i_ref];
      eta2 = Ref_eta[i_ref];
      phi2 = Ref_phi[i_ref];
      dr_temp = sqrt((eta1-eta2)*(eta1-eta2) + (phi1-phi2)*(phi1-phi2));
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

std::vector<int> match_idx(ROOT::VecOps::RVec<int> Input_id, ROOT::VecOps::RVec<float> Input_pt, ROOT::VecOps::RVec<float> Input_eta, ROOT::VecOps::RVec<float> Input_phi, int nRef, ROOT::VecOps::RVec<float> Ref_pt, ROOT::VecOps::RVec<float> Ref_eta, ROOT::VecOps::RVec<float> Ref_phi, float dr_cut, float pt_ratio_cut){

  // Function used for doing kinematic match of "Ref" particle to "Input" particle", dedicated for map_id_input (i.e. tightJets_id etc.)

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
      dr_temp = sqrt((eta1-eta2)*(eta1-eta2) + (phi1-phi2)*(phi1-phi2));
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


std::vector<int> match_idx_parton(int nGenPart, ROOT::VecOps::RVec<int> GenPart_genPartIdxMother, ROOT::VecOps::RVec<int> GenPart_pdgId, ROOT::VecOps::RVec<int> GenPart_statusFlags){

  // Find mother particle id for genPart

  std::vector<int> match_idx;
  int daughter_id, daughter_statusflags, mother_idx, mother_id, mother_statusflags;
  bool isdaughter_HardProcess;

  for(int index_ = 0; index_ < nGenPart; index_++){
    daughter_id = GenPart_pdgId[index_];
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

int match_reco_parton(int Reco_index, std::vector<int> Gen_Reco_match, std::vector<int> Part_Gen_match, std::vector<int> Part_mother_match){
  
  // Function used for mapping reco object to mother parton

  int gen_index = Gen_Reco_match[Reco_index];
  if(gen_index < 0) return -1;
  int part_index = Part_Gen_match[gen_index];
  if(part_index < 0) return -1;
  int part_mother_index = Part_mother_match[part_index];
  if(part_mother_index < 0) return -1;
  return part_mother_index;
}

int match_parton_to_reco(int parton_pdgid,  int reco_pt_order, std::vector<int> Gen_Reco_match, std::vector<int> Part_Gen_match, std::vector<int> Part_mother_match, ROOT::VecOps::RVec<int> GenPart_pdgId){

  int parton_index, iparton;
  std::vector<int> reco_candidate;
  for(int iReco=0; iReco < Gen_Reco_match.size(); iReco++){
    iparton = match_reco_parton(iReco, Gen_Reco_match, Part_Gen_match, Part_mother_match);
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
    std::vector<int> cv = particle_cv(iPart, Part_mother_match, GenPart_pdgId);
    bool Flag = true;
    bool isdaughter_prompt      = (GenPart_statusFlags[iPart]>>0)&1;
    bool isdaughter_HardProcess = (GenPart_statusFlags[iPart]>>7)&1;
    bool isdaughter_lastcopy    = (GenPart_statusFlags[iPart]>>13)&1;
  //  if(!(isdaughter_prompt && isdaughter_lastcopy)) continue;
    if(!(isdaughter_HardProcess)) continue;
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
  if(D<0) return A;
  else{ 
    if(abs(A + sqrt(D)/(l_pt*l_pt)) > abs(A - sqrt(D)/(l_pt*l_pt))){
      return A - sqrt(D)/(l_pt*l_pt);
    }
    else return A + sqrt(D)/(l_pt*l_pt);
  }
}

float top_reconstruction(float W_E, float W_px, float W_py, float W_pz, ROOT::VecOps::RVec<float> b_jet_id, ROOT::VecOps::RVec<float> Jet_pt, ROOT::VecOps::RVec<float> Jet_eta, ROOT::VecOps::RVec<float> Jet_phi, ROOT::VecOps::RVec<float> Jet_mass){

  float top_E = -1.;
  float top_px = -1.;
  float top_py = -1.;
  float top_pz = -1.;
  float top_mass = -1.;
  float mT = 172.69; //PDG 2023
  float jet_pt, jet_eta, jet_phi, jet_mass, jet_e, jet_px, jet_py, jet_pz;
  float top_e_tmp, top_px_tmp, top_py_tmp, top_pz_tmp, top_mass_tmp;

  for(int ijet = 0; ijet < b_jet_id.size(); ijet++){
    int jet_idx = b_jet_id[ijet];
    if(jet_idx < 0) continue;
    jet_pt = Jet_pt[jet_idx]; jet_eta = Jet_eta[jet_idx]; jet_phi = Jet_phi[jet_idx]; jet_mass = Jet_mass[jet_idx];
    jet_px = jet_pt * cos(jet_phi);
    jet_py = jet_pt * sin(jet_phi);
    jet_pz = jet_pt * sinh(jet_eta);
    jet_e  = sqrt(jet_pt*jet_pt * (1. + cosh(jet_eta)*cosh(jet_eta)) + jet_mass*jet_mass); 

    top_e_tmp  = W_E + jet_e;
    top_px_tmp = W_px + jet_px;
    top_py_tmp = W_py + jet_py;
    top_pz_tmp = W_pz + jet_pz;
    top_mass_tmp = sqrt(top_e_tmp*top_e_tmp - top_pz_tmp*top_pz_tmp - top_py_tmp*top_py_tmp - top_px_tmp*top_px_tmp);

    if(abs(top_mass_tmp - mT) < abs(top_mass - mT)){
      top_mass = top_mass_tmp;
      top_px   = top_px_tmp;
      top_py   = top_py_tmp;
      top_pz   = top_pz_tmp;
    }
  }

  return top_mass;
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

///////////////
//  BTag SF  //
///////////////

ROOT::VecOps::RVec<Int_t> reselect_btag_jet(ROOT::VecOps::RVec<float> Jet_eta, ROOT::VecOps::RVec<Int_t> jetid){
  ROOT::VecOps::RVec<Int_t> return_id;
  for(int i = 0; i < jetid.size(); i++){
    if (jetid[i] < 0) continue;
    if (abs(Jet_eta[jetid[i]]) > 2.4) continue;
    return_id.push_back(jetid[i]);
  }
  return return_id;
}


float btag_SF(ROOT::VecOps::RVec<Int_t> jetid, ROOT::VecOps::RVec<float> btag_sf){
  float sf = 1.0;
  for(int i=0; i < jetid.size(); i++){
    if(jetid[i]<0) continue;
    sf*=btag_sf[jetid[i]];
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
