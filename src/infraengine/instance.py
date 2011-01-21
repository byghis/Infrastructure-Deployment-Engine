import os, sys, random
from euca2ools import Euca2ool, InstanceValidationError
from availability_zones import availabilityZones
from images import imageInstance

# Default directory to include virtual machines private keys
INFRA_DEPLOY   = "/opt/infra_deployment_engine"

# Default instances types in Eucalyptus Cloud
INSTANCE_TYPES = ['m1.small', 'c1.medium', 'm1.large', 'm1.xlarge', 'c1.xlarge']

class nodeInstance():
    """Class Infrastructure Deployment Engine
    Public API
     1. get_reservations(instance_ids=None)
     2. get_reservations_ids(instance_ids=None)
     3. get_instances(number_instances, policies=None, instance_ids=None)
     4. get_all_instances()
     5. get_instances_ids()
     6. get_num_instances()
     7. run_instances(number=1, policies=None)
     8. reboot_instances(instance_ids)
     9. terminate_instance(instance_ids)
    10. get_ips_instances(num_instances=1)
    11. get_ids_instances(num_instances=1)
    12. get_ids(instances)
    13. get_ips(instances)
    14. show_console(ips)
    """

    def __init__ (self):
        self.euca         = None  #Euca2ool Object
        self.reservations = None  #Reservations of Instances
        self.instance_ids = None  #Instances ids
        self.__init_euca()        #Initialize a Euca2ool Object
        
    def __init_euca(self):
        """Return a Euca2ool Object
        """
        if self.euca:
            return
        self.euca = Euca2ool()

    def __make_connection(self):
        """Return a boto onnection (see Boto Python API)
        """
        return self.euca.make_connection()
    
    def __validate_instance_id(self, instance_ids):
        """Validate one or more instance ids

        Keyword arguments:
        instance_ids -- list containing the instances_ids to validate

        """
        try:
            if instance_ids:
                for id in instance_ids:
                    self.euca.validate_instance_id(id)
        except InstanceValidationError:
            sys.exit(1)

    def __get_reservations(self, instance_ids=None):
        """Validate instance_ids and get reservations deployed

        Keyword arguments:
        instance_ids -- list of instance_ids used to return the reservations

        """
        if instance_ids:
            self.__validate_instance_id(instance_ids)
        euca_conn = self.__make_connection()
        try:
            return euca_conn.get_all_instances(instance_ids)
        except:
            euca.display_error_and_exit('%s' % ex)
            return False

    def get_reservations(self, instance_ids=None):
        """Get Reservations deployed

        Keyword arguments:
        instance_ids -- list of instance_ids to return the reservations

        """
        return self.__get_reservations(instance_ids)

    def get_reservations_ids(self, instance_ids=None):
        """Get Reservations ids deployed

        Keyword arguments:
        instance_ids -- list of instance_ids to return the reservations ids

        """
        reservations = self.__get_reservations(instance_ids)
        reservations_ids = []
        for reservation in reservations:
            reservations_ids.append(reservation.id.encode("latin-1"))

        return reservations_ids

    def __get_multi_instances(self, reservations, instance_ids=None, policies=None):
        """Utility function to get multi-instances.
        Return instances and the number of instances returned

        Keyword arguments:
        reservations -- reservations dictionary containing all instances
        instance_ids -- list of instances_ids to return specific instances from the instance_ids
        policies     -- dictionary containing the values of requeriments

        """
        check_instance_ids = False
        if ( instance_ids and len(instance_ids) > 0 ):
            check_instance_ids = True
        instances = []        
        for reservation in reservations:
            if check_instance_ids:
                for instance in reservation.instances:
                    if instance.id in instance_ids:
                        instances.append(instance)
            elif policies:
                for instance in reservation.instances:
                    if 'typevm' in policies and instance.instance_type == policies['typevm']:
                        instances.append(instance)                    
                    elif policies.get('level')==1:
                        if self.__compare_types_instances(policies, instance.instance_type.encode("latin-1")):
                            instances.append(instance)
                    elif policies.get('level') == 0:
                        if self.__is_adaptive_instance(self.__get_metrics_adapted(policies), instance.instance_type.encode("latin-1")):
                            instances.append(instance)
                    else:
                        instances=[]
            else:
                instances += reservation.instances
        return instances, len(instances)

    def __get_metrics_adapted(self, policies):
        """Calculate and return the metrics adapted.

        Keyword arguments:
        policies -- dictionary of policies (cpu, ram, disk)

        """
        percent_min = 1 - policies['percent']
        percent_max = 1 + policies['percent']
        metrics = {'cpu_min':percent_min*policies['cpu'], 'cpu_max':percent_max*policies['cpu'],
                   'memory_min':percent_min*policies['ram'], 'memory_max':percent_max*policies['ram'],
                   'disk_min':percent_min*policies['disk'], 'disk_max':percent_max*policies['disk']}
        return metrics

    def __compare_types_instances(self, policies, instance_type):
        """Compare and return if exist one instance equal some policies (cpu, ram, disk)

        Keyword argument:
        policies -- dictionary of policies (cpu, ram, disk)
        instance_type -- type of instance 

        """
        zones  = availabilityZones()
        types_ins = zones.get_typevm_zones()

        if ( types_ins[instance_type]['cpu'] == policies['cpu'] and
             types_ins[instance_type]['ram'] == policies['ram'] and
             types_ins[instance_type]['disk']== policies['disk'] ):
            return 1
        return 0
    
    def __is_adaptive_instance(self, policies, instance_type):
        """Return true if is possible adapt the instance_type for the policies

        Keyword argument:
        policies -- dictionary of policies (cpu, ram, disk)
        instance_type -- type of instance 

        """
        zones  = availabilityZones()
        typevms = zones.get_typevm_zones()
        if ( typevms[instance_type]['cpu']  >= policies['cpu_min']    and typevms[instance_type]['cpu']  <= policies['cpu_max']    and
             typevms[instance_type]['ram']  >= policies['memory_min'] and typevms[instance_type]['ram']  <= policies['memory_max'] and
             typevms[instance_type]['disk'] >= policies['disk_min']   and typevms[instance_type]['disk'] <= policies['disk_max'] ):
            return True
        return False

    def __find_adaptive_image(self, policies):
        """Find and return true and the instance_type true according policies

        Keyword argument:
        policies -- dictionary of policies (cpu, ram, disk)

        """
        instances_types = INSTANCE_TYPES;
        if policies['level'] == 1:
            for instance_type in instances_types:
                if self.__compare_types_instances( policies, instance_type ):
                    return True, instance_type
        elif policies['level'] == 0:
            for instance_type in instances_types:
                if self.__is_adaptive_instance( self.__get_metrics_adapted(policies), instance_type ):
                    return True, instance_type
        else:
            return False, None

    def __get_instances(self, instance_ids=None, policies=None):
        """Return the instances

        Keyword argument:
        instance_ids -- list of instance_ids
        policies -- dictionary of policies (cpu, ram, disk)

        """
        self.reservations = self.__get_reservations(instance_ids)
        return self.__get_multi_instances(self.reservations, instance_ids, policies)

    def get_instances(self, number_instances, policies=None, instance_ids=None):
        """Get the nummber of instances(number_instances)

        Keyword argument:
        number_instances -- number of instances to return
        policies -- the instances will be selected according the policies (cpu, ram, disk)
        instance_ids -- get only the instances from the list instance_ids

        """
        ins = []
        if policies:
            ins, num_ins = self.__get_instances(instance_ids, policies)
            if number_instances < len(ins):
                random.shuffle(ins)
                ins = ins[:number_instances]
        else:
            ins, num_ins = self.__get_instances(instance_ids)
            if number_instances < len(ins):
                random.shuffle(ins)
                ins = ins[:number_instances]
        return ins, num_ins - number_instances

    def get_all_instances(self):
        """ Return all instances
        """
        self.instance_ids = self.euca.process_args()
        self.reservations = self.__get_reservations(self.instance_ids)
        return self.__get_multi_instances(self.reservations)

    def get_instances_ids(self):
        """ Return all instances ids
        """
        reservations = self.__get_reservations()
        instances_ids = []
        instances,_ = self.__get_multi_instances(reservations)
        for instance in instances:
            instances_ids.append(instance.id.encode("latin-1"))
        return instances_ids

    def get_num_instances(self):
        """Return the total number of instances
        """
        return len( self.get_instances_ids() ) 
        
    def __run_instances(self, number=1, policies={}):
        """ Run instances (by default use the virtual machine image

        Keyword arguments:
        number -- number of instances to execute (default 1)
        policies -- list of requirements for the virtual machine image

        """
        try:
            self.euca = Euca2ool('k:n:t:g:d:f:z:',
                                ['key=', 'kernel=', 'ramdisk=', 'instance-count=', 'instance-type=',
                                'group=', 'user-data=', 'user-data-file=', 'addressing=', 'availability-zone='])
        except Exception, ex:
            sys.exit(1)

        instance_type = policies.get('instance_type') or 'm1.small'
        image_id      = policies.get('image_id') or self.__get_image_id()[0]
        min_count  = number
        max_count  = number
        keyname    = 'mykey'
        
        kernel_id  = None
        ramdisk_id = None
        group_names     = []
        user_data       = None
        addressing_type = None
        zone            = None
        user_data       = None
        
        if image_id:
            euca_conn = self.__make_connection()
            try:
                reservation = euca_conn.run_instances(image_id = image_id,
                                                      min_count = min_count,
                                                      max_count = max_count,
                                                      key_name = keyname,
                                                      security_groups = group_names,
                                                      user_data = user_data,
                                                      addressing_type = addressing_type,
                                                      instance_type = instance_type,
                                                      placement = zone,
                                                      kernel_id = kernel_id,
                                                      ramdisk_id = ramdisk_id)
            except Exception, ex:
                self.euca.display_error_and_exit('error:%s' % ex)
            return reservation
        return False

    def __get_multi_images_ids(self, num_images=0):
        """Return the virtual machine images registered

        Keyword arguments:
        num_images -- return the number of images ids

        """        
        availability_images = imageInstance()
        images = availability_images.get_images()
        images_ids = []
        for image in images:
            if image.type == 'machine':
                images_ids.append( image.id.encode("latin-1") )
        if num_images>1:
            random.shuffle(images_ids)
            return images_ids[:num_images]
        return images_ids

    def __get_image_id(self):
        """Get one image id
        """
        return self.__get_multi_images_ids(1)

    def __is_image_id( self, image_id ):
        """Return true if the image_id is registered

        Keyword arguments:
        image_id -- id of the virtual machine image

        """
        images_ids = self.__get_multi_images_ids()
        for id in images_ids:
            if image_id == id:
                return True
        return False
    
    def __is_type_instance( self, instance_type ):
        """Return true if the instace type exist

        Keyword arguments:
        instance_type -- type of instance to verify

        """
        for index, instance in enumerate(INSTANCE_TYPES):
            if instance == instance_type:
                return True
        return False

    def __verify_policies( self, policies ):
        """Get one Image Id, Type of Instance and State according some policies(requirements)

        Keyword arguments:
        policies -- dictionary containing the values of requeriments to verify

        """
        image_id = ''
        instance_type=''
        if type(policies) == type(str()):
            if self.__is_type_instance( policies ):
                instance_type = policies
                state = True
            elif self.__is_image_id( policies ):
                image_id = policies
                state = True
            else:
                state = False
        else:
            verify, ins_type = self.__find_adaptive_image( policies )
            if verify:
                instance_type = ins_type
                state = True

        image_id = image_id or self.__get_image_id()
        instance_type = instance_type or 'm1.small'
        state = state or False

        return image_id, instance_type, state

    def run_instances(self, number=1, policies=None):
        """Run Instances

        Keyword arguments:
        number -- number of virtual machines to instance
        policies -- list of requirements for the virtual machine image

        """
        if not policies:
            return self.__run_instances(number)
        else:
            image_id, instance_type, is_available = self.__verify_policies( policies )
            if type(policies)==type(str()):
                policies={}
            if is_available:                
                policies['image_id'] = image_id[0]
                policies['instance_type'] = instance_type
                return self.__run_instances( number, policies )
        return None

    def reboot_instances(self, instance_ids):
        """Reboot instances

        Keyword arguments:
        instance_ids -- list containing instances ids to reboot

        """
        instances_reboot = []
        if (len(instance_ids) > 0):
            self.__validate_instance_id(instance_ids)       
            euca_conn = self.__make_connection()
            for instance_id in instance_ids:
                try:
                    return_code = euca_conn.reboot_instances(instance_id)
                    instances_reboot.append(return_code)
                except Exception, ex:
                    self.euca.display_error_and_exit('%s' % ex)
            return instances_reboot
        else:
            return False

    def terminate_instance(self, instance_ids):
        """Shutdown the instance(s) instance_ids

        Keyword arguments:
        instance_ids -- dictionary containing instances ids to poweroff
        
        """
        instances_terminated = []
        if (len(instance_ids) > 0):
            self.__validate_instance_id(instance_ids)
            euca_conn = self.__make_connection()
            for instance_id in instance_ids:
                try:
                    instance = euca_conn.terminate_instances(instance_id.encode("latin-1"))
                    instances_terminated.append(instance)
                except Exception, ex:
                    self.euca.display_error_and_exit('%s' % ex)

            return instances_terminated
        else:
            return False

    def get_ips_instances(self, num_instances=1):
        """Return Ip(s) instances
        
        Keyword arguments:
        num_instances -- number of ip(s) required

        """
        instances,_ = self.__get_multi_instances( self.__get_reservations() )
        ips = []
        for instance in instances:
            ips.append(instance.public_dns_name)

        return ips[:num_instances]

    def get_ids_instances(self, num_instances=1):
        """Return id(s) instances

        Keyword arguments:
        num_instances -- number of id(s) that will be returned

        """
        instances_ids = self.get_instances_ids()
        random.shuffle(instances_ids)
        return instances_ids[:num_instances]

    def get_ids(self, instances):
        """Return ids from instances

        Keyword arguments:
        instances -- list of instances necessary to get the ids

        """
        instance_ids = []
        for instance in instances:
            instance_ids.append(instance.id)
        return instance_ids

    def get_ips(self, instances):
        """Return ips from instances

        Keyword arguments:
        instances -- list of instances necessary to get the ips

        """
        public_ips = []
        for instance in instances:
            public_ips.append(instance.public_dns_name)
        return public_ips

    def show_console(self, ips):
        """Show Xterm Terminal Sessions

        Keyword arguments:
        ips -- list of ips to logging

        """
        geometry= ['63x19+0+0', '63x19+645+0', '63x17+645+420', '63x17+0+420']
        os.chdir(INFRA_DEPLOY)

        if len(ips)==1:
            ACCESS_VM = "xterm -e 'ssh -i mykey.private root@" + ips[0] + "' &"
            os.system(ACCESS_VM)
            return True

        else:
            i=0
            for ip in ips:
                ACCESS_VM = "xterm -geometry " + geometry[i]  + " -e 'ssh -i mykey.private root@" + ip + "' &"
                os.system(ACCESS_VM)
                i+=1
            return True
        return False