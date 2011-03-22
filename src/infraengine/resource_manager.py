from instance import nodeInstance

"""
SCS Component Deployment Scenario
----------------------------------
A scenario to SCS Components Deployment is required for a simple test deployment.
The adminstrator needs to implement a minimal Resource Manager. The API implemented
has the main functions enabling reuse functions.
The plain design speficies:
- A function to get four instances
- A function to reboot the four instances
- Support a simple log in for the instances, example ssh
"""

class ResourceManager:
    """
    Public API
    get_instances(specifications)
    reboot_instances(instances_ids)
    show_instances(instances_ips)
    """

    def __init__(self):
        self.instances = None
        self.engine = nodeInstance()

    def get_instances(self, specifications):
        """Get vm instances or create new VMs according the specifications

        Keyword arguments:
        specifications -- list of list containing the instance specifications

        """
        instances = []
        instances_ok = []
        reservations = []
        for spec in specifications:
            instance, instance_ok  = self.engine.get_instances(1, spec)
            if instance:
                instances.append(instance)
                instances_ok.append(instance_ok)

            else:
                reservation = self.engine.run_instances(1, spec)
                reservations.append(reservation)

        self.instances = instances
        return instances, instances_ok, reservations


    def reboot_instances(self, instances_ids):
        """Reboot instances

        Keyword arguments:
        instances_ids -- list of instances_ids necessary to reboot the instances

        """
        return self.engine.reboot_instances( instances_ids )

    def show_instances(self, instances_ips):
        """Loggging a show the instances

        Keyword arguments:
        instances_ips -- list of instances_ips necessary to logging

        """
        return self.engine.show_console( instances_ips )