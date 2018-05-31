class Source(object):
    '''
    '''
    def __init__(self, file_like, data_types=None):
        '''
        A source of data.
        '''
        pass


class OpenCluster(object):
    '''
    '''
    coord = None
    fe_h = None
    tau = None
    eb_v = None
    Z = None
    d_modulus = None  # (m - M)
    name = None
    image_path = None
    source = None
    
    def __init__(self, friendly_name, coord, source,
                 fe_h=None, tau=None, eb_v=None, Z=None,
                 d_modulus=None, name=None, image_path=None):
        self.friendly_name = friendly_name
        self.coord = coord
        self.source = source
        self.fe_h = fe_h
        self.tau = tau
        self.eb_v = eb_v
        self.Z = Z
        self.d_modulus = d_modulus
        self.name = name
        self.image_path = image_path

    def __repr__(self):
        return '<astropixie.OpenCluster %s %s>' % (self.name, self.coord)

    def __str__(self):
        return self.__repr__()
    

class Star(object):
    def __init__(self, u_mag=None, b_mag=None, v_mag=None,
                 g_mag=None, r_mag=None, i_mag=None, z_mag=None, y_mag=None):
        self.u_mag = u_mag
        self.b_mag = b_mag
        self.v_mag = v_mag
        self.g_mag = g_mag
        self.r_mag = r_mag
        self.i_mag = i_mag
        self.z_mag = z_mag
        self.y_mag = y_mag

    def __repr__(self):
        s = '<astropixie.Star'
        for name, value in {'u': self.u_mag,
                            'b': self.b_mag,
                            'v': self.v_mag,
                            'g': self.g_mag,
                            'r': self.r_mag,
                            'i': self.i_mag,
                            'z': self.z_mag,
                            'y': self.y_mag}:
            if value:
                s += ' {0}={1:0.2f}'.format(name, value)
        s += '>'
        return s

    def __str__(self):
        return self.__repr()
