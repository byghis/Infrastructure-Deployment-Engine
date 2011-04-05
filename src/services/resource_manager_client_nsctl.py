#!/usr/bin/env python

import sys

# Import the Corba Module
from omniORB import CORBA

# Import the stubs for the CosNaming
import CosNaming

# Import the stubs for the Example module
import ResourceManager

# Initialize the ORB
orb = CORBA.ORB_init( sys.argv, CORBA.ORB_ID )


#Get the IOR of an ResourceManager object from the command line
file = open('ref.ior')
ior = file.read()
file.close

file2 = open('ref2.ior')
ior2 = file2.read()
file2.close

file3 = open('ref3.ior')
ior3 = file3.read()
file3.close

# Convert the IOR to an object reference
obj  = orb.string_to_object(ior)
obj2 = orb.string_to_object(ior2)
obj3 = orb.string_to_object(ior3)

'''
# Obtain a reference to the root naming context
obj         = orb.resolve_initial_references("NameService")
rootContext = obj._narrow(CosNaming.NamingContext)

if rootContext is None:
    print "Failed to narrow the root naming context"
    sys.exit(1)

# Resolve the name "test.my_context/ResourceManger.Instance"
name_instance = [CosNaming.NameComponent("test", "my_context"),
		 CosNaming.NameComponent("ResourceManagerInstance", "Object")]

# Resolve the name "test.my_context/ResourceManger.Image"
name_image = [CosNaming.NameComponent("test", "my_context"),
	      CosNaming.NameComponent("ResourceManagerImage", "Object")]

name_zone = [CosNaming.NameComponent("test", "my_context"),
	     CosNaming.NameComponent("ResourceManagerAvailabilityZone", "Object")]

# 
try:
    instance_obj = rootContext.resolve(name_instance)
    image_obj = rootContext.resolve(name_image)
    zone_obj = rootContext.resolve(name_zone)

except CosNaming.NamingContext.NotFound, ex: 
    print "Name not found"
    sys.exit(1)
'''


# Narrow reference
instance  = obj._narrow(ResourceManager.Instance)
image = obj2._narrow(ResourceManager.Image)
zone = obj3._narrow(ResourceManager.AvailabilityZone)

"""
# Narrow the object to an ResourceManage::Instance
instance = instance_obj._narrow(ResourceManager.Instance)

# Narrow the object to an ResourceManager::Image
image   = image_obj._narrow(ResourceManager.Image)

# Narrow the object to an ResourceManager::AvailabilityZone
zone	= zone_obj._narrow(ResourceManager.AvailabilityZone)

if instance is None:
    print "Object reference is not an ResourceManager::Instance"
    sys.exit(1)

if image is None:
    print "Object reference is not an ResourceManager::Image"
    sys.exit(1)

if zone is None:
    print "Object reference is not an ResourceManager::AvailabilityZone"
    sys.exit(1)
"""

if instance is None:
	print "Object reference is not an ResourceManager::Instance"
	sys.exit(1)

if image is None:
	print "Object Image reference is not an ResourceManager::Image"
	sys.exit(1)

if zone is None:
	print "Object AvailabilityZone reference is not an Resource::AvailabilityZone"


pcpu=ResourceManager.HashObject('cpu','1')
pmem=ResourceManager.HashObject('ram','100')
pdisk=ResourceManager.HashObject('disk','2')
plevel=ResourceManager.HashObject('level','0')
plevelExact=ResourceManager.HashObject('leve','1')
ppercent=ResourceManager.HashObject('percent','0.5')

policies = [pcpu,pmem,pdisk,plevel,ppercent]
policies_new_instance = [pcpu, pmem, pdisk, plevelExact]
lista_void = []

instance_ids = instance.get_instance_ids()
print "instances_ids running: %s" % instance_ids

#instances = iobj.get_instances(1, policies, [])
instances = instance.get_instances(1, lista_void, lista_void)
print "instances: %s" % instances

reservation_ids = instance.get_reservation_ids()
print "reservation_ids: %s" % reservation_ids

reservations = instance.get_reservations()
print "reservations: %s" % reservations

# hard-code
emi_id = "emi-01FD1576"
image_info_from_id = image.get_emi_info(emi_id)
print "The ImageInfo for the image emi-01FD1576 is: %s" % image_info_from_id

zones = zone.get_zones()
print "All Zones are: %s" % zones

typevms = zone.get_typevm_zones()
#print "All typevms are: %s" % typevms

#reservation_info = iobj.run_instances(1,policies)
#print "reservation info (after run_instances call): %s" % reservation_info

#instances_info = iobj.get_instances(1,policies,[])
#print "instance info: %s" % instances_info

#Invoke
#list_reservations = iobj.get_reservations()
#print "reservation list: %s" % list_reservations

#list_reservation_ids = iobj.get_reservation_ids()
#print "list reservations: %s" % list_reservation_ids

