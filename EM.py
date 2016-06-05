# -*- coding: UTF-8 -*-
from getModel import *
from math import log10, pow
import re
import sys

d_topic2count = getDict_topic2count()

d_topic_str2idx = {}
d_topic_idx2str = {}

l_topicWCs = []
corpus_WC = {}

l_topicLMs = []
corpusLM = {}

test_filepaths = getList_testpath("./20news/Test")
unlabel_filepaths = getList_unlabel("./20news/Unlabel")

d_inverted = getDict_inverted('inverted-file')
d_unlabelIdx2count = getDict_unlabelIdx2count('unlabel_wordcount')

idx = 0
topics = d_topic2count.keys()
trainDoc_count = sum(d_topic2count.values())
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
miu_rate = 0.05
V = len(corpus_WC)
idx = 0
for topic_wc in l_topicWCs:
	topic_count = topic_total_counts[idx]
	miu = miu_rate * topic_count
	l_topicLMs.append({})
	for word, count in corpus_WC.items():
		if word in topic_wc:
			l_topicLMs[idx][word] = log10((topic_wc[word]+1) / (topic_count + V))
			#l_topicLMs[idx][word] = log10((topic_wc[word] + miu * corpus_WC[word] / corpus_total_count ) / (topic_count + miu))
		else :
			l_topicLMs[idx][word] = log10(1 / (topic_count + V))
			#l_topicLMs[idx][word] = log10((miu * corpus_WC[word] / corpus_total_count ) / (topic_count + miu) )
	idx += 1


iteration = 10
topic_expectation = [0.05]*len(l_topicLMs)
l_emptyFile = []
for i in range(iteration):
	#E-step
	d_fileIdx2probList = {}
	max4normalize = -999999999.0
	for un_file in unlabel_filepaths:
		l_result4topics = [0.0]*len(l_topicLMs)
		filename = un_file.split('/')[-1]
		fileIdx = int(filename)
		
		if fileIdx in l_emptyFile:
			continue
		
		with open(un_file, 'r', encoding="utf-8" ) as f:
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
			
			if sum(l_result4topics) == 0.0:
				l_emptyFile.append(filename)
				continue
			
			for i in range(len(l_result4topics)):
				l_result4topics[i] += log10(topic_expectation[i])
			
			max4normalize = max(l_result4topics)
			for i in range(len(l_result4topics)):
				power = l_result4topics[i] - max4normalize
				if pow < -4:
					l_result4topics[i] = 0
				else:
					l_result4topics[i] = pow(10, power)
			
			sum = sum(l_result4topics)
			for i in range(len(l_result4topics)):
				l_result4topics[i] = l_result4topics[i] / sum
					
			d_fileIdx2probList[fileIdx] = l_result4topics
	
			
	
	
	#M-step
	prob_sum = [0.0] * len(l_topicWCs)
	for fileIdx, probList in d_fileIdx2probList.items():
		for i in range(len(probList)):
			prob_sum[i] += probList[i]
			
	for i in range(topic_expectation):
		topic_expectation[i] = (prob_sum + d_topic2count[d_topic_idx2str[i]]) / (trainDoc_count + len(unlabel_filepaths) - len(l_emptyFile))
	
		#update model
	tfsum4topic =[0.0] * len(l_topicWCs)
	for i, topic_wc in enumerate(l_topicWCs):
		topic_count = topic_total_counts[i]
		#miu = miu_rate * topic_count   
		
		for word, count in corpus_WC.items():
			sum = 0.0
			for fileIdx, probList in d_fileIdx2probList.items():
				sum += probList[i] * d_inverted[word][fileIdx]
	 
			if word in topic_wc:
				sum += topic_wc[word]

			l_topicLMs[i][word] = sum
			tfsum4topic[i] += sum
	
	for i in range(len(l_topicWCs)):
		for word in corpus_WC.keys():
			l_topicLMs[i][word] = log10( (l_topicLMs[i][word] + 1) / (tfsum4topic[i] + 1 * V) ) 
		   
			
	#Testing on test data
	d_docname2result = {}
	for filepath in test_filepaths:
		l_result4topics = [0.0] * len(l_topicLMs)
		filename = filepath.split('/')[-1]
		
		with open(filepath, 'r', encoding="utf-8") as f:
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
				l_result4topics[i] += log10(topic_expectation[i])
			result_idx = l_result4topics.index(max(l_result4topics))
			d_docname2result[filename] = d_topic_idx2str[result_idx]
	
	
	d_docname2ans = getDict_test2ans()
	
	match = 0.0
	for docname, ans in d_docname2ans.items():
		if ans == d_docname2result[docname]:
			match += 1
	
	print("The Accuracy is : ", match/float(len(d_docname2ans)))
	