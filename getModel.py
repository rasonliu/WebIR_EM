import os

def getList_unlabeled(unlabel_dir):
	l = []
	for path, subfolds, filenames in os.walk(unlabel_dir):
		for f in filenames:
			l.append(os.path.join(path, f))
	return l

def getList_testpath(test_dir):
	l = []
	for path, subfolds, filenames in os.walk(test_dir):
		for f in filenames:
			l.append(os.path.join(path, f))
	return l

def getDict_topic2count():
	d = {}
	with open("topicCount", 'r') as f:
		lines = f.readlines()
		for line in lines:
			parseLine = line.strip().split()
			d[parseLine[0]] = int(parseLine[1])
	return d

def getWC(topicname):
	d = {}
	filename = topicname + "_WC"
	with open(filename, 'r') as f:
		lines = f.readlines()
		for line in lines:
			parseLine = line.strip().split()
			d[parseLine[0]] = float(parseLine[1])
	return d

def getCorpusWC(path):
	d = {}
	filename = path + "_WC"
	with open(filename, 'r') as f:
		lines = f.readlines()
		for line in lines:
			parseLine = line.strip().split()
			d[parseLine[0]] = float(parseLine[1])
	return d

"""
def getList_stopword():
	l = []
	with open("stopword", 'r') as f:
		lines = f.readlines()
		for line in lines:
			l.append(line.strip())
	return l
"""

def getDict_test2ans():
	d = {}
	with open("ans.test", "r") as f:
		lines = f.readlines()
		for line in lines:
			parseLine = line.strip().split()
			d[parseLine[0]] = parseLine[1]
	return d
