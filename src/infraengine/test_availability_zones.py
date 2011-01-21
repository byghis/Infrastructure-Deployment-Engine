from availability_zones import availabilityZones

#
# TEST - availabilityZones Class
#

zones  = availabilityZones()

print "Getting Zones"
cluster = zones.get_zones()
for instance in cluster:
    cluster_string = '%s %s' % (instance.name, instance.state)
    print "Cluster: %s" % cluster_string

print "\nGetting Detailed Zones"
cluster = zones.get_zones_detailed()
for instance in cluster:
    cluster_string = '%s %s' % (instance.name, instance.state)
    print "Cluster: %s" % cluster_string

#Move to InfraDeployment
print "\nGetting List Detailed Zones"
clusters_details = zones.get_typevm_zones()
print "Detailed Zones: %s" % clusters_details