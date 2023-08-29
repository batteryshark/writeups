'''
Clocktower Text Injector by rFx
'''
import os,sys,struct,binascii

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def get_real_offset(offset):
	#Get High Value
	high_val = offset & 0xFFFF0000
	high_val /= 2
	low_val = offset & 0xFFFF
	return high_val+low_val
def get_fake_offset(offset):
	#Get High Value
	mult = int(offset / 0x8000)
	shft_val = 0x8000 * mult

	low_val = offset & 0xFFFF

	return offset + shft_val


f = open("CT_J.ADO","rb")
data = f.read()
f.close()

offset_vals = []
adt_list = []
newdata = ""
f = open("ct_txt_proc.txt","rb")
lines = f.readlines()
o,l,s = lines[0].split("\t")
first_offset = int(o,16)
o,l,s = lines[0].split("\t")
last_offset_strend = int(o,16) + int(l)
newdata = data[:first_offset]

for i in range(0,len(lines)):
	line = lines[i]
	offset, osl, instr = line.split("\t")
	offset = int(offset,16)

	instr = instr.rstrip('\n')

	instr = instr.replace("[NEWLINE]","\x0a")
	#Fix the ASCII characters.
	instr = instr.decode("SHIFT-JIS")
	newstr = ""
	for char in instr:
		if(is_ascii(char)):
			newstr+=char+'\x00'
		else:
			newstr+=char
	instr = newstr
	instr = instr.encode("SHIFT-JIS")
	newstrlen = len(instr)
	osl = int(osl)
	strldiff = newstrlen - osl

	#Replace the data
	if(i < len(lines)-1):
		nextline = lines[i+1]
		nextoffset,nsl,nstr = nextline.split("\t")
		offset_vals.append({"offset":offset,"val":strldiff})
		nextoffset = int(nextoffset,16)

		newdata += instr+data[offset+osl:nextoffset]
	else:
		offset_vals.append({"offset":offset,"val":strldiff})
		newdata += instr + data[offset+osl:]



#End of last string to EOF

f.close()

#Write new ADO File.
g = open("CT.ADO","wb")
g.write(newdata)
g.close()

#Fix up the ADT file.
f = open("CT_J.ADT","rb")
datat = f.read()
f.close()
g = open("CT.ADT","wb")

for i in range(0,len(datat),4):
	cur_offset = get_real_offset(struct.unpack("<I",datat[i:i+4])[0])
	final_adj = 0
	for offset in offset_vals:

		if(cur_offset > offset["offset"]):
			final_adj += offset["val"]
	g.write(struct.pack("<I",get_fake_offset(cur_offset + final_adj)))
g.close()
