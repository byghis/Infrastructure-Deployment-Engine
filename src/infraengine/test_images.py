from images import imageInstance

#
# TEST - imageInstance Class
#

image  = imageInstance()

print "Getting all Images registered"
images = image.get_images()
for image in images:
    print "Image: %s" % image