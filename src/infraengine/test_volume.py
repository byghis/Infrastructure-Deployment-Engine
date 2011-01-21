from volume import volumeStorage

#
# TEST -- Volume Storage Class
#
volume = volumeStorage()

print "\nCreating a New Volume"
volumes = volume.create_volume(1, 'clusterpituba')
print "Volumen(new volumen): %s" % volumes

print "\nGetting all Volumes"
volumes = volume.get_volumes()
print "Volumes are: %s" % volumes

print "\nDelete all Volumes"
volumes_deleted, volumes_ok = volume.delete_volumes()
print "Delete all volumes: %s" % volumes_deleted
print "The volumes deleted(true or false): %s" % volumes_ok

'''
volume_ids = volume.get_volumes_ids()
print "\nDelete Volumes from Volume Ids:%s " volume_ids

volumes_deleted, volumes_ok = volume.delete_volumes(volume_ids)
print "Delete volumes: %s" % volumes_deleted
print "The volumes deleted(true or false): %s" % volumes_ok
'''
