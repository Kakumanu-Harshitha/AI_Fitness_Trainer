import ctypes
import os
import sys

def check_dlls(bin_dir):
    print(f"Checking DLLs in {bin_dir}")
    os.chdir(bin_dir)
    # Add bin_dir to DLL search path for this process
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(bin_dir)
    else:
        os.environ['PATH'] = bin_dir + os.pathsep + os.environ['PATH']
    
    dlls = ["libiconv-2.dll", "libintl-9.dll", "libcrypto-3-x64.dll", "libssl-3-x64.dll", "libpq.dll"]
    for dll in dlls:
        try:
            print(f"Trying to load {dll}...", end=" ")
            ctypes.WinDLL(os.path.join(bin_dir, dll))
            print("SUCCESS")
        except Exception as e:
            print(f"FAILED: {e}")

if __name__ == "__main__":
    check_dlls(r"C:\Program Files\PostgreSQL\18\bin")
