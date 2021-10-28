# -*- coding:utf-8 -*-
import asyncio
import aiomysql
import pymysql
from collections import defaultdict
from read_config import mysql_config,milvus_config
import uuid
# from utils import singleton
import jieba
import jieba.analyse
# from milvus import Milvus,DataType
import numpy as np 
import hashlib
from collections import Counter
from read_config import stopwords_path
from multiprocessing import Queue,Pool,cpu_count
# from auto_text_filter.text_spectral_cluster import stopwords

from client.milvus_client import AioMilvus
collection_name ='atf'
milvus_client = AioMilvus(collection_name,asyncio.get_event_loop())

#创建mysql连接池
res=[]
async def get_mysql_pool():
    async def _foo(res):
        dbpool = await aiomysql.create_pool(
            **mysql_config,
            maxsize=10,
            loop=asyncio.get_event_loop()
        )
        res.append(dbpool)
        return dbpool
    global res
    if len(res)==0: return await _foo(res)
    else: return res[0]

def insert_words_2_mysql(cluster_result):
    taskid= cluster_result['taskid']
    # print(f"loop in insert_keywords_2_mysql: {id(asyncio.get_event_loop())}")
    cluster_name_result = cluster_result['cluste_name']
    class_ave_simi = cluster_result['cluste_ave_simi']
    file_words = cluster_result['file_words']
    cate=[]
    doc_name=[]
    class_avisimi_list=[]
    words=[]
    for ca in cluster_name_result.keys():
        for name in cluster_name_result[ca]:
            cate.append(ca)
            doc_name.append(name)
            words.append(file_words[name])
            class_avisimi_list.append(float(class_ave_simi[ca]))
    cate_doc_words = tuple([(taskid,cate[i],class_avisimi_list[i],doc_name[i],words[i],'true') for i in range(0,len(cate))])
    class_doc_words_sql="INSERT IGNORE INTO t_cls_file(`f_task_id`,`f_class`,`f_cls_simi`,`f_file_name`,`f_word`,`f_flag`) VALUES (%s,%s,%s,%s,%s,%s)"  

    conn = pymysql.connect(host=mysql_config['host'], port=mysql_config['port'], user=mysql_config['user'], passwd=mysql_config['password'], db=mysql_config['db'])
    curs = conn.cursor()
    # async with dbpool.acquire() as conn, conn.cursor() as curs:
    curs.executemany(class_doc_words_sql, cate_doc_words)
    # curs.executemany(class_word_sql, word_file)
    conn.commit()
    conn.close()
    curs.close()
    return {"status":0}

#根据任务id查询聚类的结果
async def clusterResultGet(taskid):
    get_cluster_result = "SELECT f_class,f_cls_simi,f_file_name FROM t_cls_file WHERE f_task_id=%s and f_flag='true';"
    # all_taskid_sql = "SELECT f_task_id FROM t_cls_file;"
    dbpool = await get_mysql_pool()       
    async with dbpool.acquire() as conn, conn.cursor() as curs:
        await curs.execute(get_cluster_result,(taskid,))
        clas_pro_docs =await curs.fetchall()
        await conn.commit()
        if len(clas_pro_docs)==0 or clas_pro_docs==None:return {"status":1,"message":"NO cluster data"}
        clas_docs=defaultdict(list)
        clas_pro = defaultdict()
        for i in clas_pro_docs:
            clas_docs[i[0]].append(i[2])
            clas_pro[i[0]]=i[1]
        result= {}
        for k,v in clas_docs.items():
            newd={}
            newd['docs']=v
            newd['similar']=clas_pro[k]
            result[k]=newd
        cluster_result={}
        cluster_result['cluster_result']=result
        cluster_result['status']=0
        return cluster_result
   
#修改聚类完成后文本是否参与条件关键词的生成，0为删除，非0为撤销删除
async def docsWordsPut(taskid,doc_name,action):
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:     
        update_doc_flag_sql = "UPDATE t_cls_file SET f_flag=%s WHERE f_task_id= %s and f_file_name=%s;"     
        if action==0:
            line_num = await curs.execute(update_doc_flag_sql, ('false',taskid,doc_name))
            await conn.commit()
            if line_num==0: return {"status":1,"message":"Error operater or error message or error file_name"}
        else:
            line_num=await curs.execute(update_doc_flag_sql, ('true',taskid,doc_name))
            await conn.commit()
            if line_num==0: return {"status":1,"message":"Error operater or error message"}
        return {"status":0,"message":"操作成功"}

