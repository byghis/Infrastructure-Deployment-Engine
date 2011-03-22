import sys, os
import time
import logging
import logging.config
import ResourceManager, ResourceManager__POA

from instance import nodeInstance
from omniORB import CORBA, PortableServer

LOG_FILENAME='resource_manager.log'
logging.config.fileConfig('logging.conf')

# Create logger
logger = logging.getLogger('simpleExample')

class Instance_i(ResourceManager__POA.Instance):

	def __init__(self):
		self.engine = nodeInstance()
		
		#self.reservations    = []
		#self.reservation_ids = []
		#self.instances       = []
		#self.instance_ids    = []
	
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

	def get_instance_ids(self):
		"""
		@rtype: <class 'boto.resultset.ResultSet'>
		@return:
		"""
		instance_ids = self.engine.get_instances_ids()
		logger.debug("instance_ids(get_instances_ids): %s", instance_ids)
		logger.debug("type(instance_ids): %s", type(instance_ids))
		return instance_ids

	def get_num_instances(self):
		"""Get the number of instances
		"""
		logger.debug("number of instances: %s", self.engine.get_num_instances())
		return self.engine.get_num_instances()
	

	def __get_multi_instance_data(self, instance):
		"""Utility function
		"""
		#TODO: get instance from instance_id
		#instances, num_instances = self.engine.get_instances(1)
		#instance = instances[0]
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
		
		logger.debug("instance_data(__get_multi_instance_data): %s", instance_data)
		return instance_data
	
	def __get_instance_info(self, instance):
		"""Utility function
		"""
		logger.debug("instance_id(__get_instance_info): %s",instance.id)
		instance_data = self.__get_multi_instance_data(instance)
		instance_info = ResourceManager.InstanceInfo( instance.id.encode('latin-1'), instance_data )
		logger.debug("instance_info(__get_instance_info): %s", instance_info)
		return instance_info

	def __get_instances_info(self, instances):
		"""Utility function
		"""
		logger.debug("__get_instances_info: %s", instances)
		#for ins_id in instances_ids:
		#	self.instances.append( self.__get_instance_info(instances, ins_id) )
		instances_info=[]
		for instance in instances:
			instances_info.append( self.__get_instance_info(instance) )
		return instances_info
		
	def __hashtable_to_dictionary(self, hashtable):
		"""Convert a hashtable to hashmap
		"""
		policies = {}
		logger.debug("hashtable(__hashtable_to_dictionary): %s", hashtable)
		logger.debug("type(hashtable): %s", type(hashtable))
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
		
		logger.debug("dictionary(__hashtable_to_dictionary): %s", policies)
		return policies

	def get_instances(self, num_instances, ht_policies, instance_ids):
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
		
		@type policies: hashtable
		@param policies: Policies 
		
		@type instances_ids: list
		@param instances_ids: List ids

		@rtype self.instances: InstanceInfoSeq (list) 
		@return self.instances: InstanceInfo List
		"""

		logger.debug("num_instances(get_instances): %s", num_instances)
		logger.debug("ht_policies:%s", ht_policies)
		logger.debug("type(ht_policies):%s", type(ht_policies))
		logger.debug("instance_ids):%s", instance_ids)
		
		
		if ht_policies is None:
			logger.debug("no ht_policies: %s", type(ht_policies))
			policies = {}
		#if type(ht_policies) == type(list()):
		#	logger.debug("a policy specification was included: %s", type(ht_policies))
		policies = self.__hashtable_to_dictionary(ht_policies)
		
		logger.debug("dictionary policies: %s", policies)
		instances, num_instances = self.engine.get_instances(num_instances, policies, instance_ids)

		#getting ids (only for debugging)
		instance_ids = self.engine.get_ids( instances )		
		logger.debug("instances_ids(get_instances): %s", instance_ids )
		logger.debug("instance(get_instances): %s",  instances)
		logger.debug("type(instance): %s", type(instances[0]))
		logger.debug("instance.id: %s", instances[0].id)

		#
		#instances_infos = []
		#for inst in instances:
		#	instances_infos.append( self.__get_instance_info( inst.id ) )
		#return instances_infos

		return self.__get_instances_info( instances ) #return instances ids

	def __get_multi_reservation_data(self, reservation):
		"""
		"""
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
		"""
		"""

		reservation = None
		reservations = self.engine.get_reservations()
		found=False
		for reservation in reservations:
			if reservation.id == reservation_id:
				found=True
				break
		if not found:
			#TODO: raise a ReservationFailed CORBA exception
			sys.exit(1)
	
		reservation_data, reservation_instances_ids = self.__get_multi_reservation_data( reservation )
		reservation_info = ResourceManager.ReservationInfo(	reservation_id.encode('latin-1'), 
									reservation_data,
									self.__get_instances_info(reservation.instances)
									)
	
		logger.debug("Reservations Info: %s", reservation_info)
		return reservation_info

	def __get_reservations_info(self, reservation_ids):
		"""Get Reservations
		"""
		reservations_info=[]
		for reservation_id in reservation_ids:
			logger.debug("reservation_id(__get_reservations_info):%s", reservation_id)
			reservations_info.append( self.__get_reservation_info(reservation_id) )
		return reservations_info
	
	def get_reservations(self):
		"""Get Reservations
	
		@rtype:
		@return:

		"""
		reservations = self.engine.get_reservations()
		reservation_ids = []
		logger.debug("reservations(get_reservations): %s",  reservations)
		logger.debug("type(reservations): %s", type(reservations) )
		
		for reserv in reservations:
			logger.debug("reservation: %s", reserv )
			logger.debug("type(reservation): %s", type(reserv))
			logger.debug("reservation ID: %s", reserv.id.encode('latin-1'))
			reservation_ids.append(reserv.id.encode('latin-1'))

		logger.debug("reservations_ids: %s", reservation_ids)	
		return self.__get_reservations_info( reservation_ids )

	def get_reservation_ids(self):
		"""Get Reservations IDs
	
		@rtype:
		@return: Reservations
		"""
		reservation_ids = []
		reserv = self.engine.get_reservations()
		logger.debug("reservations(get_reservations): %s",  reserv)
		
		for res in reserv:
			reservation_ids.append(res.id.encode('latin-1'))
			logger.debug("reservation instance: %s", res.instances)

		return reservation_ids

	def __run_instance(self, num_instances, ht_policies):
		"""
		"""
		policies = self.__hashtable_to_dictionary(ht_policies)
		logger.debug("policies(__run_instances): %s", policies )
		reservation = self.engine.run_instances(num_instances, policies)
		logger.debug("New reservation created: %s", reservation)
		logger.debug("Retrieving the reservation.id: %s", reservation.id)
		#sleep until the vm instance started and a ip is created

		#TODO:Review if all num_instances will be executed
		instances = reservation.instances
		logger.debug("instance(__run_instance): %s", instances)
		instances_ids = self.engine.get_ids(instances)
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
		"""
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



# Initialise the ORB
orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)

# Find the root POA
poa = orb.resolve_initial_references("RootPOA")

# Create an instance of 
ii = Instance_i()

# Create an object reference, and implicitly activate the object
io = ii._this()

# Create ref.ior
ior = orb.object_to_string(io)
file = open('ref.ior', 'w')
file.write(ior)
file.close()

# Print out the IOR
print orb.object_to_string(io)

# Activate the POA
poaManager = poa._get_the_POAManager()
poaManager.activate()

# Everything is running now, but if this thread drops out of the end
# of the file, the process will exit. orb.run() just blocks until the
# ORB is shut down
orb.run()
