from getModel import *
from math import log10
import re
import sys

d_topic2count = getDict_topic2count()

d_topic_str2idx = {}
d_topic_idx2str = {}

l_topicWCs = []
corpus_WC = {}

l_topicLMs = []
corpusLM ={}
#l_stopword = getList_stopword()

test_filepaths = getList_testpath("./20news/Test")

idx = 0
topics = d_topic2count.keys()
doc_count = sum(d_topic2count.values())
for topic in topics:
	d_topic_str2idx[topic] = idx
	d_topic_idx2str[idx] = topic
	l_topicWCs.append(getWC(topic))
	idx += 1

corpus_WC = getCorpusWC("corpus")


topic_total_counts = [sum(wc.values()) for wc in l_topicWCs]
corpus_total_count = sum(corpus_WC.values())


#smooth

#miu_rate = float(sys.argv[1]) / 100.0
miu_rate = 0.75

V = len(corpus_WC)
idx = 0
for topic_wc in l_topicWCs:
	topic_count = topic_total_counts[idx]
	miu = miu_rate * topic_count
	l_topicLMs.append({})
	for word, count in corpus_WC.items():
		if word in topic_wc:
			#l_topicLMs[idx][word] = log10((topic_wc[word]+1) / (topic_count + V))
			l_topicLMs[idx][word] = log10((topic_wc[word] + miu * corpus_WC[word] / corpus_total_count ) / (topic_count + miu))
		else :
			#l_topicLMs[idx][word] = log10(1 / (topic_count + V))
			l_topicLMs[idx][word] = log10((miu * corpus_WC[word] / corpus_total_count ) / (topic_count + miu) )
	idx += 1





##start test
d_docname2result = {}
for filepath in test_filepaths:
	l_result4topics = [0.0] * len(l_topicLMs)
	filename = filepath.split('/')[-1]
	
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
				if not low_word in l_topicLMs[0]:
					continue
				for i, LM in enumerate(l_topicLMs):
					l_result4topics[i] += LM[low_word]
		for i, LM in enumerate(l_topicLMs):
			l_result4topics[i] += log10(float(d_topic2count[d_topic_idx2str[i]])/float(doc_count))
		result_idx = l_result4topics.index(max(l_result4topics))
		d_docname2result[filename] = d_topic_idx2str[result_idx]


d_docname2ans = getDict_test2ans()

match = 0.0
for docname, ans in d_docname2ans.items():
	if ans == d_docname2result[docname]:
		match += 1

print "The Accuracy is : ", match/float(len(d_docname2ans))
#print "For miu.rate=", sys.argv[1], ", The Accuracy is : ", match/float(len(d_docname2ans))




