import sys, os, time
import logging, logging.config
import ResourceManager, ResourceManager__POA

from instance import nodeInstance
from images import imageInstance
from availability_zones import availabilityZones
from omniORB import CORBA, PortableServer

import CosNaming

logging.config.fileConfig('logging.conf')

# Create a Logger
logger = logging.getLogger('deployLog')

class Instance_i(ResourceManager__POA.Instance):

	def __init__(self):
		self.engine = nodeInstance()
		self.image  = imageInstance()
		#self.reservations    = []
		#self.instances       = []
	
	'''
	@deprecated
	'''
	def get_reservations_d(self):
		"""Get Reservations Ids
	
		@type variable_name: string
		@param variable_name: description (example: Your AWS Access Key ID)
	
		@rtype: type returned (example: L{SQSConnection<boto.sqs.connection.SQSConnection>})
		@return: description (example: A connection to Amazon's SQS

		"""
		reservations = self.engine.get_reservations()
		logger.debug("type(reservations): %s", type(reservations))
		logger.debug("reservations: %s",  reservations)
		return "HelloWorld"

	def get_instance_ids(self):
		"""Return a list of Instance IDs

		@rtype: list
		@return: A list of Instances IDs

		"""
		logger.info("In get_instance_ids()")
		instance_ids = self.engine.get_instances_ids()
		logger.debug("instance_ids(get_instances_ids): %s", instance_ids)
		return instance_ids

	def get_num_instances(self):
		"""Get the number of instances
		"""
		logger.debug("number of instances: %s", self.engine.get_num_instances())
		return self.engine.get_num_instances()
	

	def __get_multi_instance_data(self, instance):
		"""Return a InstanceData
	
		@type instance:  <class 'boto.ec2.instance.Instance'> 
		@param instance: An Instance Object

		@rtype: InstanceData
		@return: A set of data from an Instance

		"""
		logger.info("In __get_multi_instance_data(instance)")
		logger.debug("Type of instance object: %s", type(instance))
		instance_data = ResourceManager.InstanceData(	instance.image_id.encode('latin-1'),
								instance.public_dns_name.encode('latin-1'),
								instance.private_dns_name.encode('latin-1'),
								instance.state.encode('latin-1'),
								instance.key_name.encode('latin-1'),
								instance.ami_launch_index.encode('latin-1'),
								'None', #instance.product_codes.encode('latin-1'),
								instance.instance_type.encode('latin-1'),
								instance.launch_time.encode('latin-1'),
								instance.placement.encode('latin-1'),
								instance.kernel.encode('latin-1'),
								instance.ramdisk.encode('latin-1') )
		
		logger.debug("Returning a new instance_data: %s", instance_data)
		return instance_data
	
	def __get_instance_info(self, instance):
		"""Return an InstanceInfo
	
		@type instance:  <class 'boto.ec2.instance.Instance'>
		@param instance: An Instance Object
		
		@rtype: InstanceInfo
		@return: InstanceInfo containing a instance id and InstanceData
		
		"""
		logger.info("In __get_instance_info()")
		logger.debug("instance_id(__get_instance_info): %s",instance.id)
		instance_data = self.__get_multi_instance_data(instance)
		instance_info = ResourceManager.InstanceInfo( instance.id.encode('latin-1'), instance_data )
		logger.debug("instance_info(__get_instance_info): %s", instance_info)
		return instance_info

	def __get_instances_info(self, instances):
		"""Return a list of InstanceInfo
	
		@type instances: <class 'boto.resultset.ResultSet'>
		@param instances: 

		@rtype: InstanceInfoSeq
		@return: A list of InstanceInfo 

		"""
		logger.info("In __get_instances_info(instances)")
		logger.debug("Instances are: %s", instances)
		logger.debug("Type of instances: %s", type(instances))
		instances_info=[]
		for instance in instances:
			logger.debug("A instance to retrieve info: %s", instance)
			instances_info.append( self.__get_instance_info(instance) )
		return instances_info
		
	def __hashtable_to_dictionary(self, hashtable):
		"""Convert a hashtable to hashmap
		
		@type hashtable: HashObjectSeq 
		@param hashtable: A list of HashObjects

		@rtype: list
		@return: A list of policies(dictionary)

		"""
		logger.info("In __hashtable_to_dictionary()")
		policies = {}
		logger.debug("hashtable(__hashtable_to_dictionary): %s", hashtable)
		if hashtable is not None: 
			for ht in hashtable:
				# FIXME: weird coersion to guess the value's type
				# dynamically, because Euca2ools will raise errors if
				# the hashmap passed doesn't have the proper value type
				try:
					validCoersion = int(ht.value)
					ht.value = validCoersion 
				except ValueError:
					try:
						validCoersion = float(ht.value)
						ht.value = validCoersion
					except ValueError:
						pass
				policies[ht.name] = ht.value
		
		logger.debug("policies: %s", policies)
		return policies

	def __check_policies(self, policies):
		"""
		"""
		if policies is None:
			logger.debug("Not policies included: %s", type(policies))
			return False
		return True

	def get_instances(self, num_instances, policies, instance_ids):
		"""Get Instances
		get_instances() provide a way to retrieve vm instances data running
		on the local cloud. This function allows you to specify a number of
		instances, policies, and a list of instances_ids to reduce the search
		space. At least is needed to specify some number of instances and will be
		returned a random instance list because wasn't specified any policie.
		To return vm instances according differents vm requirements (cpu, ram,
		disk, platform, network type, security options, etc) is necessary to pass
		a list of requirements(dictionary key, value). Finally is possible reduce
		the search space for restrict the pool of instances.

		@type number_instances: string
		@param number_instances: Number of instances
		
		@type policies: HashObjectSeq
		@param policies: A list of HashObjects
		
		@type instance_ids: list
		@param instance_ids: A list of instance IDs

		@rtype InstanceInfoSeq (list)
		@return A list of InstanceInfo

		"""
		logger.info("In get_instances()")
		logger.debug("num_instances: %s", num_instances)
		logger.debug("policies: %s", policies)
		logger.debug("instance_ids: %s", instance_ids)
				
		if not self.__check_policies(policies):
			instance_policies = {}
		instance_policies = self.__hashtable_to_dictionary(policies)
		
		logger.info("Getting instances list and num of instances for SLA")
		instances, num_instances = self.engine.get_instances(num_instances, instance_policies, instance_ids)
		#Type of instances elements: <class 'boto.ec2.instance.Instance'>

		return self.__get_instances_info( instances )
	
	def get_instances_sla(self, num_instances, policies, instance_ids):
		"""
		"""
		logger.info("In get_instances_sla()")
		instances, num_ideficit = self.engine.get_instances(num_instances, instance_policies, instance_ids)
		instance_sla = ResourceManager.InstanceInfoSLA(	num_ideficit,
								"default",
								self.__get_instances_info(instances))
		return instances_sla
		
	def __get_multi_reservation_data(self, reservation):
		"""Get a ReservationData
		
		@type reservation: <class 'boto.ec2.instance.Reservation'> 
		@param reservation:
		
		@rtype ReservationData, list
		@return a ReservationData, and a list of instance_ids (reservation.instances)
		
		"""
		logger.info("In __get_multi_reservation_data()")
		logger.debug("reservation: %s", reservation)
		logger.debug("instances included in reservation: %s", reservation.instances)
		
		reservation_data = ResourceManager.ReservationData(	reservation.owner_id.encode('latin-1'),
									reservation.groups[0].id.encode('latin-1') )
		logger.debug("reservation_data: %s", reservation_data)
		
		reservation_instances_ids=[]
		for instance in reservation.instances:
			logger.debug("instance(__get_multi_reservation_data):%s", instance.id)
			reservation_instances_ids.append(instance.id.encode('latin-1'))
		logger.debug("reservation_instances_ids: %s", reservation_instances_ids)	
		return reservation_data, reservation_instances_ids
			

	def __get_reservation_info(self, reservation_id):
		"""Get a ReservationInfo from reservation_id
	
		@type reservation_id: string
		@param reservation_id: A reservation ID

		@rtype ReservationInfo
		@return A ReservationInfo
		
		"""
		logger.info("In __get_reservation_info")
		#reservation = None
		reservations = self.engine.get_reservations()
		found=False
		for reservation in reservations:
			if reservation.id == reservation_id:
				found=True
				break
		if not found:
			#TODO: raise a ReservationFailed CORBA exception
			sys.exit(1)
		
		#reservation = self.engine.get_reservation(reservation_id) #version ResourceEngine 1.1 
		reservation_data, reservation_instances_ids = self.__get_multi_reservation_data( reservation )
		reservation_info = ResourceManager.ReservationInfo(	reservation_id.encode('latin-1'), 
									reservation_data,
									self.__get_instances_info(reservation.instances))
		logger.debug("Reservations Info: %s", reservation_info)
		return reservation_info

	def __get_reservations_info(self, reservation_ids):
		"""Get a list of ReservationInfo from reservation_ids
		
		@type reservation_ids: list
		@param reservation_ids: A list of reservation_ids
		
		@rtype ReservationInfoSeq
		@return A list of ReservationInfo	
	
		"""
		logger.info("In __get_reservations_info")
		reservations_info=[]
		for reservation_id in reservation_ids:
			logger.debug("reservation_id(__get_reservations_info):%s", reservation_id)
			reservations_info.append( self.__get_reservation_info(reservation_id) )
		return reservations_info
	
	def get_reservations(self):
		"""Get Reservations
		Note
		reservations = self.engine.get_reservations(), where
		reservations is a instancia of  <class 'boto.resultset.ResultSet'>, and
		a resultset is a list of <class 'boto.ec2.instance.Reservation'>
	
		@rtype: list
		@return: A list of ReservationInfo

		"""
		logger.info("In get_reservations()")
		reservation_ids = self.engine.get_reservations_ids()
		logger.debug("reservations_ids: %s", reservation_ids)	

		return self.__get_reservations_info( reservation_ids )	
	
	#TODO
	def __get_reservation(self, reservation_id):
		"""Get the Reservation Object
		"""
		logger.info("Getting the reservation object from reservation.id")
		return "In __get_reservations"
	
	#TODO
	def __get_instances(self, reservation_id):
		"""Get the Instances Objects
		"""
		logger.info("Getting the instances objects from reservation.id")
		reservations = self.__get_reservations( reservation.id )
		# return __get_reservation( reservation.id ).instances
		return "In __get_instances"


	def get_reservation_ids(self):
		"""Get Reservations IDs
	
		@rtype: list
		@return: A list of Reservations IDs

		"""
		logger.info("In get_reservation_ids()")
		reserv = self.engine.get_reservations()
		logger.debug("reservations(get_reservations): %s",  reserv)
		logger.debug("type(reservations): %s", type(reserv))
		logger.debug("type(reservations[0]): %s", type(reserv[0]))
		logger.debug("type(self.engine.get_reservations_ids()): %s", type(self.engine.get_reservations_ids()))
		
		return self.engine.get_reservations_ids()

	def __run_instance(self, num_instances, ht_policies):
		"""Utility Function
		"""
		logger.info("In __run_instance()")
		policies = self.__hashtable_to_dictionary(ht_policies)
		logger.debug("policies(__run_instances): %s", policies )
		reservation = self.engine.run_instances(num_instances, policies)
		logger.debug("New reservation created: %s", reservation)
		logger.debug("Retrieving the reservation.id: %s", reservation.id)
		#sleep until the vm instance started and a ip is created

		#TODO:Review if all num_instances will be executed
		instances = reservation.instances
		logger.debug("instance(__run_instance): %s", instances)
		instances_ids = self.engine.get_ids(instances) # deprecated method in ResourceEngine 1.1
		logger.debug("instance_ids(__run_instance): %s", instances_ids)
		vm_started = num_instances
		logger.debug("vm_started: %s", vm_started)
		while vm_started > 0:
			for instance in instances:
				logger.debug("instance(in loop)%s", instance)
				logger.debug("instance.state.encode('latin'): %s", instance.state.encode('latin'))
				if instance.state.encode('latin') == 'running':
					vm_started = vm_started - 1
					if vm_started == 0:
						break
					logger.debug("instance_id: %s was started", instance)
			time.sleep(6)
			logger.debug("instances initializing: %s", vm_started)
			#update the instances from cloud (now will be return instance)
			#instances = self.get_instances(num_instances, None, instances_ids)
			logger.debug("instances_ids searching: %s", instances_ids)
			instances, num_instances_def = self.engine.get_instances(num_instances, None, instances_ids)
			logger.debug("Updating instances data: %s", instances)
			logger.debug("num_instances_def: %s", num_instances_def)
		return self.__get_reservation_info( reservation.id )

	def run_instances(self, num_instances, policies):
		"""Run Instances
		
		@type num_instances: string
		@param num_instances: a number of instances to executing
		
		@type policies: HashObjectSeq
		@type policies: A list of HashObjects
		
		@rtype ReservationInfo
		@return A ReservationInfo

		"""
		return self.__run_instance(num_instances, policies)	

	def get_all_instances(self):
		"""
		"""
		#TODO: not working, we must fix this call	
		return self.__get_instances_info( self.engine.get_instances_ids() )

	def get_num_instances(self):
		"""
		"""
		return self.engine.get_num_instances();

	def reboot_instances(self, instance_ids):
		"""
		"""
		return self.engine.reboot_instances(instance_ids)

	def terminate_instances(self, instance_ids):
		"""
		"""
		return self.engine.terminate_instances(instance_ids)

	def show_console(self, instance_ids):
		"""
		"""
		return self.engine.show_console(instance_ids)

	#Utility Functions
	
	def get_ip_instances(self, number_instances=1):
		"""Return a list of number_instances ips(publics)
		"""
		return self.engine.get_ips_instances( number_instances )

	def get_ips(self, instances):
		"""Return a list of all ips from instances
		"""
		return self.engine.get_ips( instances )

	def get_id_instances(self, number_instances=1):
		"""Return a list of number_instances ids
		"""
		return self.engine.get_ids_instances( number_instances )
	
	def get_ids(self, instances):
		"""Return a list of all ids from instances
		"""
		return self.engine.get_ids( instances )

	
