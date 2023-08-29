import ctypes,struct

IMAGE_ORDINAL_FLAG32 = 0x80000000


# Import Descriptor Table Helpers
class IDTEntry(ctypes.Structure):
    _pack_ = 1
    _fields_ = [('p_original_first_thunk', ctypes.c_int32),
                ('time_datestamp', ctypes.c_uint32),
                ('forwarder_chain', ctypes.c_int32),
                ('p_name', ctypes.c_int32),
                ('p_first_thunk', ctypes.c_int32)]
    def __new__(self, sb=None):
        if sb:
            return self.from_buffer_copy(sb)
        else:
            return ctypes.Structure.__new__(self)


def get_idt_entry_size():
    return ctypes.sizeof(IDTEntry)



class ImportDescriptorTable(object):
    def __init__(self,data):
        self.entries = []
        entry_size = get_idt_entry_size()
        for i in range(0,len(data),entry_size):
            ne = IDTEntry(sb=data[i:i+entry_size])
            self.entries.append(ne)
            if ne.p_original_first_thunk == 0:
                break

    def serialize(self):
        bdata = b""
        for entry in self.entries:
            bdata+= struct.pack("<I",entry.p_original_first_thunk) + \
                struct.pack("<I", entry.time_datestamp) + \
                struct.pack("<I", entry.forwarder_chain) + \
                struct.pack("<I", entry.p_name) + \
                struct.pack("<I", entry.p_first_thunk)
        return bdata

    def __str__(self):
        print("[Import Descriptor Table]")
        for entry in self.entries:
            print("pOFT: 0x%04X, Time/DateStamp: %d, Forwarder Chain: 0x%04X, pName: 0x%04X, pFirstThunk: 0x%04X" % (entry.p_original_first_thunk,entry.time_datestamp, entry.forwarder_chain,entry.p_name,entry.p_first_thunk))
        return ""
