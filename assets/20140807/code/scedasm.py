'''
Clocktower ADC Object File Disassembler by rFx
'''
import os,sys,binascii,struct

ADO_FILENAME = "CT_J.ADO"
ADT_FILENAME = "CT_J.ADT"

ADO_OP = {
0xFF00:"RETN", #Scene Prologue - 0 bytes of data. - Also an END value... the game looks to denote endings.
0xFF01:"UNK_01", # varying length data
0xFF02:"UNK_02", # 3 bytes of data
0xFF03:"UNK_03", # 3 bytes of data
0xFF04:"UNK_04", # 3 bytes of data
0xFF05:"UNK_05", # 3 bytes of data
0xFF06:"UNK_06", # 3 bytes of data
0xFF07:"UNK_07", # 3 bytes of data
0xFF0A:"UNK_0A", # 4 bytes of data. Looks like an offset to another link in the list?
0xFF0C:"UNK_0C", # 4 bytes of data
0xFF0D:"UNK_0D", # 4 bytes of data
0xFF10:"UNK_10", # 4 bytes of data
0xFF11:"UNK_11", # 4 bytes of data
0xFF12:"UNK_12", # 4 bytes of data
0xFF13:"UNK_13", # 4 bytes of data
0xFF14:"UNK_14", # 4 bytes of data
0xFF15:"UNK_15", # 4 bytes of data
0xFF16:"UNK_16", # 4 bytes of data
0xFF1F:"UNK_1F", # 0 bytes of data
0xFF20:"ALL", # 0 bytes of data. Only at the end of the ADO (twice)
#All opcodes above this are like... prologue opcodes (basically in some other list)
0xFF21:"ALLEND",  # 2 bytes of data
0xFF22:"JMP",  # 2 bytes of data - I think it uses the value for the int offset in adt as destination +adds 2
0xFF23:"CALL",  # 6 bytes of data
0xFF24:"EVDEF", # Not used in the game
0xFF25:"!!!!!!", #Not used in the game
0xFF26:"!!!!!!", #Not used in the game
0xFF27:"!!!!!!", #Not used in the game
0xFF28:"!!!!!!", #0 bytes of data.
0xFF29:"END_IF", # 4 bytes of data
0xFF2A:"WHILE",  # 4 bytes of data
0xFF2B:"NOP",    # 0 bytes of data
0xFF2C:"BREAK", # Not used in the game
0xFF2D:"ENDIF",  # 2 bytes of data
0xFF2E:"ENDWHILE",  # 2 bytes of data
0xFF2F:"ELSE",   # 2 bytes of data
0xFF30:"MSGINIT",   # 10 bytes of data
0xFF31:"MSGTYPE",   # Not used in the game
0xFF32:"MSGATTR",   # 16 bytes of data
0xFF33:"MSGOUT",   # Varying length, our in-game text uses this. :)
0xFF34:"SETMARK", #Varying length
0xFF35:"SETWAIT",  #Not used in the game
0xFF36:"MSGWAIT", #0 bytes of data
0xFF37:"EVSTART", #4 bytes of data
0xFF38:"BGFILEDISP", #Not used in the game.
0xFF39:"BGLOAD", #Varying length, normally a path to a BMP file is passed in.
0xFF3A:"PALLOAD", #Varying length. Also takes BMP files.
0xFF3B:"BGMREQ", #Varying length - loads a MIDI file into memory.
0xFF3C:"SPRCLR", #2 bytes of data.
0xFF3D:"ABSOBJANIM", #Not used in the game
0xFF3E:"OBJANIM", #Not used in the game.
0xFF3F:"ALLSPRCLR", #0 bytes of data
0xFF40:"MSGCLR", #0 bytes 0f data
0xFF41:"SCREENCLR", #0 bytes of data
0xFF42:"SCREENON", #0 bytes of data
0xFF43:"SCREENOFF", #0 bytes of data
0xFF44:"SCREENIN", # Not used in the game.
0xFF45:"SCREENOUT", # Not used in the game.
0xFF46:"BGDISP", # Always 12 bytes of data.
0xFF47:"BGANIM", #14 bytes of data.
0xFF48:"BGSCROLL",#10 bytes of data.
0xFF49:"PALSET", #10 bytes of data.
0xFF4A:"BGWAIT", #0 bytes of data.
0xFF4B:"WAIT", #4 bytes of data.
0xFF4C:"BWAIT", #Not used in the game.
0xFF4D:"BOXFILL", #14 bytes of data.
0xFF4E:"BGCLR", # Not used in the game.
0xFF4F:"SETBKCOL", #6 bytes of data.
0xFF50:"MSGCOL", #Not used in the game.
0xFF51:"MSGSPD", #2 bytes of data.
0xFF52:"MAPINIT", #12 bytes of data.
0xFF53:"MAPLOAD", #Two Paths... Sometimes NULL NULL - Loads the background blit bmp and the map file to load it.
0xFF54:"MAPDISP", #Not used in the game.
0xFF55:"SPRENT", #16 bytes of data.
0xFF56:"SETPROC", #2 bytes of data.
0xFF57:"SCEINIT", #0 bytes of data.
0xFF58:"USERCTL", #2 bytes of data.
0xFF59:"MAPATTR", #2 bytes of data.
0xFF5A:"MAPPOS", #6 bytes of data.
0xFF5B:"SPRPOS", #8 bytes of data.
0xFF5C:"SPRANIM", #8 bytes of data.
0xFF5D:"SPRDIR", #10 bytes of data.
0xFF5E:"GAMEINIT", #0 bytes of data.
0xFF5F:"CONTINIT", #0 bytes of data.
0xFF60:"SCEEND", #0 bytes of data.
0xFF61:"MAPSCROLL", #6 bytes of data.
0xFF62:"SPRLMT", #6 bytes of data.
0xFF63:"SPRWALKX", #10 bytes of data.
0xFF64:"ALLSPRDISP", #Not used in the game.
0xFF65:"MAPWRT", #Not used in the game.
0xFF66:"SPRWAIT", #2 bytes of data.
0xFF67:"SEREQ", #Varying length - loads a .WAV file.
0xFF68:"SNDSTOP", #0 bytes of data.
0xFF69:"SESTOP", #Varying length - specifies a .WAV to stop or ALL for all sounds.
0xFF6A:"BGMSTOP", #0 bytes of data.
0xFF6B:"DOORNOSET", #0 bytes of data.
0xFF6C:"RAND", #6 bytes of data.
0xFF6D:"BTWAIT", #2 bytes of data
0xFF6E:"FAWAIT", #0 bytes of data
0xFF6F:"SCLBLOCK", #Varying length - no idea.
0xFF70:"EVSTOP", #Not used in the game.
0xFF71:"SEREQPV", #Varying length - .WAV path input, I think this is to play and repeat.
0xFF72:"SEREQSPR", #Varying length - .WAV path input, I think this is like SEREQPV except different somehow.
0xFF73:"SCERESET", #0 bytes of data.
0xFF74:"BGSPRENT", #12 bytes of data.
0xFF75:"BGSPRPOS", #Not used in the game.
0xFF76:"BGSPRSET", #Not used in the game.
0xFF77:"SLANTSET", #8 bytes of data.
0xFF78:"SLANTCLR", #0 bytes of data.
0xFF79:"DUMMY", #Not used in the game.
0xFF7A:"SPCFUNC", #Varying length - usage uncertain.
0xFF7B:"SEPAN", #Varying length - guessing to set the L/R of Stereo SE.
0xFF7C:"SEVOL", #Varying length - guessing toe set the volume level of SE
0xFF7D:"BGDISPTRN", #14 bytes of data.
0xFF7E:"DEBUG", #Not used in the game.
0xFF7F:"TRACE", #Not used in the game.
0xFF80:"TMWAIT", #4 bytes of data.
0xFF81:"BGSPRANIM", #18 bytes of data.
0xFF82:"ABSSPRENT", #Not used in the game.
0xFF83:"NEXTCOM", #2 bytes of data.
0xFF84:"WORKCLR", #0 bytes of data.
0xFF85:"BGBUFCLR", #4 bytes of data.
0xFF86:"ABSBGSPRENT", #12 bytes of data.
0xFF87:"AVIPLAY", #This one is used only once - to load the intro AVI file.
0xFF88:"AVISTOP", #0 bytes of data.
0xFF89:"SPRMARK", #Only used in PSX Version.
0xFF8A:"BGMATTR",#Only used in PSX Version.
#BIG GAP IN OPCODES... maybe not even in existence.
0xFFA0:"UNK_A0", #12 bytes of data.
0xFFB0:"UNK_B0", #12 bytes of data.
0xFFDF:"UNK_DF", #2 bytes of data.
0xFFE0:"UNK_E0", #0 bytes of data.
0xFFEA:"UNK_EA", #0 bytes of data.
0xFFEF:"UNK_EF" #12 bytes of data.
}

