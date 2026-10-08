from librouteros import connect

api = connect(
    username='admin',
    password='Bismill@h',
    host='192.168.220.1',
    port=3101
)

resource = list(api.path('system', 'resource'))[0]

print(resource)
