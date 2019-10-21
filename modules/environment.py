# -*- coding: utf-8 -*-
import os

def run(**args):   # 可接受可變數量的引述
   print "[*] In environment module."
   return str(os.environ)  # 傳回所有環境變數
   