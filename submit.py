

### The only things you'll have to edit (unless you're porting this script over to a different language) 
### are at the bottom of this file.

import urllib
import urllib2
import hashlib
import random
import email
import email.message
import email.encoders
import StringIO
import sys
from subprocess import Popen
from subprocess import PIPE
from time import time
import os
import glob
import zipfile
import json
import xmlrpclib 
from urllib2 import urlopen
import re
import shutil
import tempfile
import datetime

""""""""""""""""""""
""""""""""""""""""""

class NullDevice:
  def write(self, s):
    pass

def submit():   
  print '==\n== Submitting Solutions \n=='
  
  (login, password) = loginPrompt()
  if not login:
    print '!! Submission Cancelled'
    return
  
  print '\n== Connecting to Coursera ... '

  # Part Identifier
  (partIdx, sid) = partPrompt()

  # Get Challenge
  (login, ch, state, ch_aux) = getChallenge(login, sid) #sid is the "part identifier"
  if((not login) or (not ch) or (not state)):
    # Some error occured, error string in first return element.
    print '\n!! Error: %s\n' % login
    return

  # Attempt Submission with Challenge
  ch_resp = challengeResponse(login, password, ch)
  (result, string) = submitSolution(login, ch_resp, sid, output(partIdx), \
                                  source(partIdx), state, ch_aux)

  print '== %s' % string.strip()


# =========================== LOGIN HELPERS - NO NEED TO CONFIGURE THIS =======================================

def loginPrompt():
  """Prompt the user for login credentials. Returns a tuple (login, password)."""
  (login, password) = basicPrompt()
  return login, password


def basicPrompt():
  """Prompt the user for login credentials. Returns a tuple (login, password)."""
  login = raw_input('Login (Email address): ')
  password = raw_input('One-time Password (from the assignment page. This is NOT your own account\'s password): ')
  return login, password

def partPrompt():
  print 'Hello! These are the assignment parts that you can submit:'
  counter = 0
  for part in partFriendlyNames:
    counter += 1
    print str(counter) + ') ' + partFriendlyNames[counter - 1]
  partIdx = int(raw_input('Please enter which part you want to submit (1-' + str(counter) + '): ')) - 1
  return (partIdx, partIds[partIdx])

def getChallenge(email, sid):
  """Gets the challenge salt from the server. Returns (email,ch,state,ch_aux)."""
  url = challenge_url()
  values = {'email_address' : email, 'assignment_part_sid' : sid, 'response_encoding' : 'delim'}
  data = urllib.urlencode(values)
  req = urllib2.Request(url, data)
  response = urllib2.urlopen(req)
  text = response.read().strip()

  # text is of the form email|ch|signature
  splits = text.split('|')
  if(len(splits) != 9):
    print 'Badly formatted challenge response: %s' % text
    return None
  return (splits[2], splits[4], splits[6], splits[8])

def challengeResponse(email, passwd, challenge):
  sha1 = hashlib.sha1()
  sha1.update("".join([challenge, passwd])) # hash the first elements
  digest = sha1.hexdigest()
  strAnswer = ''
  for i in range(0, len(digest)):
    strAnswer = strAnswer + digest[i]
  return strAnswer 
  
def challenge_url():
  """Returns the challenge url."""
  return "https://stanford.coursera.org/" + URL + "/assignment/challenge"

def submit_url():
  """Returns the submission url."""
  return "https://stanford.coursera.org/" + URL + "/assignment/submit"

def submitSolution(email_address, ch_resp, sid, output, source, state, ch_aux):
  """Submits a solution to the server. Returns (result, string)."""
  #source_64_msg = email.message.Message()
  #source_64_msg.set_payload(source)
  #email.encoders.encode_base64(source_64_msg)

  output_64_msg = email.message.Message()
  output_64_msg.set_payload(output)
  email.encoders.encode_base64(output_64_msg)
  values = { 'assignment_part_sid' : sid, \
             'email_address' : email_address, \
             'submission' : output_64_msg.get_payload(), \
             'submission_aux' : source, \
             'challenge_response' : ch_resp, \
             'state' : state \
           }
  url = submit_url()  
  data = urllib.urlencode(values)
  req = urllib2.Request(url, data)
  response = urllib2.urlopen(req)
  string = response.read().strip()
  result = 0
  return result, string


## This collects the source code (just for logging purposes) 
def source(partIdx):
  if partIdx == 2:
      
      if not os.path.exists("report.pdf"):
          print "No report.pdf file found in the directory. Please make sure it exists (and make sure it's all lowercase letters)."
          sys.exit(1);
          
      p = open("report.pdf","rb").read().encode("base64")
      return p
  
  return ""



############ BEGIN ASSIGNMENT SPECIFIC CODE - YOU'LL HAVE TO EDIT THIS ##############

# Make sure you change this string to the last segment of your class URL.
# For example, if your URL is https://class.coursera.org/pgm-2012-001-staging, set it to "pgm-2012-001-staging".
URL = 'cs276-001'

# the "Identifier" you used when creating the part
partIds = ['pa1_task1','pa1_task2','pa1_task3','pa1_task4']                        
# used to generate readable run-time information for students
partFriendlyNames = ['Task 1 - Uncompressed Index ', 'Task 2 - Variable Length Encoding', 'Task 3 - Report','Extra Credit'] 
# source files to collect (just for our records)
#sourceFiles = ['sampleStudentAnswer.py', 'sampleStudentAnswer.py', 'sampleStudentAnswer.py']                           
          
