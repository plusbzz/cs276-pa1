#!/bin/env python
from collections import deque
import os, glob, os.path
import sys
import re

if len(sys.argv) != 2:
  print >> sys.stderr, 'usage: python query.py index_dir' 
  os._exit(-1)

def merge_posting (postings1, postings2):
  new_posting = sorted(list(set(postings1).intersection(set(postings2))))
  return new_posting

# file locate of all the index related files
index_dir = sys.argv[1]
index_f = open(index_dir+'/corpus.index', 'r')
word_dict_f = open(index_dir+'/word.dict', 'r')
doc_dict_f = open(index_dir+'/doc.dict', 'r')
posting_dict_f = open(index_dir+'/posting.dict', 'r')

word_dict = {}
doc_id_dict = {}
file_pos_dict = {}
doc_freq_dict = {}

print >> sys.stderr, 'loading word dict'
for line in word_dict_f.readlines():
  parts = line.split('\t')
  word_dict[parts[0]] = int(parts[1])
print >> sys.stderr, 'loading doc dict'
for line in doc_dict_f.readlines():
  parts = line.split('\t')
  doc_id_dict[int(parts[1])] = parts[0]
print >> sys.stderr, 'loading index'
for line in posting_dict_f.readlines():
  parts = line.split('\t')
  term_id = int(parts[0])
  file_pos = int(parts[1])
  doc_freq = int(parts[2])
  file_pos_dict[term_id] = file_pos
  doc_freq_dict[term_id] = doc_freq


# provide implementation for posting list lookup for a given term
# a useful function to use is index_f.seek(file_pos), which does a disc seek to 
# a position offset 'file_pos' from the beginning of the file

def read_posting(term):
  if term in word_dict:
    term_id = word_dict[term]
    file_pos = file_pos_dict[term_id]
    index_f.seek(file_pos)
    word_id,docs = index_f.readline().strip().split(':')
    posting_list = [int(d) for d in docs.split(',')]
    doc_freq = doc_freq_dict[term_id]
    return (doc_freq,posting_list)
  else:
    return None

# read query from stdin
while True:
  input = sys.stdin.readline()
  input = input.strip()
  if len(input) == 0: # end of file reached
    break
  input_parts = input.split()
  # you need to translate words into word_ids
  # don't forget to handle the case where query contains unseen words
  no_results = False
  postings = []
  for term in input_parts:    
    posting = read_posting(term)
    
    # Account for unseen words
    if posting is None:
      no_results = True
      break
    
    postings.append(posting)

  if no_results:
    print "no results found"
    continue
  
    
  # Sort postings by size increasing order
  postings.sort(key=lambda tup: tup[0])
  postings = [p[1] for p in postings]
  
  # merge the posting lists to produce the final result
  result = reduce(merge_posting,postings)
  

  # don't forget to convert doc_id back to doc_name, and sort in lexicographical order
  # before printing out to stdout
  docs = sorted([doc_id_dict[doc_id] for doc_id in result])
  for doc in docs: print doc  
