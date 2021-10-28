import os,sys,json
import numpy as np
import web
_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),os.path.dirname(__file__), path))

img_dir='CheckImageData'
def create_summary_dict():
    summary_dict={}
    test_dir=_get_module_path(img_dir)
    with open('old_summary.txt', 'r') as fr:
        for line in fr:
            img,tmp = line.split('#')
            tmp = tmp.split()
            idx = tmp[0]
            summary = ' '.join(tmp[1:])
            if img not in summary_dict:
                summary_dict[img] = {}
            if 'old_summary_list' not in summary_dict[img]:
                summary_dict[img]['old_summary_list'] = [summary]
            else:
                summary_dict[img]['old_summary_list'].append(summary)

    os.system('touch new_summary.txt')
    with open('new_summary.txt', 'r') as fr:
        for line in fr:
            img,tmp = line.split('#')
            tmp = tmp.split()
            idx = tmp[0]
            summary = ' '.join(tmp[1:])
            if img not in summary_dict:
                summary_dict[img]={}
            if 'new_summary_list' not in summary_dict[img]:
                summary_dict[img]['new_summary_list'] = [summary]
            else:
                summary_dict[img]['new_summary_list'].append(summary)
    return summary_dict

summary_dict=create_summary_dict()

class index():
    def GET(self):
        pass

class img():
    def GET(self):
        web.header("Access-Control-Allow-Origin", "*")
        params=web.input()
        img=params['name']
        if img not in summary_dict:
            return json.dumps(dict(status=1,message='IMAGE NOT FOUND: %s'%img))
        url='http://server-ip:54321/CheckImageData/%s'%img
        if 'new_summary_list' in summary_dict[img]:
            check_done=True
            summary_list=summary_dict[img]['new_summary_list']
        else:
            check_done=False
            summary_list=summary_dict[img]['old_summary_list']
        return json.dumps(dict(name=img,url=url,summary_list=summary_list,check_done=check_done,count=len(summary_dict),res_count=len([img for img in summary_dict if 'new_summary_list' not in summary_dict[img]])))

class img_list():
    def GET(self):
        web.header("Access-Control-Allow-Origin", "*")
        return_dict=dict(status=0,count=len(summary_dict),res_count=len([img for img in summary_dict if 'new_summary_list' not in summary_dict[img]]))
        results=[]
        for img, summary_info in summary_dict.items():
            url='http://server-ip:54321/CheckImageData/%s'%img
            if 'new_summary_list' in summary_dict[img]:
                check_done=True
                summary_list=summary_dict[img]['new_summary_list']
            else:
                check_done=False
                summary_list=summary_dict[img]['old_summary_list'] 
            results.append(dict(
                name=img,
                url=url,
                summary_list=summary_list,
                check_done=check_done
            ))
        return_dict['results'] = results
        return json.dumps(return_dict)

class submit_summary():
    def GET(self):
        web.header("Access-Control-Allow-Origin", "*") 
        params=web.input()
        img = params['name']
        if img not in summary_dict: return json.dumps(dict(message='IMAGE NOT FOUND: %s'%img, status=1))
        summary_list = [params[k] for k in params.keys() if 'summary'in k]
        print(summary_list)
        summary_dict[img]['new_summary_list'] = summary_list
        return json.dumps(dict(status=0))

class dump_to_file():
    def GET(self):
        with open('new_summary.txt','w') as fp:
            for img, _summary in summary_dict.items():
                if 'new_summary_list' not in _summary: continue
                new_summary_list = _summary['new_summary_list']
                sid=0
                for s in set(new_summary_list):
                    s = new_summary_list[sid]
                    if len(s)<5: continue
                    fp.write('%s#%s %s\n'%(img,sid,s))
                    sid += 1
        return 'domp to file new_summary.txt SUCCESS!!!\n'
                    

urls=(
    '/', 'index',
    '/image', 'img',
    '/image/list', 'img_list',
    '/submit_summary', 'submit_summary',
    '/dump_to_file', 'dump_to_file'
)
if __name__=='__main__':
    app = web.application(urls,globals())
    app.run()
