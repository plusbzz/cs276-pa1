#!/bin/env python
from collections import deque
import os, glob, os.path
import sys
import re

if len(sys.argv) != 3:
  print >> sys.stderr, 'usage: python index.py data_dir output_dir' 
  os._exit(-1)

total_file_count = 0
root = sys.argv[1]
out_dir = sys.argv[2]
if not os.path.exists(out_dir):
  os.makedirs(out_dir)

# this is the actual posting lists dictionary
posting_dict = {}
# this is a dict holding document name -> doc_id
doc_id_dict = {}
# this is a dict holding word -> word_id
word_dict = {}
# this is a queue holding block names, later used for merging blocks
block_q = deque([])

# function to count number of files in collection
def count_file():
  print >> sys.stderr, 'you must provide implementation'

# function for printing a line in a postings list to a given file
def print_posting(file, posting_line):
  # a useful function is f.tell(), which gives you the offset from beginning of file
  # you may also want to consider storing the file position and doc frequence in posting_dict in this call
  print >> sys.stderr, 'you must provide implementation'
  
# function for merging two lines of postings list to create a new line of merged results
def merge_posting (line1, line2):
  # don't forget to return the resulting line at the end
  print >> sys.stderr, 'you must provide implementation'
  return None


doc_id = -1
word_id = 0

for dir in sorted(os.listdir(root)):
  print >> sys.stderr, 'processing dir: ' + dir
  dir_name = os.path.join(root, dir) 
  term_doc_list = []
  
  for f in sorted(os.listdir(dir_name)):
    count_file()
    
    # Add 'dir/filename' to doc id dictionary
    file_name = os.path.join(dir, f)
    doc_id += 1
    doc_id_dict[file_name] = doc_id
    fullpath = os.path.join(dir_name, f)
    
    with open(fullpath, 'r') as infile:
      for line in infile.readlines():
        tokens = line.strip().split()
        for token in tokens:
          if token not in word_dict:
            word_dict[token] = word_id
            word_id += 1
          term_doc_list.append( (word_dict[token], doc_id) )
  
  # sort term doc list
  print >> sys.stderr, 'sorting term doc list for dir:' + dir
  term_doc_list.sort(key=lambda tup: tup[0])  # sorts in place
  
  
  # write the posting lists to block_pl for this current block 
  print >> sys.stderr, 'print posting list to disc for dir:' + dir
  block_pl_name = out_dir+'/'+dir
  with open(block_pl_name, 'wb') as block_pl:
    pass

  # append block names to a queue, later used in merging
  block_q.append(block_pl_name)

print >> sys.stderr, '######\nposting list construction finished!\n##########'

print >> sys.stderr, '\nMerging postings...'
dircnt = 1
while len(block_q) > 1:
  b1 = block_q.popleft()
  b2 = block_q.popleft()
  comb = out_dir + '/'+ str(dircnt)
  dircnt += 1
  
  print >> sys.stderr, 'merging %s and %s' % (b1, b2)
  
  with open(b1,'r') as b1_f, open(b2,'r') as b2_f, open(comb,'r') as comb_f:
    # (provide implementation merging the two blocks of posting lists)
    # write the new merged posting lists block to file 'comb_f'
    pass
  

  os.remove(b1)
  os.remove(b2)
  block_q.append(comb)
    
print >> sys.stderr, '\nPosting Lists Merging DONE!'

# rename the final merged block to corpus.index
final_name = block_q.popleft()
os.rename(out_dir+'/'+final_name, out_dir+'/corpus.index')

# print all the dictionary files
doc_dict_f = open(out_dir + '/doc.dict', 'w')
word_dict_f = open(out_dir + '/word.dict', 'w')
posting_dict_f = open(out_dir + '/posting.dict', 'w')
print >> doc_dict_f, '\n'.join( ['%s\t%d' % (k,v) for (k,v) in sorted(doc_id_dict.iteritems(), key=lambda(k,v):v)])
print >> word_dict_f, '\n'.join( ['%s\t%d' % (k,v) for (k,v) in sorted(word_dict.iteritems(), key=lambda(k,v):v)])
print >> posting_dict_f, '\n'.join(['%s\t%s' % (k,'\t'.join([str(elm) for elm in v])) for (k,v) in sorted(posting_dict.iteritems(), key=lambda(k,v):v)])
doc_dict_f.close()
word_dict_f.close()
posting_dict_f.close()

print total_file_count
