# MetaClass Implementing reading/writing of packed LC Executables
import pefile
import struct
import binascii
from py3rijndael import Rijndael
import pylc
import pe_imports

LCSH_SECTION_NAME = b".lcsh"
LEET_MOD_SECTION_NAME = b".l33t"

# Utility Function to Decrypt Blocks w/Rijndael
def rijndael_decrypt(key, data):
    outdata = b""
    r = Rijndael(key, block_size=16)
    for i in range(0, len(data), 16):
        outdata += r.decrypt(data[i:i + 16])
    return outdata

# Hamfisted way to get a cstring out of a buffer.
def get_cstr(data,start_offset):
    end_offset = data[start_offset:].find(b"\x00") + start_offset
    return data[start_offset:end_offset].decode('utf-8')

# This looks at every OFT and finds the lowest one to determine where the head of the IAT starts.
# I mean... it's not wrong, it's just stupid - LOL
def get_lowest_oft(data):
    lowest_value = 0xFFFFFFFF
    for i in range(0,len(data),0x14):
        tval = struct.unpack("<I",data[i:i+4])[0]
        if(tval < lowest_value and tval > 0):
            lowest_value = tval
    return lowest_value


class LC_Enveloped_EXE(object):
    def __init__(self,path_to_exe,exe_key=b""):
        self.valid = False
        self.pe = pefile.PE(path_to_exe)
        self.exe_key = exe_key
        if self._read_packer_section() is False:
            return

        self.valid = True


    # Reads Key Values from .lcsh section - these offsets may change between versions.
    def _read_packer_section(self):
        for i in range(0, len(self.pe.sections)):
            if (LCSH_SECTION_NAME in self.pe.sections[i].Name):

                data = self.pe.get_data(self.pe.sections[i].VirtualAddress,self.pe.sections[i].Misc_VirtualSize)
                self.image_base = struct.unpack("<I", data[0x12E88:0x12E8C])[0]
                self.oep = struct.unpack("<I", data[0x12E28:0x12E2C])[0]
                self.relocation_offset = struct.unpack("<I", data[0x12EB0:0x12EB4])[0]

                # Excise Import Address Table Blob
                ib_rva = struct.unpack("<I", data[0x12E30:0x12E34])[0]
                ib_size = struct.unpack("<I", data[0x12ED4:0x12ED8])[0] & 0xFFF0
                encrypted_iat_blob = self.pe.get_data(ib_rva,ib_size)

                # Excise Import Descriptor Table Blob
                idt_offset = struct.unpack("<I", data[0x12E60:0x12E64])[0] - self.pe.sections[i].VirtualAddress
                self.idt = pe_imports.ImportDescriptorTable(data[idt_offset:])

                # Excise Dongle Stuff
                self.lc_developer_id = struct.unpack("<I", data[0x12DA4:0x12DA8])[0]
                self.exe_pre_key = data[0x12DB0:0x12DC0]
                self.lc_password = data[0x12DC0:0x12DC8]

                # If the EXE key is given, we don't need to ask the dongle for it.
                if self.exe_key is b"":
                    status, self.exe_key = pylc.lc_encrypt(self.lc_developer_id, self.lc_password, self.exe_pre_key)
                    if status is True:
                        self.valid = True
                    else:
                        print("LC_Encrypt Fail!")
                        return False

                # If everything is good so far, might as well decrypt and parse the IAT Blob
                if self.parse_iat_blob(rijndael_decrypt(self.exe_key,encrypted_iat_blob),ib_rva) is False:
                    print("Parse IAT Blob Fail!")
                    return False

                print("--[Packer Section]--")
                print("Image Base: 0x%04X" % self.image_base)
                print("Original Entry Point: 0x%04X" % self.oep)
                print("Relocation Section: 0x%04X" % self.relocation_offset)
                print("LC Developer ID: 0x%04X" % self.lc_developer_id)
                print("LC Password: %s" % self.lc_password.decode('utf-8'))
                print("EXE Pre Key: %s" % binascii.hexlify(self.exe_pre_key))
                print("EXE Key: %s" % binascii.hexlify(self.exe_key))
                print(self.idt)
                print("[Imports]")
                for entry in self.import_db:
                    print("  %s" % entry['dll_name'])
                    for im in entry['functions']:
                        if(im['ordinal'] != 0):
                            print("\t Ordinal: %02X" % im['ordinal'])
                        else:
                            print("\t %s" % im['name'])
                return True
        return False

    def parse_iat_blob(self,data,base_rva):
        print("Parsing IAT Blob...")
        end_lib_entries = False
        self.import_db = []
        offset = 0
        while end_lib_entries is False:
            offset_lib_name = struct.unpack("<I", data[offset + 12:offset + 16])[0]
            offset_func_table = struct.unpack("<I", data[offset + 16:offset + 20])[0]

            offset += 20
            lib_name = get_cstr(data, offset_lib_name - base_rva)

            if (offset_lib_name == 0 or offset_func_table == 0):
                end_lib_entries = True
                print("Parsing IAT Blob... Done!")
                return True
                # Get Function Table.
            offset_func_table = offset_func_table - base_rva
            func_table = []

            offset_func_table_offset = 0
            end_func_entries = False
            while end_func_entries is False:
                f_offset = struct.unpack("<I", data[
                                               offset_func_table_offset + offset_func_table:offset_func_table_offset + offset_func_table + 4])[
                    0]
                if (f_offset is 0):
                    end_func_entries = True
                    break
                func_ordinal = 0

                if (f_offset > 0x80000000):
                    func_ordinal = f_offset
                    func_name = ""
                else:
                    f_offset -= base_rva
                    func_name = get_cstr(data, f_offset + 2)
                func_table.append({
                    "name": func_name,
                    "ordinal": func_ordinal
                })
                offset_func_table_offset += 4

            self.import_db.append({
                "dll_name": get_cstr(data, offset_lib_name - base_rva),
                "functions": func_table
            })

        return False

    def decrypt_code_sections(self):
        print("Decrypting CODE Sections...")
        for i in range(0, len(self.pe.sections)):
            if not LCSH_SECTION_NAME in self.pe.sections[i].Name:
                if self.pe.sections[i].IMAGE_SCN_MEM_EXECUTE is True:
                    enc_data = self.pe.get_data(self.pe.sections[i].VirtualAddress,length=self.pe.sections[i].SizeOfRawData)
                    self.pe.set_bytes_at_offset(self.pe.sections[i].PointerToRawData, rijndael_decrypt(self.exe_key, enc_data))
                    print("Decrypted Section %s" % self.pe.sections[i].Name.decode('utf-8'))
        print("Decrypting CODE Sections... Done!")
        return True

    def write_import_tables(self):
        print("Writing Import Tables...")
        lowest_oft = 0xFFFFFFFF
        for i in range(0,len(self.idt.entries)):
            if self.idt.entries[i].p_original_first_thunk > 0 and self.idt.entries[i].p_original_first_thunk < lowest_oft:
                lowest_oft = self.idt.entries[i].p_original_first_thunk

        if lowest_oft == 0 or lowest_oft == 0xFFFFFFFF :
            print("Write Import Table Failure!")
            return False

        b_idt = self.idt.serialize()
        original_iat_offset = self.pe.get_offset_from_rva(lowest_oft)
        original_iat_offset -= len(b_idt)
        self.original_iat_rva = self.pe.get_rva_from_offset(original_iat_offset)
        print("Import Table (%d Bytes) Written to 0x%04X RVA: 0x%04X" % (len(b_idt),original_iat_offset,self.original_iat_rva))
        self.pe.set_bytes_at_offset(original_iat_offset, b_idt)

        # Adjust our Import Header Offsets/Sizes
        for j in range(0, len(self.pe.OPTIONAL_HEADER.DATA_DIRECTORY)):
            cd = self.pe.OPTIONAL_HEADER.DATA_DIRECTORY[j]
            if (cd.name is "IMAGE_DIRECTORY_ENTRY_IMPORT"):
                self.pe.OPTIONAL_HEADER.DATA_DIRECTORY[j].VirtualAddress = self.original_iat_rva
                self.pe.OPTIONAL_HEADER.DATA_DIRECTORY[j].Size = len(b_idt)
        return True

    def restore_dll_strings(self):
        print("Restoring Original DLL Strings...")
        for i in range(0, len(self.import_db)):
            dest_dllname_offset = self.pe.get_offset_from_rva(self.idt.entries[i].p_name)
            bdll_name = self.import_db[i]['dll_name'].encode('ascii')
            self.pe.set_bytes_at_offset(dest_dllname_offset,bdll_name)
        return True

    def write_thunk_tables(self, thunk_offset):
        print("Writing New Thunk Tables...")
        function_tables = b""
        for i in range(0, len(self.import_db)):
            for j in range(0, len(self.import_db[i]["functions"])):
                cf = self.import_db[i]["functions"][j]
                if (cf["name"] == ""):
                    self.import_db[i]["functions"][j]['entry_offset'] = cf["ordinal"]
                else:
                    bname = cf["name"].encode('ascii') + b"\x00"
                    bentry = b"\x00\x00" + bname
                    if (len(bname) % 2 == 1):
                        bentry += b"\x00"
                    self.import_db[i]["functions"][j]['entry_offset'] = thunk_offset + len(function_tables)
                    function_tables += bentry

        self.pe.set_bytes_at_offset(thunk_offset, function_tables)
        self.thunk_table_size = len(function_tables)
        return True


    def fix_relocations(self):
        print("Fixing Relocations...")
        for i in range(0, len(self.import_db)):
            bdata = b""
            for j in range(0, len(self.import_db[i]['functions'])):
                entry_offset = self.import_db[i]['functions'][j]['entry_offset']
                if (entry_offset > 0x80000000):  # ORDINALS
                    bdata += struct.pack("<I", entry_offset)
                else:
                    bdata += struct.pack("<I", self.pe.get_rva_from_offset(entry_offset))

            self.pe.set_bytes_at_offset(self.pe.get_offset_from_rva(self.idt.entries[i].p_original_first_thunk), bdata)
            self.pe.set_bytes_at_offset(self.pe.get_offset_from_rva(self.idt.entries[i].p_first_thunk), bdata)


    def fix_header(self):
        print("Fixing PE Header...")
        rva_oep = self.oep - self.image_base
        self.pe.OPTIONAL_HEADER.AddressOfEntryPoint = rva_oep
        print("OEP Set to 0x%04X" % rva_oep)

        print("Rename .lcsh Section...")
        self.pe.sections[-1].Name = b".l33t\x00\x00\x00"
        self.pe.sections[-1].SizeOfRawData = self.thunk_table_size
        self.pe.__data__ = self.pe.__data__[:self.pe.sections[-1].PointerToRawData + self.pe.sections[-1].SizeOfRawData]

        if (self.relocation_offset != 0):
            for j in range(0, len(self.pe.OPTIONAL_HEADER.DATA_DIRECTORY)):
                cd = self.pe.OPTIONAL_HEADER.DATA_DIRECTORY[j]
                if (cd.name is "IMAGE_DIRECTORY_ENTRY_BASERELOC"):
                    self.pe.OPTIONAL_HEADER.DATA_DIRECTORY[j].VirtualAddress = self.relocation_offset
                    self.pe.OPTIONAL_HEADER.DATA_DIRECTORY[j].Size = self.pe.OPTIONAL_HEADER.SizeOfImage - self.relocation_offset
        return True


    def unpack(self):
        if self.decrypt_code_sections() is False:
            return False

        if self.write_import_tables() is False:
            return False

        if self.restore_dll_strings() is False:
            return False

        if self.write_thunk_tables(self.pe.sections[-1].PointerToRawData) is False:
            return False

        if self.fix_relocations() is False:
            return False

        if self.fix_header() is False:
            return False

        return True

    # Save a copy of the modified exe - truncate any
    # unnecessary garbage at the end of the image.
    def save(self,output_path):
        data = self.pe.write()
        with open(output_path,"wb") as g:
            g.write(data[:len(self.pe.__data__)])