#根据任务id删除任务t_cls_file中的数据
async def docsWordsDelete(taskid):
    dl_sql="DELETE t_cls_file FROM t_cls_file WHERE f_task_id=%s;"
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:     
        line_num = await curs.execute(dl_sql, (taskid,))
        await conn.commit()
        if line_num==0: return {"status":1,"message":"The taskid had no doc or error taskid"}   
        return {"status":0,"taskid":taskid,"message":"删除数据成功"}

#查询条件分组及分组下的条件
async def condiGroupGet(group_id=None): 
    select_condi = 'SELECT g.`f_group_id`,g.`f_group`,c.`f_cond`,c.`f_cond_id` FROM t_group g LEFT JOIN t_cond c ON c.`f_group_id`=g.`f_group_id` ;'
    select_condi_one = 'SELECT g.`f_group_id`,g.`f_group`,c.`f_cond`,c.`f_cond_id` FROM t_group g LEFT JOIN  t_cond c ON c.`f_group_id`=g.`f_group_id` where g.`f_group_id`=%s ;'
    dbpool = await get_mysql_pool()
    async with dbpool.acquire() as conn, conn.cursor() as curs:
        if group_id ==None:
            line_num = await curs.execute(select_condi)
            await conn.commit()
            if line_num ==0: return {"status":1,"message":"No group"}
            result =await curs.fetchall()
            groups={}          
            for tr in result:
                if tr[0] in groups.keys():
                    groups[tr[0]]['condis'][tr[2]]=tr[3]
                else:
                    gid={}
                    gid['group_name']=tr[1]
                    gid['condis']={tr[2]:tr[3]}
                    groups[tr[0]]=gid                    
            return {"status":0,"groups":groups}            
        if group_id !=None:
            line_num = await curs.execute(select_condi_one,(group_id,))
            await conn.commit()
            if line_num ==0: return {"status":1,"message":"No group"}
            result =await curs.fetchall()
            groups={}  
            for tr in result:
                if tr[0] in groups.keys():
                    groups[tr[0]]['condis'][tr[2]]=tr[3]
                else:
                    gid={}
                    gid['group_name']=tr[1]
                    gid['condis']={tr[2]:tr[3]}
                    groups[tr[0]]=gid             
            return {"status":0,"groups":groups}

#只查看所有条件分组名称和id
async def groupGet(group_id=None): 
    select_cla_count = 'SELECT f_group_id,f_group FROM t_group;'
    select_group_only = 'SELECT f_group FROM t_group where f_group_id = %s;'
    dbpool = await get_mysql_pool()
    async with dbpool.acquire() as conn, conn.cursor() as curs:
        if group_id ==None:
            line_num = await curs.execute(select_cla_count)
            await conn.commit()
            if line_num==0: return {'message':'No group',"status": 1}
            result =await curs.fetchall()
            condi_group={}
            if len(result)>0:            
                for i in result:
                    condi_group[i[0]] = i[1]
            return {"status":0,"groups":condi_group}
        else:
            line_num = await curs.execute(select_group_only,(group_id,))
            await conn.commit()
            if line_num==0: return {'message':'No group',"status": 1}
            result =await curs.fetchall()
            condi_group={}
            condi_group[group_id] = result[0][0]
            return {"status":0,"groups":condi_group}

#增加条件分组
async def condiGroupPost(group_name):
    conditon_group_insert_sql = "INSERT IGNORE INTO t_group(`f_group_id`,`f_group`) VALUES (%s,%s)"
    group_id = str(uuid.uuid1())
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:
        line_num = await curs.execute(conditon_group_insert_sql, (group_id,group_name))
        await conn.commit()
        if line_num==0:return {'message':'Group_name repeated',"status": 1}
        return {'status':0,'group_id':group_id,'message':'新增条件分组成功'}
 