if(__name__=="__main__"):
	print("#Disassembling ADO/ADT...")
	#Read ADO/ADT Data to memory.
	f = open(ADO_FILENAME,"rb")
	ado_data = f.read()
	f.close()
	f = open(ADT_FILENAME,"rb")
	adt_data = f.read()
	f.close()
	scene_count = -1
	#Skip ADO Header
	i = 256
	while i < (len(ado_data) -1):
		cur_val = struct.unpack("<H",ado_data[i:i+2])[0]

		if(cur_val in ADO_OP.keys()):
			#0xFF00
			if(cur_val == 0xFF00):
				scene_count +=1
				print("#----SCENE %d (Offset %#x)" % (scene_count,i))
				print(ADO_OP[cur_val])
				i+=2
			elif(cur_val == 0xFF1F or cur_val == 0xFF20 or cur_val == 0xFF84 or cur_val == 0xFFEA or cur_val == 0xFFE0
 or cur_val == 0xFF88 or cur_val == 0xFF78 or cur_val == 0xFF73 or cur_val == 0xFF6E or cur_val == 0xFF6B
 or cur_val == 0xFF6A or cur_val == 0xFF68 or cur_val == 0xFF60 or cur_val == 0xFF5F or cur_val == 0xFF5E
 or cur_val == 0xFF57 or cur_val == 0xFF4A or cur_val == 0xFF43 or cur_val == 0xFF42 or cur_val == 0xFF41
 or cur_val == 0xFF40 or cur_val == 0xFF36 or cur_val == 0xFF3F or cur_val == 0xFF36 or cur_val == 0xFF2B or cur_val == 0xFF28):


				print(ADO_OP[cur_val])
				i+=2
			#0xFF22
			elif(cur_val == 0xFF22 or cur_val == 0xFF51 or cur_val == 0xFF21 or
				cur_val == 0xFF2D or cur_val == 0xFF2E or cur_val == 0xFF2F or cur_val == 0xFF3C
				or cur_val == 0xFF56 or cur_val == 0xFF58 or cur_val == 0xFF59 or cur_val == 0xFF66
				or cur_val == 0xFF6D or cur_val == 0xFF83 or cur_val == 0xFFDF):
				i+=2
				jmpdata = struct.unpack("<H",ado_data[i:i+2])[0]
				print("%s %d" % (ADO_OP[cur_val],jmpdata))
				i+=2
			#0xFF23
			elif(cur_val == 0xFF23):
				i+=2
				val_1 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_2 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_3 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				print("%s %#x %#x %#x" % (ADO_OP[cur_val],val_1,val_2,val_3))
			elif cur_val == 0xFF29 or cur_val == 0xFF2A or cur_val == 0xFF37:
				i+=2
				val_1 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_2 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				print("%s %d %d" % (ADO_OP[cur_val],val_1,val_2))
			elif cur_val in range(0xFF02,0xFF08):
				i+=2
				pri_val = struct.unpack("b",ado_data[i])[0]
				i+=1
				sec_val = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				print("%s %d %d" % (ADO_OP[cur_val],pri_val,sec_val))
			elif cur_val in range(0xFF0A,0xFF17):
				i+=2
				pri_val = struct.unpack("<I",ado_data[i:i+4])[0]
				i+=4
				print("%s %#x" % (ADO_OP[cur_val],pri_val))
			elif (cur_val == 0xFF30):
				i+=2
				val_1 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_2 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_3 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_4 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_5 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				print("%s %#x %#x %#x %#x %#x" % (ADO_OP[cur_val],val_1,val_2,val_3,val_4,val_5))
			elif (cur_val == 0xFF33):
				i+=2
				val_1 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_2 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				endstr_offset = ado_data[i:].index("\xff")
				endstr_offset -=1

				instr = ado_data[i:i+endstr_offset]
				i+= len(instr)
				#Decode to UTF-8
				instr = instr.replace("\x0a\x00","[NEWLINE]")
				instr = instr.replace("\x00","[NULL]")
				instr = instr.decode("SHIFT-JIS")
				instr = instr.encode("UTF-8")

				print("%s %#x %#x ``%s``" % (ADO_OP[cur_val],val_1,val_2,instr))
			elif (cur_val == 0xFF32):
				i+=2
				val_1 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_2 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_3 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_4 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_5 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_6 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_7 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_8 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				print("%s %#x %#x %#x %#x %#x %#x %#x %#x" % (ADO_OP[cur_val],val_1,val_2,val_3,val_4,val_5,val_6,val_7,val_8))
			elif(cur_val == 0xFF34):
				i+=2
				endval_offset = ado_data[i:].index("\xff") - 1
				instr = ado_data[i:i+endstr_offset]
				i+= len(instr)
				print("%s %s" % (ADO_OP[cur_val],binascii.hexlify(instr)))
				i+=2
			elif(cur_val in range(0xFF39,0xFF3C) or cur_val == 0xFF67):
				i+=2
				val_1 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				endstr_offset = ado_data[i:].index("\xff") - 1
				instr = ado_data[i:i+endstr_offset]
				i+= len(instr)
				if(instr.find("\x00\x00\x00") != -1):
					finstr = instr[:instr.index("\x00")]
					val_2 = struct.unpack("b",instr[instr.index("\x00")+1:instr.index("\x00")+2])[0]
					val_3 = struct.unpack("b",instr[instr.index("\x00")+2:])[0]
					print("%s %#x %s %#x %#x" % (ADO_OP[cur_val],val_1,finstr,val_2,val_3))
				elif(instr.find("\x00\x00") != -1):
					finstr = instr[:instr.index("\x00")]
					val_2 = struct.unpack("b",instr[instr.index("\x00")+1:])[0]
					print("%s %#x %s %#x" % (ADO_OP[cur_val],val_1,finstr,val_2))
			elif(cur_val == 0xFF69):
				i+=2
				endstr_offset = ado_data[i:].index("\xff") - 1
				instr = ado_data[i:i+endstr_offset]
				i+= len(instr)
				if(instr.find("\x00\x00\x00") != -1):
					finstr = instr[:instr.index("\x00")]
					val_2 = struct.unpack("b",instr[instr.index("\x00")+1:instr.index("\x00")+2])[0]
					val_3 = struct.unpack("b",instr[instr.index("\x00")+2:])[0]
					print("%s %s %#x %#x" % (ADO_OP[cur_val],finstr,val_2,val_3))
				elif(instr.find("\x00\x00") != -1):
					finstr = instr[:instr.index("\x00")]
					val_2 = struct.unpack("b",instr[instr.index("\x00")+1:])[0]
					print("%s %s %#x" % (ADO_OP[cur_val],finstr,val_2))

			elif(cur_val == 0xFF71 or cur_val == 0xFF72):
				i+=2
				val_1 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_2 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_3 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				endstr_offset = ado_data[i:].index("\xff") - 1
				instr = ado_data[i:i+endstr_offset]
				i+= len(instr)
				if(instr.find("\x00\x00\x00") != -1):
					finstr = instr[:instr.index("\x00")]
					val_4 = struct.unpack("b",instr[instr.index("\x00")+1:instr.index("\x00")+2])[0]
					val_5 = struct.unpack("b",instr[instr.index("\x00")+2:])[0]
					print("%s %#x %#x %#x %s %#x %#x" % (ADO_OP[cur_val],val_1,val_2,val_3,finstr,val_4,val_5))
				elif(instr.find("\x00\x00") != -1):
					finstr = instr[:instr.index("\x00")]
					val_4 = struct.unpack("b",instr[instr.index("\x00")+1:])[0]
					print("%s %#x %#x %#x %s %#x" % (ADO_OP[cur_val],val_1,val_2,val_3,finstr,val_4))
			elif(cur_val == 0xFF87):
				i+=2
				val_1 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_2 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_3 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_4 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				val_5 = struct.unpack("<H",ado_data[i:i+2])[0]
				i+=2
				endstr_offset = ado_data[i:].index("\xff") - 1
				instr = ado_data[i:i+endstr_offset]
				i+= len(instr)
				if(instr.find("\x00\x00\x00") != -1):
					finstr = instr[:instr.index("\x00")]
					val_6 = struct.unpack("b",instr[instr.index("\x00")+1:instr.index("\x00")+2])[0]
					val_7 = struct.unpack("b",instr[instr.index("\x00")+2:])[0]
					print("%s %#x %#x %#x %#x %#x %s %#x %#x" % (ADO_OP[cur_val],val_1,val_2,val_3,val_4,val_5,finstr,val_6,val_7))
				elif(instr.find("\x00\x00") != -1):
					finstr = instr[:instr.index("\x00")]
					val_6 = struct.unpack("b",instr[instr.index("\x00")+1:])[0]
					print("%s %#x %#x %#x %#x %#x %s %#x" % (ADO_OP[cur_val],val_1,val_2,val_3,val_4,val_5,finstr,val_6))

			#NOT DONE YET
			else:
				i+=1
		else:
			i+=1
