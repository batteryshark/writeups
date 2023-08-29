# Unpack Script for Senselock LC (Clave2) Envelope
import os
import sys
import binascii
import lcshell


def usage():
    print("%s path/to/exe [optional_hex_decryptedkey]" % sys.argv[0])
    exit(-1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Arguments Invalid")
        usage()
    if not os.path.exists(sys.argv[1]):
        print("EXE Path Invalid")
        usage()

    path_to_exe = sys.argv[1]
    unpacked_path = os.path.splitext(path_to_exe)[0] + "_Unpacked.exe"

    # Load Optional EXE Key
    given_exe_key = b""
    if (len(sys.argv) > 2):
        try:
            given_exe_key = binascii.unhexlify(sys.argv[2])
        except Exception as e:
            print("EXE Key must be ASCII HEX")
            print(e)
            usage()

    lc_pe = lcshell.LC_Enveloped_EXE(path_to_exe,given_exe_key)
    if lc_pe.valid is False:
        print("Error Reading Enveloped PEFile")
        exit(-1)

    if lc_pe.unpack() is False:
        print("Error Unpacking Enveloped PEFile")
        exit(-1)

    lc_pe.save(unpacked_path)
    print("DonionRingz!")
    exit(0)