#删除条件分组
async def condiGroupDelete(group_id):
    # del_group_sql = "DELETE g,c,w FROM t_group g LEFT JOIN t_cond c ON g.`f_group_id`=c.`f_group_id` LEFT JOIN t_word_file w ON c.`f_file_name` = w.`f_file_name` WHERE g.`f_group_id`=%s;"
    del_group_sql = "DELETE g,c FROM t_group g LEFT JOIN t_cond c ON g.`f_group_id`=c.`f_group_id`  WHERE g.`f_group_id`=%s;"
    select_condid_sql = "SELECT f_milvusid FROM t_cond WHERE f_group_id =%s;"
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:
        line_num = await curs.execute(select_condid_sql, (group_id,))
        await conn.commit()
        if line_num!=0:
            cond_ids = await curs.fetchall()
            del_milid=[co[0] for co in cond_ids]           
            result = milvus_client.delete_entity_by_id(milvus_id_list=del_milid)
            if result['status'] !=0: return {"status":2,"message":result['message']}
            
        line_num = await curs.execute(del_group_sql, (group_id,))
        await conn.commit()
        if line_num==0:return {'message':'Error group_id or no data',"status": 1}               
        return {'status':0,'group_id':group_id,'message':'删除条件分组成功'}
     
#修改条件分组名
async def condiGroupPut(group_id,new_grp_name):
    put_grp_sql = "UPDATE t_group SET f_group=%s WHERE f_group_id= %s;"
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:
        line_num = await curs.execute(put_grp_sql, (new_grp_name,group_id))
        await conn.commit()
        if line_num==0:return {'message':'Group_ID NOT exist or Group name exist',"status": 1}
        return {'status':0,'group_id':group_id,'message':'修改条件分组名称成功'}

#添加条件时，判断任务id，类名，分组id是否存在或正确，条件名是否已经存在
async def judge_condition_post(taskid,class_name,group_id,condi_name):
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:
    #判断group-id是否存在
        select_group = 'SELECT f_group FROM t_group where `f_group_id` = %s;'
        ln = await curs.execute(select_group,(group_id,))
        await conn.commit()
        if ln==0:return {'message':'Group_ID NOT exist',"status": 1}       
        #判断新增的条件名是否存在
        condi_sql="SELECT f_cond_id FROM t_cond where `f_cond`=%s;"
        ln2 = await curs.execute(condi_sql,(condi_name,))
        await conn.commit()
        # condis = await curs.fetchall()
        # if (condi_name,) in condis: return {"status":1, "message":"Conditon name already exist"}
        if ln2 != 0:return {"status":1, "message":"Conditon name already exist"}
        select_cla_count = "SELECT f_file_name,f_word FROM t_cls_file WHERE f_task_id = %s and f_class=%s and f_flag='true';"
        ln3 = await curs.execute(select_cla_count, (taskid,class_name))
        #判断此类别下是否有数据
        if ln3==0: return {"status":1,"message":"No class data"}  
        result_name_word = await curs.fetchall()
        await conn.commit()
        return {"status":0,"result":result_name_word} 

#把所有的关键词生成向量
def get_keywords_vec(result_name_word):   
    fnames=[]
    fnameword={}
    vecs=[]
    for i in result_name_word:
        fnames.append(i[0])
        fnameword[i[0]]=i[1]
        vecs.append(get_text_vec(i[1])) 
    return vecs,fnames,fnameword
