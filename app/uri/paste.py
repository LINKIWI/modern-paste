from base_uri import URI


class PastePostInterfaceURI(URI):
    path = '/paste/new'


class PasteViewInterfaceURI(URI):
    path = '/paste/<paste_id>'


class PasteViewRawInterfaceURI(URI):
    path = '/paste/<paste_id>/raw'


class PasteDeactivateInterfaceURI(URI):
    path = '/paste/<paste_id>/deactivate/<deactivation_token>'


class PasteArchiveInterfaceURI(URI):
    path = '/archive'


class PasteSubmitURI(URI):
    api_endpoint = True
    path = '/api/paste/submit'


class PasteDeactivateURI(URI):
    api_endpoint = True
    path = '/api/paste/deactivate'


class PasteDetailsURI(URI):
    api_endpoint = True
    path = '/api/paste/details'


class RecentPastesURI(URI):
    api_endpoint = True
    path = '/api/paste/recent'


class TopPastesURI(URI):
    api_endpoint = True
    path = '/api/paste/top'
