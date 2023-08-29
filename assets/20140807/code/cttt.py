#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Clocktower Auto Translator by rFx
'''
import os,sys,binascii,struct
from translate import Translator
translator = Translator(to_lang="en") #Set to English by Default



f = open("ct_txt.txt","rb")
g = open("ct_txt_proc2.txt","wb")
proc_str = []
for line in f.readlines():
	proc_str.append(line.rstrip())

for x in range(0,len(proc_str)):
	line = proc_str[x]
	o,l,instr = line.split("\t")

	ts = translator.translate(instr.decode("SHIFT-JIS").encode("UTF-8"))

	ts = ts.encode("SHIFT-JIS","replace")
	proc_str[x] = "%s\t%s\t%s" % (o,l,ts)
	g.write(proc_str[x]+"\n")


#for pc in proc_str:
#	g.write(pc)

g.close()