#添加条件，把聚类的结果，类名重命名为条件名、文件名存到条件表中
async def conditionPost(taskid,class_name,group_id,condi_name):
    #判断参数是否存在或正确
    result = await judge_condition_post(taskid,class_name,group_id,condi_name)
    if result['status'] ==1:return result
    result_name_word = result['result']
    new_class_insert_sql = "INSERT IGNORE INTO t_cond(`f_cond_id`,`f_group_id`,`f_cond`,`f_file_name`,`f_word`,`f_milvusid`) VALUES (%s,%s,%s,%s,%s,%s);"  
    #用于条件插入时，搜索出相似文本大于0.7时，mysql中搜出相关信息
    have_sim_te_f={}
    cond_sql = "SELECT f_cond_id,f_cond,f_file_name FROM t_cond WHERE f_milvusid=%s;"
    vecs=[]
    fnames=[]
    fnameword={}
    # for i in result_name_word:
    #     keywords = i[1]     
    #     vectors = get_text_vec(keywords)
    #     fnames.append(i[0])
    #     vecs.append(vectors)
    #     fnameword[i[0]]=i[1]
    vecs ,fnames,fnameword = get_keywords_vec(result_name_word)
    vecss=np.array(vecs)
    result = await milvus_client.search(top_k=1,partition_list=None,vec=vecss)
    if result['status']==1:return result
    all_milvus_search = result['message'] 
    similar_milvus_id_list, dis_list = all_milvus_search._id_array, all_milvus_search._dis_array

    #新增条件
    con_id=str(uuid.uuid1())
    # result_con = milvus_client.creat_partition(partition_tag = con_id)
    # if result_con['status'] !=0: return {"status":1,"message":result_con['message']} 

    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:      
        if len(dis_list)> 0 and len(dis_list[0])>0:
            for one in range(len(dis_list)):
                if dis_list[one][0]>0.7:
                    #若搜索出的文本相似度，大于0.7则判断两个文本有一定的相似度，为一类的可能性比较大
                    line_num = await curs.execute(cond_sql,(similar_milvus_id_list[one][0],))
                    await conn.commit()
                    if line_num ==0:
                        return {'message':'Mysql and milvus data are Inconsistency',"status": 1}
                    cnf = await curs.fetchall()
                    c_id=cnf[0][0]
                    c_name=cnf[0][1]
                    f_na=cnf[0][2]
                    have_sim_te_f[fnames[one]]=[c_id,c_name,f_na]
                    continue
                milvus_result = milvus_client.insert(vecss[one].reshape(1,-1),partition_tag=None)
                if milvus_result['status']==1:return milvus_result
                milvus_id = milvus_result['message'][0]
                line_num = await curs.execute(new_class_insert_sql,(con_id,group_id,condi_name,fnames[one],fnameword[fnames[one]],milvus_id))
                await conn.commit()
        else:
            for one in range(len(vecss)):
                milvus_result = milvus_client.insert(vecss[one].reshape(1,-1),partition_tag=None)
                if milvus_result['status']==1:return milvus_result
                milvus_id = milvus_result['message'][0]
                line_num = await curs.execute(new_class_insert_sql,(con_id,group_id,condi_name,fnames[one],fnameword[fnames[one]],milvus_id))
                await conn.commit()
    #若所有的条件下的文本都存在相似高的条件文本，则说明没有一个添加成功，都需要用户进行判断是否合并
    #把创建的partition删除
    if len(have_sim_te_f)==len(result_name_word):
        return_result={'status':0,'message':'All file have similar text','sim_file_mes':have_sim_te_f}
        # res = milvus_client.drop_partition(con_id)
        # if res['status']==1:return res
        return return_result
        # return {'status':1,'message':'Not one condition text added successfully'}
    return_result={'status':0,'message':'Added successfully','cond_id':con_id}
    #若有的文本存在相似度高的文本则把信息返回
    if len(have_sim_te_f)>0:
        return_result['sim_file_mes']=have_sim_te_f
    return return_result
    
