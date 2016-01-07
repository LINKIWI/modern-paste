from base_uri import URI


class PasteViewInterfaceURI(URI):
    path = '/paste/<paste_id>'


class PasteDeactivateInterfaceURI(URI):
    path = '/paste/<paste_id>/deactivate/<deactivation_token>'


class PasteSubmitURI(URI):
    api_endpoint = True
    path = '/api/paste/submit'


class PasteDeactivateURI(URI):
    api_endpoint = True
    path = '/api/paste/deactivate'


class PasteDetailsURI(URI):
    api_endpoint = True
    path = '/api/paste/details'
