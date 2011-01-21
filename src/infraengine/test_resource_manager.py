import time
from resource_manager import ResourceManager

#
# Resources required
#
resourcesA =  {'typevm':"m1.small"}
resourcesB =  { 'cpu':1, 'ram':128, 'disk':2, 'level':1 }
resourcesC =  { 'cpu':1, 'ram':256, 'disk':5, 'level':1 }
resourcesD =  {'cpu':1, 'ram':200, 'disk':4.5, 'level':0, 'percent':0.5}

resources = [ resourcesA, resourcesB, resourcesC, resourcesD ]
infra_deploy = ResourceManager()

#
# Getting Instances
#
instances, instances_ok, reservations = infra_deploy.get_instances(resources)
print "Instances(engine): %s" % instances
print "Num Instances to verify: %s" % instances_ok
print "New Instances(engine): %s" % reservations

#
# Rebooting Instances
#
print "\nGettint instances ids"
instances_ids = []
for instance in instances:
    instances_ids.append( instance[0].id.encode("latin-1") )

print "Instances Ids to Reboot: %s" % instances_ids
reboot_instances = infra_deploy.reboot_instances( instances_ids )
print "Instances Rebooting: %s" % reboot_instances

#
# Logging Instances
#
print "\nGettint instances ips"
instances_ips = []
for instance in instances:
    instances_ips.append( instance[0].public_dns_name.encode("latin-1") )

print "Instances Ips to Logging: %s" % instances_ips
logging_consoles = infra_deploy.show_instances( instances_ips )
print "Instances Rebooting: %s" % logging_consoles