#指定已存在的条件id，添加分析后的数据,若添加至mysql中指定的条件下有重复的文件名，则不会添加重复的名字。若条件里没有cond_id或cond_name,返回错误
async def conditionAssignPost(taskid,file_list,cond_id):
    #,cond_name,group_id
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs: 
        #判断条件是否存在
        condi_sql="SELECT f_cond,f_group_id FROM t_cond where `f_cond_id`=%s ;"
        ln2 = await curs.execute(condi_sql,(cond_id,))
        await conn.commit()
        if ln2==0:return {'status':1,'message':'Error cond_id '} 
        cond_group = await curs.fetchall()
        cond_name,group_id = cond_group[0][0],cond_group[0][1]
    
        #把指定任务下的文件列表存入指定的条件id和条件名下，相同的条件下不会存入相同的文件名
        not_insert_file=[]
        new_class_insert_sql = "INSERT IGNORE INTO t_cond(`f_cond_id`,`f_group_id`,`f_cond`,`f_file_name`,`f_word`,`f_milvusid`) VALUES (%s,%s,%s,%s,%s,%s);"
        select_word = "SELECT f_word FROM t_cls_file WHERE f_task_id = %s and f_file_name=%s and f_flag='true';"
        for i in file_list:
            ln3 = await curs.execute(select_word, (taskid,i))
            await conn.commit()
            #若没有找到这个任务下文本的数据，不会报错，会返回未添加文本的列表中，最后一起返回
            if ln3==0:
                not_insert_file.append(i)
                continue
            #若有则查询的关键词数据，生成向量存入milvus中，
            result_word = await curs.fetchall()
            vectors = get_text_vec(result_word[0][0])
            vec= vectors.reshape(1,-1)
            #把vec向量数据存入milvus中，
            milvus_result = milvus_client.insert(vec,partition_tag=None)
            if milvus_result['status']==1:return milvus_result
            milvus_id = milvus_result['message'][0]
            #把向量存入milvus中的id和其他数据（条件id，group_id,条件名,文件名，文件关键词）存入mysql中
            line_num = await curs.execute(new_class_insert_sql,(cond_id,group_id,cond_name,i,result_word[0][0],milvus_id))
            await conn.commit()
            #因在mysql中相同的条件和文件不会重复添加，会存在添加失败情况，若添加mysql失败则需要在milvus中删除已经存入的milvusid
            if line_num==0:
                milvus_client.delete_entity_by_id([milvus_id])
                not_insert_file.append(i)
        #若添加失败的文件的数量和要添加的数一样，则说明所有的文件名都和指定的条件下有相同的文件
        if len(not_insert_file)==len(file_list):return {'status':0,'message':"All condition text was not added successfully","insert_fail":not_insert_file} 
        return_result={'status':0,'message':"Added successfully"}
        #若有添加失败的文件，则返回添加失败的文件
        if len(not_insert_file)>0:
            return_result['insert_fail']=not_insert_file

        return return_result
                
#查看条件，条件按照分组进行返回
async def conditionGet(cond_id=None):
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:
        select_id="SELECT f_cond_id,f_group_id,f_cond,f_file_name FROM t_cond WHERE f_cond_id=%s;"
        select_all="SELECT f_cond_id,f_group_id,f_cond,f_file_name FROM t_cond;"
        result=[]
        condition={}
        if cond_id==None:
            await curs.execute(select_all)
        else:
            await curs.execute(select_id,(cond_id))
        await conn.commit()
        result =await curs.fetchall()
        
        if len(result)==0 or result==None:
            return {"status":0,"conditions":condition}
        #整理查询出的条件，返回固定格式数据
        for con in result:
            if con[0] in condition.keys():
                condition[con[0]]['docs'].append(con[3])
                condition[con[0]]['group_id']=con[1]
            else:
                condi_message={}
                condi_message['cond_name']=con[2]
                docs=[]
                docs.append(con[3])
                condi_message['docs']=docs
                condition[con[0]]=condi_message
        return {"status":0,"conditions":condition}
    
#删除条件
async def conditionDelete(cond_id):
    # del_group_sql = "DELETE g,c,w FROM t_group g LEFT JOIN t_cond c ON g.`f_group_id`=c.`f_group_id` LEFT JOIN t_word_file w ON c.`f_file_name` = w.`f_file_name` WHERE g.`f_group_id`=%s;"
    del_con_sql = "DELETE FROM t_cond WHERE t_cond.`f_cond_id`= %s;" 
    select_condid_sql = "SELECT f_milvusid FROM t_cond WHERE f_cond_id =%s;"
            
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:
        line_num = await curs.execute(select_condid_sql, (cond_id,))
        await conn.commit()
        if line_num==0:
            return {"status":1,"message":"Error cond_id or The cond_id have no data"}

        cond_ids = await curs.fetchall()
        del_milid=[co[0] for co in cond_ids]
        result = milvus_client.delete_entity_by_id(milvus_id_list=del_milid)
        if result['status'] !=0: return {"status":1,"message":result['message']}

        await curs.execute(del_con_sql, (cond_id,))
        await conn.commit()
        # if line_num2==0:
        #     return {'message':'Mysql and milvus data are Inconsistency',"status": 2}               
        return {'status':0,'cond_id':cond_id,'message':'删除条件成功'}
  