class Image_i(ResourceManager__POA.Image):
	def __init__(self):
		self.image  = imageInstance()

	#Images Functions
	def get_emi_info(self, image_id):
		"""Return EMI(eucalyptus machine image) data
		"""
		logger.info("In get_emi_data")
		#TODO: exception if not image is returned
		images = self.image.get_images()
		for image in images:
			if image.id == image_id:
				break
		
		image_data = ResourceManager.ImageData(	image.location.encode('latin-1'),
							image.ownerId.encode('latin-1'),
							image.state.encode('latin-1'),
							"public", #image.type_access.enconde('latin-1'),
							image.architecture.encode('latin-1'),
							image.type.encode('latin-1'),
							image.ramdisk_id.encode('latin-1'),
							image.kernel_id.encode('latin-1'))

		image_info = ResourceManager.ImageInfo( image.id.encode('latin-1'),
							image_data)			

		logger.debug("Returning the image_info: %s", image_info)
		return image_info


class AvailabilityZone_i(ResourceManager__POA.AvailabilityZone):
	def __init__(self):
		self.availability_zone = availabilityZones()

	#AvailabilityZones
	def get_zones(self):
		"""Return all Availability Zones

		"""
		zones = self.availability_zone.get_zones()
		logger.debug("Availability Zones: %s", zones)
	
		availability_zones = []
		for zone in zones:
			zone_data = ResourceManager.ZoneData(	zone.name.encode('latin-1'),
								zone.state.encode('latin-1'))
			availability_zones.append(zone_data)

		return availability_zones
	
	def get_typevm_zones(self):
		"""Return all typevm
		"""
		logger.info("In get_typevm_zones()")		
		typevms = self.availability_zone.get_typevm_zones()
		logger.debug("Printing all typevms: %s", typevms)
	
		logger.info("Printing all typevm")
		list_typevm = []	

		for typevm in typevms:
			logger.debug("typevm: %s ", typevm)
			logger.debug("type(typevm): %s ", type(typevm))
			logger.debug("typevm(element): %s ", typevms[typevm])
			specifications  =  typevms[typevm]

			list_type_specification = []	
			for spec in specifications:
				logger.debug("spec: %s", spec)
				logger.debug("type(spec): %s", type(spec))
				logger.debug("value: %s", specifications[spec])
				logger.debug("type(value): %s", type(specifications[spec]))
				object = ResourceManager.HashObject( spec, str(specifications[spec]) )
				list_type_specification.append(object)

			typevm_object = ResourceManager.HashObjectComposed( typevm, list_type_specification )
			list_typevm.append(typevm_object)
				
		return list_typevm

		
		

