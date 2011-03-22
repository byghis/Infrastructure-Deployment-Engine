from instance import nodeInstance
import inspect
#
# Test - nodeInstance Class
#
engine = nodeInstance()

#
# Getting information about Reservations
#

print "Getting all Reservations"
reservations = engine.get_reservations()
print "reservation's members:"
print inspect.getmembers(reservations)
for reservation in reservations:
    print "Reservation ID is: %s"  % reservation.id

print "\nGet Random Instances 1"
instances, num_instances = engine.get_instances()
for instance in instances:
    print "Instance id: %s" % instance.id
print "Number of instances to verify: %d" % num_instances