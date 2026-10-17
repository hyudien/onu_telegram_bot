from mikrotik.api import get_api

api = get_api("KWL")

resource = list(api.path('system', 'resource'))[0]

print(resource)
