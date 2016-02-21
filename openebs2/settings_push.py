PUSH_DEFAULTS = {
    'timeout': 10,  # Seconds
    'debug': True  # Logs everything
}
PUSH_SETTINGS = [
    {'alias': 'govi',
     'enabled': True,
     'priority': 1,
     'failOnFailure': True,
     'host': 'localhost:8888',  #drisacc.transmodel.nl
     'subscriberName': 'openov',
     'endpoints': {
        'KV6': {'path': '/TMI_Post/KV6'},
        'KV15': {'path': '/TMI_Post/KV15'},
        'KV17': {'path': '/TMI_Post/KV17'}
     }
    },
    {'alias': 'ovapi',
     'enabled': False,
     'priority': 2,
     'failOnFailure': False,
     'host': 'ovrkv.ovapi.nl',
     'subscriberName': 'openov',
     'endpoints': {
         'KV15': {'path' : '/RIG/KV6posinfo'},
         'KV15': {'path' : '/RIG/KV15messages'},
         'KV17': {'path' : '/RIG/KV17cvlinfo'}
     }
    }
]