#删除条件下的一个文本，不能修改撤回
async def condidocsDelete(cond_id,doc_name):
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:
        #查询MySQL中这个文本的milvusid
        select_milvus_id='SELECT f_milvusid FROM t_cond WHERE f_cond_id=%s AND f_file_name=%s;'
        ln = await curs.execute(select_milvus_id,(cond_id,doc_name))
        await conn.commit()
        if ln==0:return {'message':'Error cond_id or error doc_name or no data',"status": 1}
        result_mysql =await curs.fetchall()
        milvus_id = result_mysql[0][0]
        #根据milvusid，删除milvus中的文本向量
        result = milvus_client.delete_entity_by_id(milvus_id_list=[milvus_id])
        if result['status'] !=0: return {"status":1,"message":result['message']}
        #再删除MySQL中的此文本数据
        d_cond_sql="DELETE t_cond FROM t_cond WHERE f_cond_id=%s AND f_file_name=%s;"           
        line_num = await curs.execute(d_cond_sql,(cond_id,doc_name))     
        await conn.commit() 
        # d_cond_sql="DELETE t_cond FROM t_cond WHERE f_cond_id=%s AND f_file_name=%s;" %(cond_id,doc_name)          
        # line_num = await curs.execute(d_cond_sql)     
        # await conn.commit()
        if line_num ==0: 
            return {'message':'Mysql and milvus data are Inconsistency',"status": 2}       
        return {'status':0,'message':'删除成功'}
   

#修改条件名
async def conditionPut(cond_id,new_condi_name):
    put_cond_sql = "UPDATE t_cond SET f_cond=%s WHERE f_cond_id=%s"  
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:
        #判断修改的条件名是否存在
        condi_sql="SELECT f_cond_id FROM t_cond where `f_cond`=%s;"
        ln2 = await curs.execute(condi_sql,(new_condi_name,))
        await conn.commit()
        if ln2 != 0:return {"status":1, "message":"Conditon name already exist"}

        line_num = await curs.execute(put_cond_sql, (new_condi_name,cond_id))
        await conn.commit()
        if line_num==0:return {'message':'Error cond_id or condi name aleady exist',"status": 1}
        return {'status':0,'message':'操作成功'}



def content_2_vec(content):
    extract_words = extract_tag(content)
    if extract_words['status']==1:return extract_words
    keywords = extract_words['words']
    # print(keywords)
    vectors = get_text_vec(keywords)
    vec= vectors.reshape(1,-1)
    result={}
    result['status']=0
    result['vec']=vec
    result['keywords']=keywords
    return result

#查看条件，根据期望条件查看信息
async def conditionexpectGet(expect_cond_id):

    select_id="SELECT f_cond,f_file_name,f_word FROM t_cond WHERE f_cond_id=%s;"
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:    
        num = await curs.execute(select_id,(expect_cond_id,))
        await conn.commit()
        if num ==0: return {"status":1,"message":"Error expect_cond_id or no data"}
        result =await curs.fetchall()
        expect_result={}
        expect_result['cond_name']=result[0][0]
        expect_result['cond_id'] = expect_cond_id
        sim_file={}
        for con in result:
            sim_file[con[1]]=con[2].split(' ')
        expect_result['sim_file']=sim_file
        return {"status":0,"expect_result":expect_result}
#单分类
async def milvus_search(content,partition_list=None):
    result = content_2_vec(content)
    if result['status']!=0:return result
    vec,keywords = result['vec'],result['keywords']
    result=await vec_2_multi_clas(vec)
    if result['status']!=0:return result
    sim=0
    res_condname=None
    res_id = None
    mc = result['multi_class']
    if partition_list==None or len(partition_list)==0:      
        for mk,mv in mc.items():
            if mv['sim']>sim:
                sim = mv['sim']
                res_condname=mk
                res_id=mv
    else:
        for mk,mv in mc.items():
            if mv['sim']>sim and mv['cond_id'] in partition_list:
                sim = mv['sim']
                res_condname=mk
                res_id=mv
    classify_result={}
    if res_condname !=None:
        classify_result[res_condname]=res_id

    return_result={}
    return_result['classify_result']=classify_result
    return_result['words']=keywords.split(' ')
    return_result['status']=0
    return return_result

