PUSH_DEFAULTS = {
    'timeout': 10,  # Seconds
    'debug': True  # Logs everything
}
PUSH_SETTINGS = [
    {'alias' : 'govi',
     'enabled' : True,
     'priority' : 1,
     'failOnFailure' : True,
     'host' : 'localhost:8888',#drisacc.transmodel.nl
     'subscriberName' : 'openov',
     'endpoints' : {
        'KV6' : {'path' : '/TMI_Post/KV6POSINFO'},
        'KV15' : {'path' : '/TMI_Post/KV15'},
        'KV17' : {'path' : '/TMI_Post/KV17'}
     }
    },
    {'alias' : 'ovapi',
     'enabled' : True,
     'priority' : 2,
     'failOnFailure' : False,
     'host' : 'ovrkv.ovapi.nl',
     'subscriberName' : 'openov',
     'endpoints' : {
         'KV6' : {'path' : '/RIG/KV6posinfo'},
         'KV15' : {'path' : '/RIG/KV15messages'},
         'KV17' : {'path' : '/RIG/KV17cvlinfo'}
     }
    },
    {'alias' : 'ndovloket_rig',
      'enabled' : True,
      'priority' : 3,
      'failOnFailure' : False,
      'host' : '87.213.168.1',
      'subscriberName' : 'RIG-NDOV',
      'endpoints' : {
        'KV15' : {'path' : '/rcv-htm-01-acc/KV15.aspx'},
        'KV17' : {'path' : '/rcv-htm-01-acc/KV17.aspx'}
      }
    }
]
