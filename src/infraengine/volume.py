from euca2ools import Euca2ool, SizeValidationError, SnapshotValidationError

class volumeStorage():
    """
    Public API
    1. create_volume(size = 1, zone = 'clusterpituba', snapshot_id = None)
    2. get_volumes(volume_ids=None )
    3. get_volumes_ids()
    4. delete_volumes(volume_ids=None)
    """
    def __init__(self):
        self.euca = None
        self.size = None
        self.zone = None
        self.snapshot_id = None
        self.__init_euca()

    def __init_euca(self):
        """Return a Euca2ool Object
        """
        if self.euca:
            return
        self.euca = Euca2ool('s:z:', ['zone=', 'snapshot=', 'size='], compat=True)

    def __make_connection(self):
        """Return a boto onnection (see Boto Python API)
        """
        return self.euca.make_connection()

    def create_volume(self, size=1, zone='clusterpituba', snapshot_id=None):
        """Create a New Volume (see Storage Controller Eucalyptus)

        Keyword arguments:
        
        size -- the volume size (default 1GB)
        zone -- the zone or cluster (default clusterpituba)
        snapshot_id -- the snapshot_id (default None)
        
        """
        self.size = size
        self.zone = zone
        self.snapshot_id = snapshot_id

        euca_conn = self.__make_connection()

        if self.size:
            try:
                self.euca.validate_volume_size(self.size)
            except SizeValidationError:
                sys.exit(1)

        if self.snapshot_id:
            try:
                self.euca.validate_snapshot_id(self.snapshot_id)
            except SnapshotValidationError:
                sys.exit(1)

        try:
            volume = euca_conn.create_volume(self.size, self.zone, self.snapshot_id)

            return volume
        except Exception, ex:
            self.euca.display_error_and_exit('%s' % ex)

        return False

    def get_volumes(self, volume_ids=None):
        """Return all Volumes

        Keyword arguments:

        volume_ids -- List of volumen ids

        """
        if volume_ids:
            try:
                for id in volume_ids:
                    euca.validate_volume_id(id)
            except VolumeValidationError:
                sys.exit(1)
        
        euca_conn = self.__make_connection()
        try:
            volumes = euca_conn.get_all_volumes()
        except Exception, ex:
            euca.display_error_and_exit('%s' % ex)

        return volumes

    def get_volumes_ids(self):
        """Get Volumes Ids
        """
        volumes_ids = []
        volumes = self.get_volumes()
        for volume in volumes:
            volumes_ids.append(volume.id)
        return volumes_ids

    def delete_volumes(self, volume_ids=None):
        """Delete volumes

        Keyword arguments:

        volume_ids -- List of volumen ids to delete

        """        
        if volume_ids:
            for volume_id in volume_ids:
                try:
                    self.euca.validate_volume_id(volume_id)
                except VolumeValidationError:
                    sys.exit(1)

        self.euca_conn = self.euca.make_connection()

        volumes_codes_deleted = []
        volumes_return_code = []
        volume_ids_delete = volume_ids or self.get_volumes_ids()

        for volume_id in volume_ids_delete:
            try:
                return_code = self.euca_conn.delete_volume(volume_id)
                volumes_codes_deleted.append(volume_id)
                volumes_return_code.append(return_code)
            except Exception, ex:
                euca.display_error_and_exit('%s' % ex)

        return volumes_codes_deleted, volumes_return_code

    

