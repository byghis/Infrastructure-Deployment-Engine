from instance import nodeInstance

#
# Test - nodeInstance Class
#
engine = nodeInstance()

#
# Getting information about Reservations
#

print "Getting all Reservations"
reservations = engine.get_reservations()
for reservation in reservations:
    print "Reservation ID is: %s"  % reservation.id

print "\nGeting Reservations Ids"
reservations_ids = engine.get_reservations_ids()
print "The Reservations Ids are: %s" % reservations_ids

print "\nGeting Reservations Ids from Instances Ids"
instance_ids = ['i-39F606CC'] # update values
reservations_ids = engine.get_reservations_ids( instance_ids )
print "The Reservations Ids are from instances_ids: %s" % reservations_ids

#
# Getting Instances
#

print "\nGet all Instances"
instances,_ = engine.get_all_instances()
for instance in instances:
    print "Instance Id is: %s" % instance.id

print "\nGet all Instances ids"
instances_ids = engine.get_instances_ids()
print "The Instances Ids are: %s" % instances_ids

print "\nGet Random Instances 1"
instances, num_instances = engine.get_instances(1)
for instance in instances:
    print "Instance id: %s" % instance.id
print "Number of instances to verify: %d" % num_instances

print "\nGet Random Instances 2 "
instances, num_instances = engine.get_instances(2)
for instance in instances:
    print "Instance id: %s and Instance launch_time: %s" % (instance.id, instance.launch_time)
print "Number of instances to verify: %d" % num_instances

# Example of num_instances use
if num_instances > 0:
    print "Other instances available: %d" % num_instances
elif num_instances == 0:
    print "Don't exist more instances"
else:
    print "Is necesary run %s machines" % num_instances

print "\nGet Instances from List of Ids"
instances_ids = engine.get_instances_ids()
instances, instances_ok = engine.get_instances(3, None, instances_ids)
for instance in instances:
    print "Instance id: %s and Instance launch_time: %s" % (instance.id, instance.launch_time)
print "Number of instances to verify: %d" % instances_ok

#
# Getting Instances according policies 1
# policies (typevm) inside a simple list
#
policy_typevm = {'typevm':'m1.small'}
print "\nGet Instances with typevm policies"
instances_policies, instance_ok = engine.get_instances(1, policy_typevm)
print "Instances with Typevm Policies: %s" % instances_policies
print "Number of instances to verify: %d" % instance_ok

#
# Getting Instances according policies 2
# Resoyrce Types: level 1: exactly or level 0: adapte
#
policies_resources  = {'cpu':1, 'ram':128, 'disk':2, 'level':1}
'''
policies_resources = {'cpu':1, 'ram':100, 'disk':1.5, 'level':0, 'percent':0.5}
policies_resources = {'cpu':4, 'ram':400, 'disk':15, 'level':0, 'percent':0.5}
'''

print "\nGet Instances with Adaptive Resource Policies"
instances_policies, instance_ok = engine.get_instances(1, policies_resources)
print "Instances with Adaptive Resource Policies: %s" % instances_policies
print "Number of instances to verify: %d" % instance_ok

#
# Executing instances
# VM Types: m1.small, c1.medium, m1.large', m1.xlarge, c1.xlarge
# Resoyrce Types: level 1: exactly or level 0: adapte
#

print "\nNumber of running instances: %d" % engine.get_num_instances()

#
# Running Instances without policies (default instances m1.small)
#
'''
reservation = engine.run_instances(2)
print "Reservation(new instance): %s" % reservation
'''

#
# Running Instances
# Policies is a simple string of typevm or image_id
#
'''
reservation = engine.run_instances(1, "emi-022E157BA") # default m1.small
print "Reservation(new instance): %s" % reservation

reservation = engine.run_instances(1, "m1.small")      # default random image_id
print "Reservation(new instance): %s" % reservation
'''

#
# Running Instances
# Policies: Instance requirements in a list
# level 1 (exact requirements) or level 0 (adapt requirements)
#
'''
policies_instance_adaptive  = {'cpu':1, 'ram':128, 'disk':2, 'level':1}
reservation = engine.run_instances(1, policies_instance_adaptive)
print "Reservation(new instance): %s" % reservation

policies_instance_adaptive = {'cpu':1, 'ram':100, 'disk':1.5, 'level':0, 'percent':0.5}
reservation = engine.run_instances(1, policies_instance_adaptive)
print "Reservation(new instance): %s" % reservation

policies_instance_adaptive = {'cpu':4, 'ram':400, 'disk':105, 'level':0, 'percent':0.5}
reservation = engine.run_instances(1, policies_instance_adaptive)
print "Reservation(new instance): %s" % reservation
'''

#
# Reboot Instances
#
'''
instance_id_list = engine.get_instances_ids()
engine.reboot_instances(instance_id_list)
'''

#
# Terminate Instance
#
'''
instances_ids_poweroff = engine.get_instances_ids()
#instances_ids_poweroff = ['i-39F606CC']
print "Instances ids: %s" % instances_ids_poweroff
instances_ids = engine.terminate_instance(instances_ids_poweroff)
print "Instances to poweroff: %s" % instances_ids
'''

#
# Show a Console accesing to Virtual Machine
#

#instances_ips = ['139.82.2.154']
instances_ips = engine.get_ips_instances(1)
engine.show_console(instances_ips)


#
# Get ids from instances
#
print "\nGet Instances Id from instances"
instances,_ = engine.get_all_instances()
instances_ids = engine.get_ids(instances)
for instance_id in instances_ids:
    print "Instance Id is: %s" % instance_id

#
# Get ips from instances
#
print "\nGet Instances Id from instances"
instances,_ = engine.get_all_instances()
instances_ips = engine.get_ips(instances)
for instance_ip in instances_ips:
    print "Instance Ip is: %s" % instance_ip
