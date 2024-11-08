//Code generated automatically by TMVA for Inference of Model file [DNN_SR_2b_rest_fold2.onnx] at [Tue Nov  5 15:22:06 2024] 

#ifndef TMVA_SOFIE_DNN_SR_2B_REST_FOLD2
#define TMVA_SOFIE_DNN_SR_2B_REST_FOLD2

#include<algorithm>
#include<vector>
#include "TMVA/SOFIE_common.hxx"
#include <fstream>

namespace TMVA_SOFIE_DNN_SR_2b_rest_fold2{
namespace BLAS{
	extern "C" void sgemv_(const char * trans, const int * m, const int * n, const float * alpha, const float * A,
	                       const int * lda, const float * X, const int * incx, const float * beta, const float * Y, const int * incy);
	extern "C" void sgemm_(const char * transa, const char * transb, const int * m, const int * n, const int * k,
	                       const float * alpha, const float * A, const int * lda, const float * B, const int * ldb,
	                       const float * beta, float * C, const int * ldc);
}//BLAS
struct Session {
std::vector<float> fTensor_linearrelustack6weight = std::vector<float>(64);
float * tensor_linearrelustack6weight = fTensor_linearrelustack6weight.data();
std::vector<float> fTensor_linearrelustack3bias = std::vector<float>(64);
float * tensor_linearrelustack3bias = fTensor_linearrelustack3bias.data();
std::vector<float> fTensor_linearrelustack3weight = std::vector<float>(8192);
float * tensor_linearrelustack3weight = fTensor_linearrelustack3weight.data();
std::vector<float> fTensor_linearrelustack0bias = std::vector<float>(128);
float * tensor_linearrelustack0bias = fTensor_linearrelustack0bias.data();
std::vector<float> fTensor_linearrelustack6bias = std::vector<float>(1);
float * tensor_linearrelustack6bias = fTensor_linearrelustack6bias.data();
std::vector<float> fTensor_linearrelustack0weight = std::vector<float>(1792);
float * tensor_linearrelustack0weight = fTensor_linearrelustack0weight.data();
std::vector<float> fTensor_11 = std::vector<float>(1);
float * tensor_11 = fTensor_11.data();
std::vector<float> fTensor_input7 = std::vector<float>(64);
float * tensor_input7 = fTensor_input7.data();
std::vector<float> fTensor_input3 = std::vector<float>(128);
float * tensor_input3 = fTensor_input3.data();
std::vector<float> fTensor_input11 = std::vector<float>(64);
float * tensor_input11 = fTensor_input11.data();
std::vector<float> fTensor_input = std::vector<float>(128);
float * tensor_input = fTensor_input.data();


Session(std::string filename ="") {
   if (filename.empty()) filename = "DNN_SR_2b_rest_fold2.dat";
   std::ifstream f;
   f.open(filename);
   if (!f.is_open()){
      throw std::runtime_error("tmva-sofie failed to open file for input weights");
   }
   std::string tensor_name;
   int length;
   f >> tensor_name >> length;
   if (tensor_name != "tensor_linearrelustack6weight" ) {
      std::string err_msg = "TMVA-SOFIE failed to read the correct tensor name; expected name is tensor_linearrelustack6weight , read " + tensor_name;
      throw std::runtime_error(err_msg);
    }
   if (length != 64) {
      std::string err_msg = "TMVA-SOFIE failed to read the correct tensor size; expected size is 64 , read " + std::to_string(length) ;
      throw std::runtime_error(err_msg);
    }
    for (int i =0; i < length; ++i) 
       f >> tensor_linearrelustack6weight[i];
   f >> tensor_name >> length;
   if (tensor_name != "tensor_linearrelustack3bias" ) {
      std::string err_msg = "TMVA-SOFIE failed to read the correct tensor name; expected name is tensor_linearrelustack3bias , read " + tensor_name;
      throw std::runtime_error(err_msg);
    }
   if (length != 64) {
      std::string err_msg = "TMVA-SOFIE failed to read the correct tensor size; expected size is 64 , read " + std::to_string(length) ;
      throw std::runtime_error(err_msg);
    }
    for (int i =0; i < length; ++i) 
       f >> tensor_linearrelustack3bias[i];
   f >> tensor_name >> length;
   if (tensor_name != "tensor_linearrelustack3weight" ) {
      std::string err_msg = "TMVA-SOFIE failed to read the correct tensor name; expected name is tensor_linearrelustack3weight , read " + tensor_name;
      throw std::runtime_error(err_msg);
    }
   if (length != 8192) {
      std::string err_msg = "TMVA-SOFIE failed to read the correct tensor size; expected size is 8192 , read " + std::to_string(length) ;
      throw std::runtime_error(err_msg);
    }
    for (int i =0; i < length; ++i) 
       f >> tensor_linearrelustack3weight[i];
   f >> tensor_name >> length;
   if (tensor_name != "tensor_linearrelustack0bias" ) {
      std::string err_msg = "TMVA-SOFIE failed to read the correct tensor name; expected name is tensor_linearrelustack0bias , read " + tensor_name;
      throw std::runtime_error(err_msg);
    }
   if (length != 128) {
      std::string err_msg = "TMVA-SOFIE failed to read the correct tensor size; expected size is 128 , read " + std::to_string(length) ;
      throw std::runtime_error(err_msg);
    }
    for (int i =0; i < length; ++i) 
       f >> tensor_linearrelustack0bias[i];
   f >> tensor_name >> length;
   if (tensor_name != "tensor_linearrelustack6bias" ) {
      std::string err_msg = "TMVA-SOFIE failed to read the correct tensor name; expected name is tensor_linearrelustack6bias , read " + tensor_name;
      throw std::runtime_error(err_msg);
    }
   if (length != 1) {
      std::string err_msg = "TMVA-SOFIE failed to read the correct tensor size; expected size is 1 , read " + std::to_string(length) ;
      throw std::runtime_error(err_msg);
    }
    for (int i =0; i < length; ++i) 
       f >> tensor_linearrelustack6bias[i];
   f >> tensor_name >> length;
   if (tensor_name != "tensor_linearrelustack0weight" ) {
      std::string err_msg = "TMVA-SOFIE failed to read the correct tensor name; expected name is tensor_linearrelustack0weight , read " + tensor_name;
      throw std::runtime_error(err_msg);
    }
   if (length != 1792) {
      std::string err_msg = "TMVA-SOFIE failed to read the correct tensor size; expected size is 1792 , read " + std::to_string(length) ;
      throw std::runtime_error(err_msg);
    }
    for (int i =0; i < length; ++i) 
       f >> tensor_linearrelustack0weight[i];
   f.close();
}

std::vector<float> infer(float* tensor_onnxGemm0){

//--------- Gemm
   char op_0_transA = 'n';
   char op_0_transB = 't';
   int op_0_m = 1;
   int op_0_n = 128;
   int op_0_k = 14;
   float op_0_alpha = 1;
   float op_0_beta = 1;
   int op_0_lda = 14;
   int op_0_ldb = 14;
   std::copy(tensor_linearrelustack0bias, tensor_linearrelustack0bias + 128, tensor_input);
   BLAS::sgemm_(&op_0_transB, &op_0_transA, &op_0_n, &op_0_m, &op_0_k, &op_0_alpha, tensor_linearrelustack0weight, &op_0_ldb, tensor_onnxGemm0, &op_0_lda, &op_0_beta, tensor_input, &op_0_n);

//------ RELU
   for (int id = 0; id < 128 ; id++){
      tensor_input3[id] = ((tensor_input[id] > 0 )? tensor_input[id] : 0);
   }

//--------- Gemm
   char op_2_transA = 'n';
   char op_2_transB = 't';
   int op_2_m = 1;
   int op_2_n = 64;
   int op_2_k = 128;
   float op_2_alpha = 1;
   float op_2_beta = 1;
   int op_2_lda = 128;
   int op_2_ldb = 128;
   std::copy(tensor_linearrelustack3bias, tensor_linearrelustack3bias + 64, tensor_input7);
   BLAS::sgemm_(&op_2_transB, &op_2_transA, &op_2_n, &op_2_m, &op_2_k, &op_2_alpha, tensor_linearrelustack3weight, &op_2_ldb, tensor_input3, &op_2_lda, &op_2_beta, tensor_input7, &op_2_n);

//------ RELU
   for (int id = 0; id < 64 ; id++){
      tensor_input11[id] = ((tensor_input7[id] > 0 )? tensor_input7[id] : 0);
   }

//--------- Gemm
   char op_4_transA = 'n';
   char op_4_transB = 't';
   int op_4_m = 1;
   int op_4_n = 1;
   int op_4_k = 64;
   float op_4_alpha = 1;
   float op_4_beta = 1;
   int op_4_lda = 64;
   int op_4_ldb = 64;
   std::copy(tensor_linearrelustack6bias, tensor_linearrelustack6bias + 1, tensor_11);
   BLAS::sgemm_(&op_4_transB, &op_4_transA, &op_4_n, &op_4_m, &op_4_k, &op_4_alpha, tensor_linearrelustack6weight, &op_4_ldb, tensor_input11, &op_4_lda, &op_4_beta, tensor_11, &op_4_n);
	std::vector<float> ret (tensor_11, tensor_11 + 1);
	return ret;
}
};
} //TMVA_SOFIE_DNN_SR_2b_rest_fold2

#endif  // TMVA_SOFIE_DNN_SR_2B_REST_FOLD2
