'''
 CTD - Clocktower Text Dumper by rFx
'''

import os,sys,struct,binascii

f = open("CT_J.ADO","rb")
data = f.read()
f.close()
g = open("ct_txt.txt","wb")
for i in range(0,len(data)-1):
	if(data[i] == '\x33' and data[i+1] == '\xff'):
		#We have to skip 6 because of the opcodes and values we don't care about changing.
		i+=6
		str_offset = i
		str_end = data[i:].index('\xff') -1
		newstr = data[i:i+str_end]
		strlen = len(newstr)
		newstr = newstr.replace("\x0a\x00","[NEWLINE]")
		#The game puts nulls after any ASCII character, we need to remove those.
		newstr = newstr.replace("\x00","")
		g.write("%#x\t%d\t" % (str_offset,strlen))
		g.write(newstr)
		g.write("\n")

g.close()
