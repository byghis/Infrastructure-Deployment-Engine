from euca2ools import Euca2ool

class availabilityZones():
    """Class Availability Zones
    Public API
    1. get_zones(policies=None)
    2. get_zones_detailed()
    3. get_typevm_zones()
    """

    def __init__(self):
        self.euca = None
        self.zone = None
        self.__init_euca()

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

    def __get_zones(self, parameter=None):
        """Get Zones (Zone is Cluster in Eucalyptus)

        Keyword arguments:
        parameter -- option to get detailed info of the zones

        """
        euca_conn = self.__make_connection()
        try:
             zones = euca_conn.get_all_zones(parameter)
        except Exception, ex:
            euca.display_error_and_exit('%s' % ex)

        return zones

    def get_zones(self):
        """Get Zones (Zone means Clusters in Eucalyptus)
        """
        return self.__get_zones()

    def get_zones_detailed(self):
        """Get Zones and TypeVMs in it (Zone means Clusters in Eucalyptus)
        """
        return self.__get_zones('verbose')

    def get_typevm_zones(self):
        """Return list containing only main values
        """
        zones = self.__get_zones('verbose')        
        zones = zones[2:]
        detailed_zones = []
        for zone in zones:
            zone_string = '%s %s' % (zone.name, zone.state)
            temp = zone_string.encode("latin-1").split(' ')
            temp.remove('|-')
            temp.remove('/')
            while (len(temp)>=7):
                temp.remove('')
            detailed_zones.append(temp)
        typevm_zones = {}
        for zone in detailed_zones:
            dzones = {}
            dzones['free'] = zone[1]
            dzones['max']  = zone[2]
            dzones['cpu']  = int(zone[3])
            dzones['ram']  = int(zone[4])
            dzones['disk'] = int(zone[5])
            typevm_zones[zone[0]] = dzones
        return typevm_zones