#多分类
async def milvus_multi_search(content,partition_list=None):
    result = content_2_vec(content)
    if result['status']!=0:return result
    vec,keywords = result['vec'],result['keywords']
    result=await vec_2_multi_clas(vec)
    if result['status']!=0:return result   
    if partition_list==None or len(partition_list)==0:
        result['words']=keywords.split(' ')
        pre=result['multi_class']
        del result['multi_class']
        result['predict_result']=pre
        return result
    else:
        return_res={}
        mc = result['multi_class']
        for mk,mv in mc.items():
            if mv['cond_id'] in partition_list:
                return_res[mk]=mv
        result={}
        result['predict_result']=return_res
        result['words']=keywords.split(' ')
        result['status']=0
        return result

async def vec_2_multi_clas(vec):
    # vec,keywords = content_2_vec(content)
    result = await milvus_client.search(top_k=10,partition_list=None,vec=vec)
    if result['status']==1:return result
    search_milvus_id_list=result['message']
    if len(search_milvus_id_list)==0:
        return {'status':1,'message':'No sim text was found in milvus'}
    similar_milvus_id_list, dis_list = search_milvus_id_list._id_array[0], search_milvus_id_list._dis_array[0]
    #根据从milvus查询出的结果，搜索mysql中对应的类别并返回信息
    #删除的milvusid集合
    delids=[]
    #用于计算条件数量
    conds=[]
    #条件名和条件id
    conds_name={}
    # #条件和文件的集合
    # conds_file=defaultdict(list)
    #条件和文件的相似度集合
    conds_sim=defaultdict(list)
    #条件和文件及word的集合
    conds_file_word={} 
    #若有超过0.7的相似度的文本的结果
    big_sim_result={}
    cond_sql = "SELECT f_cond,f_cond_id,f_file_name,f_word FROM t_cond WHERE f_milvusid=%s;" 
    async with (await get_mysql_pool()).acquire() as conn, conn.cursor() as curs:
        #判断查询出来的值是否有超过0.7的，若有超过，则判断超过0.7的类别是否是不同的条件，若有则返回所有超过0.7的条件，为多条件，有几个就返回几个
        for i in range(len(dis_list)):
            if dis_list[i]<0.7:
                break
            line_num = await curs.execute(cond_sql, (similar_milvus_id_list[i],))
            await conn.commit()
            if line_num ==0:
                delids.append(similar_milvus_id_list[i])
                dis_list.pop(i)
                similar_milvus_id_list.pop(i)
                continue
            result =await curs.fetchall()
            one_big={}
            one_big['cond_id']=result[0][1]
            one_big['sim']=dis_list[0]
            one_big['sim_file']={result[0][2]:result[0][3].split(' ')}
            big_sim_result[result[0][0]]=one_big
        if len(big_sim_result)>0:return {'status':0,'multi_class':big_sim_result}   
        #若没有相似度超过0.7的文本，则要进行投票，最多返回三个类别
        for i in range(len(similar_milvus_id_list)):
            line_num = await curs.execute(cond_sql, (similar_milvus_id_list[i],))
            await conn.commit()
            if line_num ==0:
                delids.append(similar_milvus_id_list[i])
                continue
            result =await curs.fetchall()
            conds.append(result[0][0])
            conds_name[result[0][0]]=result[0][1]
            # conds_file[result[0][0]].append(result[0][2])
            if result[0][0] in conds_file_word:
                conds_file_word[result[0][0]][result[0][2]]=result[0][3].split(' ')
            else:
                f_w={}
                f_w[result[0][2]]=result[0][3].split(' ')
                conds_file_word[result[0][0]]=f_w
            conds_sim[result[0][0]].append(dis_list[i])
    if len(delids)>0:    
        result = milvus_client.delete_entity_by_id(delids)
        if result['status']==1:return result
    if len(conds)==0:
        return {'status':2,'message':'Mysql and milvus data are Inconsistency'}
    word_counter = Counter()
    word_counter.update(conds)
    c_n = sorted(word_counter.items(), key=lambda item:item[1], reverse=True)
    #利用knn思想，既通过top10个中属于同一类的个数大小判断，又通过一个类下的平均相似度判断
    knn_result={}
    for i in range(len(c_n)):
        cond_name = c_n[i][0]
        num_file= c_n[i][1]
        av_sim=sum(conds_sim[cond_name])/len(conds_sim[cond_name])
        #若top10中有7个以上都属于同一个类则直接判断文本属于这个类
        # if num_file>=7:
        #     one={}
        #     one['cond_id']=conds_name[cond_name]
        #     one['sim']=av_sim
        #     one['sim_file']=conds_file_word[cond_name]
        #     knn_result[cond_name]=one
        #     break
        #top10个没有7个及以上同属于一个类别，若只有少于2个包括2个个文本属于一个类别时，直接判断不属于这个类别
        if num_file<=2:
            continue
        if av_sim>=0.06:       
            one={}
            one['cond_id']=conds_name[cond_name]
            one['sim']=av_sim
            one['sim_file']=conds_file_word[cond_name]
            knn_result[cond_name]=one
        #最多返回3个类别
        if len(knn_result)>=3:
            break

    return {'status':0,'multi_class':knn_result}

