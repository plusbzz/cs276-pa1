#!/bin/env python
from collections import deque
import os, glob, os.path
import sys
import re
from itertools import groupby

if len(sys.argv) != 3:
  print >> sys.stderr, 'usage: python index.py data_dir output_dir' 
  os._exit(-1)

total_file_count = 0
root = sys.argv[1]
out_dir = sys.argv[2]
if not os.path.exists(out_dir):
  os.makedirs(out_dir)

# this is the actual posting lists dictionary
# word id -> {position_in_file, doc freq}
posting_dict = {}
# this is a dict holding document name -> doc_id
doc_id_dict = {}
# this is a dict holding word -> word_id
word_dict = {}
# this is a queue holding block names, later used for merging blocks
block_q = deque([])

# function to count number of files in collection
def count_file():
  global total_file_count
  total_file_count += 1

# function for printing a line in a postings list to a given file
# a useful function is f.tell(), which gives you the offset from beginning of file
# you may also want to consider storing the file position and doc frequence in posting_dict in this call
def print_posting(file, posting_line):
  print >> file,posting_line

#########################

'''
Format - one posting per line

term_id:doc_id1,doc_id2...
'''
def print_postings_to_file(term_doc_list, fname):
  with open(fname, 'wb') as f:
    for key,group in groupby(term_doc_list,lambda tup: tup[0]):
      docs = [str(d) for d in sorted(list(set([tup[1] for tup in group])))]
      posting_line = str(key) + ":" + ",".join(docs)
      print >> f, posting_line.strip()
      
      
def variableByteEncodeNumber(aNumber):
    bytes = deque([])
    while True:        
        bytes.appendleft(aNumber % 128)
        if aNumber < 128:
            break
        
        aNumber = aNumber // 128
    
    # Add Continuation Bit = 1
    bytes[-1] += 128    
    return bytes


def variableByteDecodeArray(byteArray):
    numbers = [];
    number  = 0;
    
    for byte in byteArray:
        if byte < 128:
            # Continuation Bit = 0
            number = 128*number + byte
        else:
            # Continuation Bit = 1
            number = 128*number + (byte-128)
            numbers.append(number)
            number = 0
            
    return numbers

def variableByteEncodeNumbers(numbers):
    encodedNumbers = []
    for number in numbers:
        encodedNumbers += variableByteEncodeNumber(number)
    
    return encodedNumbers
  
def generateGaps(docIdList):
    gaps = []
    previous = 0
    for docId in docIdList:
        gaps.append(docId-previous)
        previous = docId
        
    return gaps

def writeVariableByteEncodedGaps(strLine,outputFile,postingDictionary):
    term,docsId = strLine.split(":")
    term   = int(term)
    docsId = sorted([int(d) for d in docsId.strip().split(",")])
    
    position = outputFile.tell()
    postingDictionary[term] = (position,len(docsId))
    
    gaps        = generateGaps(docsId)
    encodedGaps = variableByteEncodeNumbers(gaps)
    
    for number in encodedGaps:
      #print >> sys.stderr, "Writing to file %s the code: %d in byte %d" % (outputfile,number,position)
      # TODO: Find a way to write a block of bytes instead of writing byte per byte 
      outputFile.write(chr(number))        

def writeNaive(strLine,outputFile,postingDictionary):
  print >> outputFile, strLine
  if postingDictionary is not None:
    position = outputFile.tell()
    postingDictionary[term] = (position,len(docsId))
  

def mergeBlocks(b1,b2,outputFile,postingDictionary,writeFunc):
  with open(b1,'r') as b1_f, open(b2,'r') as b2_f, open(outputFile,'wb') as outputFile_f:
    # (provide implementation merging the two blocks of posting lists)
    # write the new merged posting lists block to file 'outputFile_f'
    line1 = b1_f.readline().strip()
    line2 = b2_f.readline().strip()

    while True:     
      if line1 == "" and line2 == "":
        break
      elif line1 == "": # at least one of the files is done
        writeFunc(line2,outputFile_f,postingDictionary)    
        for line in b2_f: writeFunc(line.strip(),outputFile_f,postingDictionary)
        break
    
      elif line2 == "": # at least one of the files is done
        writeFunc(line1,outputFile_f,postingDictionary)    
        for line in b1_f: writeFunc(line.strip(),outputFile_f,postingDictionary)
        break
    
      else:  # files have stuff in them
        term1,docs1 = line1.split(":")
        term2,docs2 = line2.split(":")
        term1 = int(term1)
        term2 = int(term2)
  
        # We now have two sorted lists
        if term1 == term2: 
          docs1 = [int(d) for d in docs1.strip().split(",")]
          docs2 = [int(d) for d in docs2.strip().split(",")]
          docs  = [str(d) for d in sorted(docs1+docs2)]
          
          line = str(term1) + ":" + ",".join(docs)
          writeFunc(line.strip(),outputFile_f,postingDictionary)
          
          line1 = b1_f.readline().strip()
          line2 = b2_f.readline().strip()
          
        elif term1 < term2:
          writeFunc(line1.strip(),outputFile_f,postingDictionary)
          line1 = b1_f.readline().strip()
          
        else:
          writeFunc(line2.strip(),outputFile_f,postingDictionary)
          line2 = b2_f.readline().strip()



#########################

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
  # (you need to provide implementation)
  block_pl_name = out_dir+'/'+dir
  print_postings_to_file(term_doc_list,block_pl_name)

  # append block names to a queue, later used in merging
  block_q.append(block_pl_name)

print >> sys.stderr, '######\nposting list construction finished!\n##########'
print >> sys.stderr, '\nMerging postings...'

dircnt = 1
while len(block_q) > 1:
  b1 = block_q.popleft()
  b2 = block_q.popleft()
  b_comb = '_tmp_'+str(dircnt)
  comb = out_dir + '/'+ b_comb
  dircnt += 1
  
  print >> sys.stderr, 'merging %s and %s into %s' % (b1, b2,b_comb)
  
  if len(block_q) > 0:
    mergeBlocks(b1,b2,comb,None,writeNaive)
  else:
    # These are the last two blocks, generate a compressed/encoded corpus index
    mergeBlocks(b1,b2,comb,posting_dict,writeVariableByteEncodedGaps)
  
  os.remove(b1)
  os.remove(b2)
  block_q.append(comb)
    

# Rename the final merged block to corpus.index    
final_name = block_q.popleft()
os.rename(final_name, out_dir+'/corpus.index')

print >> sys.stderr, '\nPosting Lists Merging DONE!'

# Write to file word and doc dictionary files
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
