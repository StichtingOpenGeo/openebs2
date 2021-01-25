PUSH_DEFAULTS = {
    'timeout': 10,  # Seconds
    'debug': True  # Logs everything
}

# EXAMPLE CONFIG
# {'alias': 'govi',
#  'enabled': True,
#  'priority': 1,
#  'failOnFailure': True,
#  'host': 'drisacc.transmodel.nl',
#  'subscriberName': 'openov',
#  'https': True,
#  'endpoints': {
#     'KV6': {'path': '/TMI_Post/KV6'},
#     'KV15': {'path': '/TMI_Post/KV15'},
#     'KV17': {'path': '/TMI_Post/KV17'}
#  }

PUSH_SETTINGS = []

"""
{'alias' : 'ndovloket',
     'enabled' : True,
     'priority' : 2,
     'failOnFailure' : True,
     'host' : 'postacc.ndovloket.nl',
     'subscriberName' : 'openov',
     'endpoints' : {
         'KV15' : {'path' : '/OPENOV/KV15messages'},
         'KV17' : {'path' : '/OPENOV/KV17cvlinfo'}
     }
}"""