#!/usr/bin/env python

import sys
from omniORB import CORBA

# Import the stubs for the Example module
import ResourceManager

# Initialize the ORB
orb = CORBA.ORB_init( sys.argv, CORBA.ORB_ID )

# Get the IOR of an ResourceManager object from the command line
file = open('ref.ior')
ior = file.read()
file.close

# Convert the IOR to an object reference
obj = orb.string_to_object(ior)

# Narrow reference
iobj = obj._narrow(ResourceManager.Instance)

if iobj is None:
	print "Object reference is not an ResourceManager::Instance"
	sys.exit(1)

pcpu=ResourceManager.HashObject('cpu','1')
pmem=ResourceManager.HashObject('ram','128')
pdisk=ResourceManager.HashObject('disk','2')
plevel=ResourceManager.HashObject('level','0')
plevelExact=ResourceManager.HashObject('leve','1')
ppercent=ResourceManager.HashObject('percent','0.5')

policies = [pcpu,pmem,pdisk,plevel,ppercent]
policies_new_instance = [pcpu, pmem, pdisk, plevelExact]

reservation_info = iobj.run_instances(1,policies)
print "reservation info (after run_instances call): %s" % reservation_info

instances_info = iobj.get_instances(1,policies,[])
print "instance info: %s" % instances_info

#Invoke
list_reservations = iobj.get_reservations()
print "reservation list: %s" % list_reservations

list_reservation_ids = iobj.get_reservation_ids()
print "list reservations: %s" % list_reservation_ids

