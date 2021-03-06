#!/usr/bin/env python

##-----------------------------------------------------------------------
##
## HLA Tests Suite
##
## Copyright (c) 2006-2008 Eric NOULARD, Jean-Yves ROUSSELOT 
##
## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation; either
## version 2.1 of the License, or (at your option) any later version.
##
## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public
## License along with this library; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##-----------------------------------------------------------------------
#our ouwn way
# if we gonna be again
import logging
import os
import time
import threading
import getopt, sys
import dtest  

def usage():
    print "Usage:\n %s [--help] [--certi_home=<path>] --rtig=[[<user>@]<host>]:<rtig_path> --federate=[[<user>@]<host>]:<federate_path>" % sys.argv[0]

try:
    opts, args = getopt.getopt(sys.argv[1:], "hr:f:c:", ["help","rtig=", "federate=","certi_home="])
except getopt.GetoptError, err:
    print >> sys.stderr, "opt = %s, msg = %s" % (err.opt,err.msg)
    usage()
    sys.exit(2)

## default values
certi_home_defined=False
rtig_param = dtest.Utils.getUserHostPath("rtig")
federate_param = dtest.Utils.getUserHostPath("Interactive_Federate1516")
federate_param['fom']="Interactive_Federation.fed"
    
for o, a in opts:
    if o in ("--help"):
            usage()
            sys.exit(2)
    if o in ("-r", "--rtig"):
        rtig_param   = dtest.Utils.getUserHostPath(a)
    if o in ("-f", "--federate"):
        federate_param = dtest.Utils.getUserHostPath(a)
    if o in ("-c", "--certi_home"):
        certi_home = a
        certi_home_defined=True
        
if not certi_home_defined:
    if os.environ.has_key("CERTI_HOME"):
        certi_home=os.environ["CERTI_HOME"]
    else: 
        print "You must define CERTI_HOME environment variable"
        sys.exit(2)

rtig = dtest.DTester("RTIG",
                     session=dtest.SSHSessionHandler(rtig_param['user'],host=rtig_param['host']))

firstFederate = dtest.DTester("Interactive_First",
                               session=dtest.SSHSessionHandler(federate_param['user'],host=federate_param['host']))

otherFederate = dtest.DTester("Interactive_Second",
                               session=dtest.SSHSessionHandler(federate_param['user'],host=federate_param['host']))

# you may change the default time out value
rtig.timeout = 40
# you add want to save the output of your dtester to a file.
rtig.stdout    = file(rtig.name + ".out",'w+')
rtig.stdin     = file(rtig.name + ".in",'w+')
rtig.stderr    = file(rtig.name + ".err",'w+')

# describe RTIG run steps
rtig.addRunStep("ok",True,"HLA (InteractiveFederate1516) Starts.")
dtest.ReusableSequences.addConditionalRunShellScript(rtig,c_shell_cmd="source "+certi_home+"/share/scripts/myCERTI_env.csh "+rtig_param['host'],
                               bourne_shell_cmd="source "+certi_home+"/share/scripts/myCERTI_env.sh "+rtig_param['host'])
rtig.addRunStep("runCommand",command=rtig_param['path'])
rtig.addRunStep("expectFromCommand",pattern="CERTI RTIG up and running",timeout=5)
rtig.addRunStep("barrier","RTIG started")
rtig.addRunStep("barrier","All Federate(s) ended")
rtig.addRunStep("terminateCommand")
rtig.addRunStep("waitCommandTermination")
rtig.addRunStep("ok",True,"HLA (InteractiveFederate1516) Ends.")

#dtest.DTester.logger.setLevel(level=logging.DEBUG)

# describe first federate run steps
firstFederate.timeout = 35
firstFederate.stdout  = file(firstFederate.name + ".out",'w+')
firstFederate.stdin   = file(firstFederate.name + ".in",'w+')
firstFederate.stderr  = file(firstFederate.name + ".err",'w+')
firstFederate.addRunStep("barrier","RTIG started")
dtest.ReusableSequences.addConditionalRunShellScript(firstFederate,c_shell_cmd="source "+certi_home+"/share/scripts/myCERTI_env.csh "+rtig_param['host'],
                               bourne_shell_cmd="source "+certi_home+"/share/scripts/myCERTI_env.sh "+rtig_param['host'])
firstFederate.addRunStep("runCommand",command=federate_param['path']+" "+firstFederate.name)
firstFederate.addRunStep("expectFromCommand",pattern="Voulez-vous un preambule automatique.*")
firstFederate.addRunStep("ok",firstFederate.getFutureLastStepStatus,"First Federate started and has joined federation")
firstFederate.addRunStep("sendToCommand",string="n\n")
firstFederate.addRunStep("barrier","Wait others...")

#create federation
firstFederate.addRunStep("expectFromCommand",pattern="Choisissez une action :")
firstFederate.addRunStep("ok",firstFederate.getFutureLastStepStatus,"ACTION"+firstFederate.name)
firstFederate.addRunStep("sendToCommand",string="cfe\n")
firstFederate.addRunStep("expectFromCommand",pattern="Federation creee")
firstFederate.addRunStep("ok",firstFederate.getFutureLastStepStatus,firstFederate.name+" has create federation")
firstFederate.addRunStep("barrier","wait creation from first")

#join federation
firstFederate.addRunStep("expectFromCommand",pattern="Choisissez une action :")
firstFederate.addRunStep("ok",firstFederate.getFutureLastStepStatus,"ACTION"+firstFederate.name)
firstFederate.addRunStep("sendToCommand",string="jfe\n")
firstFederate.addRunStep("expectFromCommand",pattern="Federation rejointe")
firstFederate.addRunStep("ok",firstFederate.getFutureLastStepStatus,firstFederate.name+" has join federation")
firstFederate.addRunStep("barrier","Wait others2...")

