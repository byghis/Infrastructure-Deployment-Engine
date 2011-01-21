from euca2ools import Euca2ool

class imageInstance():

    def __init__(self):
        self.euca = None
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

    def get_images(self):
        """Get all images registered
        """
        euca_conn = self.__make_connection()
        try:
            images = euca_conn.get_all_images()        
        except Exception, ex:
            euca.display_error_and_exit('%s' % ex)

        return images

            