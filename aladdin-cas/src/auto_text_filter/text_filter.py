# -*- coding:utf-8 -*-

from auto_text_filter.operate_atf_db import milvus_search,content_2_vec,milvus_multi_search,vec_2_multi_clas,conditionexpectGet

async def text_filter_(content, cond_id_list):
    result = await milvus_search(content,partition_list=cond_id_list)
    if result['status'] !=0:return result
    classify_result=result['classify_result']
    if len(classify_result)>0:
        for ck,cv in classify_result.items():
            sim_file = list(cv['sim_file'].keys())
            classify_result[ck]['sim_file']=sim_file
    result['classify_result'] = classify_result
    return result

async def text_multi_filter_(content, cond_id_list):
    result = await milvus_multi_search(content,partition_list=cond_id_list)
    if result['status'] !=0:return result
    multi_clas=result['predict_result']
    for i in multi_clas.keys():
        sim_file = list(multi_clas[i]['sim_file'].keys())
        multi_clas[i]['sim_file']=sim_file
    
    result['multi_class']=multi_clas
    del result['predict_result']
    return result

async def multi_analysis(content, cond_id_list,cond_id):
    #多分类预测结果
    predict_result=await milvus_multi_search(content,partition_list=cond_id_list)
    if predict_result['status'] !=0:return predict_result
    #期望结果
    expect_result = await conditionexpectGet(cond_id)
    if expect_result['status'] !=0:return expect_result 
    del expect_result['status']
    predict_result['expect_result']=expect_result['expect_result']
    return predict_result


async def filter_analysis(content, cond_id_list,cond_id):
    predict_result=await milvus_search(content,partition_list=cond_id_list)
    if predict_result['status'] !=0:return predict_result 
    predict_result['predict_result']=predict_result['classify_result']
    del predict_result['classify_result']
    expect_result = await conditionexpectGet(cond_id)
    if expect_result['status'] !=0:return expect_result 
    predict_result['expect_result']=expect_result['expect_result']
    return predict_result