#resign federation
firstFederate.addRunStep("expectFromCommand",pattern="Choisissez une action :")
firstFederate.addRunStep("ok",firstFederate.getFutureLastStepStatus,"ACTION"+firstFederate.name)
firstFederate.addRunStep("sendToCommand",string="rfe\n")
firstFederate.addRunStep("expectFromCommand",pattern="federation quittee")
firstFederate.addRunStep("ok",firstFederate.getFutureLastStepStatus,firstFederate.name+" has resign federation")
firstFederate.addRunStep("barrier","Wait others3...")

#destroy federation
firstFederate.addRunStep("expectFromCommand",pattern="Choisissez une action :")
firstFederate.addRunStep("ok",firstFederate.getFutureLastStepStatus,"ACTION"+firstFederate.name)
firstFederate.addRunStep("sendToCommand",string="dfe\n")
firstFederate.addRunStep("expectFromCommand",pattern="Federation detruite")
firstFederate.addRunStep("ok",firstFederate.getFutureLastStepStatus,firstFederate.name+" has destroy federation")

firstFederate.addRunStep("sendToCommand",string="q\n")
firstFederate.addRunStep("terminateCommand")
firstFederate.addRunStep("barrier","All Federate(s) ended")

# other federate
otherFederate.timeout = 35
otherFederate.stdout  = file(otherFederate.name + ".out",'w+')
otherFederate.stdin   = file(otherFederate.name + ".in",'w+')
otherFederate.stderr  = file(otherFederate.name + ".err",'w+')
otherFederate.addRunStep("barrier","RTIG started")

dtest.ReusableSequences.addConditionalRunShellScript(otherFederate,c_shell_cmd="source "+certi_home+"/share/scripts/myCERTI_env.csh "+rtig_param['host'],
                               bourne_shell_cmd="source "+certi_home+"/share/scripts/myCERTI_env.sh "+rtig_param['host'])
otherFederate.addRunStep("runCommand",command=federate_param['path']+" "+otherFederate.name)
otherFederate.addRunStep("expectFromCommand",pattern="Voulez-vous un preambule automatique.*")
otherFederate.addRunStep("ok",otherFederate.getFutureLastStepStatus,"Second Federate started and has joined federation")
otherFederate.addRunStep("sendToCommand",string="n\n")
otherFederate.addRunStep("barrier","Wait others...")

#create federation
otherFederate.addRunStep("expectFromCommand",pattern="Choisissez une action :")
otherFederate.addRunStep("ok",otherFederate.getFutureLastStepStatus,"ACTION"+otherFederate.name)
otherFederate.addRunStep("barrier","wait creation from first")
otherFederate.addRunStep("sendToCommand",string="cfe\n")
otherFederate.addRunStep("expectFromCommand",pattern="Federation non creee")
otherFederate.addRunStep("ok",otherFederate.getFutureLastStepStatus,otherFederate.name+" federation already exists")

#join federation
otherFederate.addRunStep("expectFromCommand",pattern="Choisissez une action :")
otherFederate.addRunStep("ok",otherFederate.getFutureLastStepStatus,"ACTION"+otherFederate.name)
otherFederate.addRunStep("sendToCommand",string="jfe\n")
otherFederate.addRunStep("expectFromCommand",pattern="Federation rejointe")
otherFederate.addRunStep("ok",otherFederate.getFutureLastStepStatus,otherFederate.name+" has join federation")
otherFederate.addRunStep("barrier","Wait others2...")

#resign federation
otherFederate.addRunStep("expectFromCommand",pattern="Choisissez une action :")
otherFederate.addRunStep("ok",otherFederate.getFutureLastStepStatus,"ACTION"+otherFederate.name)
otherFederate.addRunStep("sendToCommand",string="rfe\n")
otherFederate.addRunStep("expectFromCommand",pattern="federation quittee")
otherFederate.addRunStep("ok",otherFederate.getFutureLastStepStatus,otherFederate.name+" has resign federation")
otherFederate.addRunStep("barrier","Wait others3...")

#destroy federation
otherFederate.addRunStep("expectFromCommand",pattern="Choisissez une action :")
otherFederate.addRunStep("ok",otherFederate.getFutureLastStepStatus,"ACTION"+otherFederate.name)
otherFederate.addRunStep("sendToCommand",string="dfe\n")
otherFederate.addRunStep("expectFromCommand",pattern="No federation to destroy")
otherFederate.addRunStep("ok",otherFederate.getFutureLastStepStatus,otherFederate.name+" no federation to destroy")

#otherFederate.addRunStep("expectFromCommand",pattern="Choisissez une action :")
#otherFederate.addRunStep("ok",otherFederate.getFutureLastStepStatus,"ACTION"+otherFederate.name)
#otherFederate.addRunStep("sendToCommand",string="ml\n")
#otherFederate.addRunStep("sendToCommand",string="0\n")
#otherFederate.addRunStep("ok",otherFederate.getFutureLastStepStatus,otherFederate.name+" has zero lookahead")

otherFederate.addRunStep("sendToCommand",string="q\n")

otherFederate.addRunStep("terminateCommand")
otherFederate.addRunStep("barrier","All Federate(s) ended")

def goTest():
    myDTestMaster = dtest.DTestMaster("HLA Interactive-1516","Launch RTIG + two interactive federates for testing zero lookahead")
    myDTestMaster.timeout = 50
    myDTestMaster.register(rtig)
    myDTestMaster.register(firstFederate)
    myDTestMaster.register(otherFederate)
    myDTestMaster.startTestSequence()
    myDTestMaster.waitTestSequenceEnd()
    
goTest()