def readstatsfile(dir, stats):
    
    stats['FILECOUNT'] = ";".join(str(x) for x in open(dir+"/filecount.txt").read().splitlines() if x)
    stats["INDEX SIZE"]= ";".join(str(x) for x in open(dir+"/indexsize.txt").read().splitlines() if not len(x.strip()) == 0)
    stats["INDEX MEMORY OUT"] =";".join(str(x) for x in open(dir+"/index_memory_out").read().splitlines() if x)
    stats["INDEX TIME"] = ";".join(str(x) for x in open(dir+"/indextime.txt").read().splitlines() if x)
    stats["QUERY MEMORY OUT"] = ";".join(str(x) for x in open(dir+"/query_memory_out").read().splitlines() if not len(x.strip()) == 0)
    stats["QUERY TIME"] = ";".join(str(x) for x in open(dir+"/querytime.txt").read().splitlines() if x)
    
def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)
        
def getFiles(tempoutfile):
    pathq = 'http://nlp.stanford.edu/sonalg/queries';
    urlpath = urlopen(pathq+"/index.txt")
    files = urlpath.read().decode('utf-8').splitlines()
    
    ensure_dir(tempoutfile+'/queries');
    if len(files) == 0:
        print 'ASSIGNMENT IS NOT READY FOR THE FINAL SUBMISSION. Please try after April 10th.'
        sys.exit(1);
    
    for filename in files:
        remotefile = urlopen(pathq + "/" + filename)
        localfile = open(tempoutfile+'/queries/'+filename,'w')
        localfile.write(remotefile.read())
        localfile.close()
        remotefile.close()
  
        
def output(partIdx):

  tempoutfile = tempfile.mkdtemp()
  getFiles(tempoutfile)
  outputString = ''
  
  if not os.path.exists("people.txt"):
      print "There is no people.txt file in this directory. Please make people.txt file in this directory with your and your partner's SUNet ID in separate lines (do NOT include @stanford.edu)"
      sys.exit(1)
  
  people = open("people.txt").read().splitlines();
  if len(people) == 0:
      print "people.txt is empty! Write the SUNet ids of you and your partner, if any, in separate lines.."
      sys.exit(1);
  for x in people:
      if len(x) < 3 or len(x) > 8 or ' ' in x.strip() == True:
        print "The SUNet IDs don't seem to be correct. Make sure to remove empty lines. They are supposed to be between 3 and 8 characters. Also, make sure to not include @stanford.edu."
        sys.exit(1);
  peopleStr = "_".join(str(x.strip()) for x in people  if x)

   
  if partIdx == 0:
      print 'Running Task 1 (this might take a while)' 
      if not os.path.isdir('task1'):
          print 'task1 directory does not exist! not submitting!'
          sys.exit(-1);
      else:
        #, stdout = PIPE, stderr = PIPE, shell=True, stdin = PIPE
        
        child = Popen(['./run.sh', 'data', tempoutfile+'/output1', tempoutfile+'/queries','task1/index.sh','task1/query.sh','\n']);
        child.wait()
        if not child.returncode == 0: 
            print 'some error!! not submitting'
            sys.exit(-1);
            
        stats ={};
        readstatsfile(tempoutfile+'/output1',stats);
        for f in glob.glob(tempoutfile+'/output1/query_out/*.*'):
            stats['ZQuery-' + str(os.path.basename(f))]=','.join(str(x) for x in open(f).read().splitlines())
        
        stats['USERIDS']= peopleStr
        stats['TIMESUBMITTED'] = str(datetime.datetime.now());
        outputString = json.dumps(stats);
        
  elif partIdx == 1:     
    print 'Running Task 2 (this might take a while)' 
    if not os.path.isdir('task2'):
          print 'task2 directory does not exist! not submitting!'
          sys.exit(-1);
    child = Popen(['./run.sh', 'data', tempoutfile+'/output2', tempoutfile+'/queries','task2/index.sh','task2/query.sh']);
    child.wait()
    if not child.returncode == 0: 
        print 'some error!! not submitting'
        sys.exit(-1);    
    
    stats ={};
    readstatsfile(tempoutfile+'/output2',stats);
    for f in glob.glob(tempoutfile+'/output2/query_out/*.*'):
        stats["ZQuery-"+str(os.path.basename(f))]=','.join(str(x) for x in open(f).read().splitlines())
    
    stats['USERIDS']= peopleStr
    stats['TIMESUBMITTED'] = str(datetime.datetime.now());
    outputString = json.dumps(stats);

    
  elif partIdx == 2:
    print 'Submitting the report'
    stats ={};
    stats['USERIDS']= peopleStr  
    stats['TIMESUBMITTED'] = str(datetime.datetime.now());
    outputString = json.dumps(stats);
    
  elif partIdx == 3:     
    print 'Running extra credit (this might take a while)'
    if not os.path.isdir('extra_credit'):
          print 'extra_credit directory does not exist! not submitting!'
          sys.exit(-1);
    child = Popen(['./run.sh', 'data', tempoutfile+'/outputextra', tempoutfile+'/queries','extra_credit/index.sh','extra_credit/query.sh']);
    child.wait()
    if not child.returncode == 0: 
        print 'some error!! not submitting'
        sys.exit(-1);
        
    stats ={};
    readstatsfile(tempoutfile+'/outputextra',stats);
    for f in glob.glob(tempoutfile+'/outputextra/query_out/*.*'):
        stats["ZQuery-"+str(os.path.basename(f))]=','.join(str(x) for x in open(f).read().splitlines())
    
    stats['USERIDS']= peopleStr
    stats['TIMESUBMITTED'] = str(datetime.datetime.now());
    outputString = json.dumps(stats);

  return outputString.strip()

def test_python_version():
    """docstring for test_python_version"""
    if sys.version_info < (2,6):
        print >> sys.stderr, "Your python version is too old, please use >= 2.6"
        sys.exit(1)

test_python_version()
submit()