# Initialise the ORB
orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)

# Find the root POA
poa = orb.resolve_initial_references("RootPOA")

# Create an instance of 
instancei = Instance_i()
imagei = Image_i()
zonei = AvailabilityZone_i()

# Create an object reference, and implicitly activate the object
instanceo = instancei._this()
imageo = imagei._this()
zoneo = zonei._this()

# Create ref.ior
ior = orb.object_to_string(instanceo)
file = open('ref.ior', 'w')
file.write(ior)
file.close()

# Create ref2.ior
ior2 = orb.object_to_string(imageo)
file2 = open('ref2.ior', 'w')
file2.write(ior2)
file2.close()

# Create ref3.ior
ior3 = orb.object_to_string(zoneo)
file3 = open('ref3.ior', 'w')
file3.write(ior3)
file3.close()

# Print out the IOR
print orb.object_to_string(instanceo)
print orb.object_to_string(imageo)
print orb.object_to_string(zoneo)

# Activate the POA
poaManager = poa._get_the_POAManager()
poaManager.activate()

# Everything is running now, but if this thread drops out of the end
# of the file, the process will exit. orb.run() just blocks until the
# ORB is shut down
orb.run()


#==================================================================
'''
# Initialise the ORB
orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)

# Find the root POA
poa = orb.resolve_initial_references("RootPOA")

# Create an instance of Instance
instancei = Instance_i()

# Create an instance of Image
imagei    = Image_i()

# Create an Zone
zonei     = AvailabilityZone_i()

# Create an object reference, and implicitly activate the object
instanceo = instancei._this()
imageo    = imagei._this()
zoneo     = zonei._this()

# Obtain a reference to the root naming context
obj         = orb.resolve_initial_references("NameService")
rootContext = obj._narrow(CosNaming.NamingContext)

if rootContext is None:
    print "Failed to narrow the root naming context"
    sys.exit(1)

# Bind a context named "test.my_context" to the root context
name = [CosNaming.NameComponent("test", "my_context")]

try:
    testContext = rootContext.bind_new_context(name)
    print "New test context bound"
except CosNaming.NamingContext.AlreadyBound, ex:
    print "Test context already exists"
    obj = rootContext.resolve(name)
    testContext = obj._narrow(CosNaming.NamingContext)
    if testContext is None:
        print "test.mycontext exists but is not a NamingContext"
        sys.exit(1)

# Bind the Instance object to the test context
name_instance = [CosNaming.NameComponent("ResourceManagerInstance", "Object")]
# Bind the Image object to the test context
name_image    = [CosNaming.NameComponent("ResourceManagerImage", "Object")]
# Bind the Image object to the test context
name_zone     = [CosNaming.NameComponent("ResourceManagerAvailabilityZone", "Object")]

try:
    testContext.bind(name_instance, instanceo)
    testContext.bind(name_image, imageo)
    testContext.bind(name_zone, zoneo)
    print "New Instace, Image object bound"

except CosNaming.NamingContext.AlreadyBound:
    testContext.rebind(name_instance, instanceo)
    testContext.rebind(name_image, imageo)
    testContext.rebind(name_zone, zoneo)
    print "Example Instance. Image binding already existed -- rebound"
    # Note that is should be sufficient to just call rebind() without
    # calling bind() first. Some Naming service implementations
    # incorrectly raise NotFound if rebind() is called for an unknown
    # name, so we use the two-stage approach above

# Activate the POA
poaManager = poa._get_the_POAManager()
poaManager.activate()
# Everything is running now, but if this thread drops out of the end
# of the file, the process will exit. orb.run() just blocks until the
# ORB is shut down
orb.run()
'''
