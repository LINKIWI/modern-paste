import config


class URI:
    fqdn = config.DOMAIN
    path = '/'
    api_endpoint = False

    def __init__(self):
        pass

    @classmethod
    def uri(cls, **kwargs):
        embedded_params = set([key for key in kwargs if '<{key}>'.format(key=key) in cls.path])
        params = [
            '{key}={param}'.format(key=key, param=param)
            for key, param in kwargs.items()
            if key != 'https' and key not in embedded_params and len(str(param)) > 0
        ]
        uri_str = str(cls.path)
        for embedded_param in embedded_params:
            uri_str = uri_str.replace('<{key}>'.format(key=embedded_param), str(kwargs[embedded_param]))
        if params:
            uri_str += '?{params}'.format(params='&'.join(params))
        return uri_str

    @classmethod
    def full_uri(cls, **kwargs):
        return cls.protocol_prefix(https=kwargs.get('https', config.DEFAULT_HTTPS)) + cls.fqdn + cls.uri(**kwargs)

    @classmethod
    def get_path(cls):
        return cls.path

    @classmethod
    def protocol_prefix(cls, https=config.DEFAULT_HTTPS):
        return 'https://' if https else 'http://'
