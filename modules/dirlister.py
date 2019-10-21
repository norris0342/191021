# -*- coding: utf-8 -*-
import os

def run(**args):   # 可接受可變數量的引述
   print "[*] In dirlister module."
   files = os.listdir(".")  # 目前檔案夾下所有檔案
   
   return str(files)
   