# 停用词
# 获取停用词
def get_stopwords():
    stopwords_set = set()
    with open(stopwords_path, "r", encoding="utf-8") as f:
        str_data = f.read()
    for d in str_data.split("\n"):
        s = d.strip()
        stopwords_set.add(s)
        if len(s) > 0:
            stopwords_set.add(s[0].upper() + s[1:])
    return stopwords_set
stopwords = get_stopwords()

def extract_tag(content):
    # con_name = args[0]
    # content = args[1]
    content = content.replace('.','')
    content = content.replace('_','')
    cutone = jieba.analyse.extract_tags(content[:10000], topK=100)
    if len(cutone)<=2:return {"status":1,"message":"Too few keywords are extracted"}
    i=0
    words=''
    for word in cutone:
        if word not in stopwords and not word.isdigit():
            words += word + ' '
            i+=1
    if i>2:
        return {"status":0,"words":words.strip()}
    else:
        return {"status":1,"message":"Too few keywords are extracted"}

    # if len(cutone)>2:
    #     words = ''isdigit
    #     for word in cutone:
    #         if word not in stopwords:
    #             words += word + ' '
    #     return {"status":0,"words":words.strip()}
    # else:
    #     return {"status":1,"message":"Too few keywords are extracted"}
 
def _hash(w): 
    o=hashlib.md5(w.encode('utf8'))
    value = o.hexdigest()
    return int(value[:8], 16)
#从本地得到的文本数据向量化
def get_text_vec(keywords):  
    # keywords = cut_word(content)
    word_counter = Counter()
    keyword_list = keywords.split()
    word_counter.update(keyword_list)
    dim=5000
    word_list = []
    counter_list = []
    vec_list = []
    for word, cou in word_counter.items():
        word_list.append(word)
        counter_list.append(cou)
        h = _hash(word)
        np.random.seed(h)
        v=np.random.randn(1,dim)
        vec_list.append(v)
    word_dict = {w: i for i, w in enumerate(word_list)}
    frequnce = np.array(counter_list, dtype=np.float)
    vector_data = np.concatenate(vec_list,axis=0)
    vector_data /= (np.sum(vector_data ** 2, axis=1) ** 0.5)[:, np.newaxis]
    vector_data *= np.log(0.2 + frequnce[:, np.newaxis])
    def wordsFeature(keywords):
        inds = np.array([word_dict[w] for w in keywords], dtype=np.int)
        data = vector_data[inds.reshape(-1, 1), np.arange(dim).reshape([1, -1])].copy()
        data = data.sum(axis=0)
        data /= (data ** 2).sum() ** 0.5
        return data
    feature = wordsFeature(keyword_list)
    return feature