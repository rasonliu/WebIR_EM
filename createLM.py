import sys
import os 
import re
from operator import itemgetter
from math import log10

train_dir = "./20news/Train"
unlabel_dir = "./20news/Unlabel"
test_dir = "./20news/Test"

train_filepaths = []
unlabel_filepaths = []
test_filepaths = []

m_topic_str2idx = {}
m_topic_idx2str = {}

d_topic2count = {}

l_topicWCs = []
alltrain_WC = {}
corpus_WC = {}

is_root = True
for path, subfolds, filenames in os.walk(train_dir):
	if is_root:
		idx = 0
		for subfold in subfolds:
			m_topic_str2idx[subfold] = idx
			m_topic_idx2str[idx] = subfold
			d_topic2count[subfold] = 0
			l_topicWCs.append({})
			idx += 1
		is_root = False

	for f in filenames:
		train_filepaths.append(os.path.join(path, f))

for path, subfolds, filenames in os.walk(unlabel_dir):
	for f in filenames:
		unlabel_filepaths.append(os.path.join(path, f))

for path, subfolds, filenames in os.walk(test_dir):
	for f in filenames:
		test_filepaths.append(os.path.join(path, f))



#do word count on train data
for filepath in train_filepaths:
	topic = filepath.split("/")[-2]
	topicIdx = m_topic_str2idx[topic]
	d_topic2count[topic] += 1

	with open(filepath, 'r') as f:
		lines = f.readlines()
		for line in lines:
			if "@" in line: 
				continue
			if len(line) == 0:
				continue
			
			words = re.sub('[<>/+*^=.:()#,?!;\"\'\\$|_%\-\[\]]', ' ',line).split()
			for word in words:
				#total_count += 1
				low_word = word.lower()
				if not low_word in l_topicWCs[topicIdx]:
					l_topicWCs[topicIdx][low_word] = 1
				else :
					l_topicWCs[topicIdx][low_word] += 1

				if not low_word in alltrain_WC:
					alltrain_WC[low_word] = 1
				else :
					alltrain_WC[low_word] += 1 

				if not low_word in corpus_WC:
					corpus_WC[low_word] = 1 
				else :
					corpus_WC[low_word] += 1


unlabel_count = 0
#do word count on unlabel data
for filepath in unlabel_filepaths:
	unlabel_count += 1
	with open(filepath, 'r') as f:	
		lines = f.readlines()
		for line in lines:
			if "@" in line: 
				continue
			if len(line) == 0:
				continue
			words = re.sub('[<>/+*^=.:()#,?!;\"\'\\$|_%\-\[\]]', ' ',line).split()
			for word in words:
				low_word = word.lower()
				if not low_word in corpus_WC:
					corpus_WC[low_word] = 1
				else :
					corpus_WC[low_word] += 1

#do word count on test data
for filepath in test_filepaths:
	with open(filepath, 'r') as f:
		lines = f.readlines()
		for line in lines:
			if "@" in line: 
				continue
			if len(line) == 0:
				continue
			words = re.sub('[<>/+*^=.:()#,?!;\"\'\\$|_%\-\[\]]', ' ',line).split()
			for word in words:
				low_word = word.lower()
				if not low_word in corpus_WC:
					corpus_WC[low_word] = 1
				else :
					corpus_WC[low_word] += 1



#record topic to count
with open('topicCount', 'w') as outfile:
	for topic, count in d_topic2count.items():
		outfile.write("%s\t%d\n" % (topic, count))


#sort corpus by term-freq
l_sorted_corpus_pair = sorted(corpus_WC.items(), key=itemgetter(1), reverse=True)
l_stop_word = [p[0] for p in l_sorted_corpus_pair[:60]]   #select top-60 as stop word and record it



#find noise word
for word, count in corpus_WC.items():
	if count == 1:
		l_stop_word.append(word)

"""
filename = "stopword"
with open(filename, 'w') as outfile:
	for w in l_stop_word:
		outfile.write("%s\n" % (w))
"""


#remove stop word from word count dict
for w in l_stop_word:
	for LM in l_topicWCs:
		if w in LM:
			LM.pop(w)
	if w in alltrain_WC:
		alltrain_WC.pop(w)
	if w in corpus_WC:
		corpus_WC.pop(w)



topic_total_counts = [sum(wc.values()) for wc in l_topicWCs]
alltrain_total_counts = sum(alltrain_WC.values())
corpus_total_count = sum(corpus_WC.values())


#create inverted-file for unlabel
d_inverted_word2list = {}
for word, count in corpus_WC.items():
	d_inverted_word2list[word] = [0] * (unlabel_count+1)

for filepath in unlabel_filepaths:
	fileIdx = int(filepath.split("/")[-1])
	with open(filepath, 'r') as f:	
		lines = f.readlines()
		for line in lines:
			if "@" in line: 
				continue
			if len(line) == 0:
				continue
			words = re.sub('[<>/+*^=.:()#,?!;\"\'\\$|_%\-\[\]]', ' ',line).split()
			for word in words:
				low_word = word.lower()
				if not low_word in corpus_WC:
					continue
				else :
					d_inverted_word2list[low_word][fileIdx] += 1	




#WC file
idx = 0
for wc in l_topicWCs:
	topicname = m_topic_idx2str[idx]
	filename = topicname+'_WC'

	with open(filename, 'w') as outfile:
		for k ,v in wc.items():
			outfile.write("%s\t%d\n"% (k,v))
	idx += 1

filename = "alltrain_WC"
with open(filename, 'w') as outfile:
	for k, v in alltrain_WC.items():
		outfile.write("%s\t%d\n"% (k,v))

filename = "corpus_WC"
with open(filename, 'w') as outfile:
	for k, v in corpus_WC.items():
		#logv = log10( float(v) / corpus_total_count)
		outfile.write("%s\t%d\n"% (k,v))

filename = "inverted-file"
with open(filename, 'w') as outfile:
	for word,l in d_inverted_word2list.items():
		outfile.write("%s" % word)
		for count in l:
			outfile.write("\t%d" % (count))
		outfile.write("\n")

