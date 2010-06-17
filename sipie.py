#!/usr/bin/env python
# Eli Criffield

import os
import sys
import getopt
import Sipie

def usage():
   pname = os.path.basename(sys.argv[0])
   print "Usage: " + pname + " [STATION]\n"
   print "\t\te.g " + pname + " 'E Street Radio'\n" 

try:
   opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help"])
except getopt.GetoptError, err:
   print str(err)
   print "Use --help for command line information"
   sys.exit(2)

for o, a in opts:
   if o in ("-h", "--help"):
      usage()
      sys.exit()        


player = Sipie.cliPlayer()
try:
    os.environ['DISPLAY']
except:
   Sipie.cliPlayer()
   sys.exit(0)

try:
    player()
except:
   try:	
      Sipie.gtkPlayer()
   except: 
      if player is not Sipie.cliPlayer:
         Sipie.cliPlayer()

	


