var qryAggStock = {
    "aggs": {
        "vehicles_running": {
            "aggs": {
                "avenio_count": {
                    "aggs": {
                        "vehicle_count": {
                            "cardinality": {
                                "field": "vehiclenumber"
                            }
                        }
                    },
                    "filter": {
                        "range": {
                            "vehiclenumber": {
                                "gte": 5000,
                                "lte": 5999
                            }
                        }
                    }
                },
                "bus_count": {
                    "aggs": {
                        "vehicle_count": {
                            "cardinality": {
                                "field": "vehiclenumber"
                            }
                        }
                    },
                    "filter": {
                        "range": {
                            "vehiclenumber": {
                                "gte": 0,
                                "lte": 2999
                            }
                        }
                    }
                },
                "gtl_count": {
                    "aggs": {
                        "vehicle_count": {
                            "cardinality": {
                                "field": "vehiclenumber"
                            }
                        }
                    },
                    "filter": {
                        "range": {
                            "vehiclenumber": {
                                "gte": 3000,
                                "lte": 3999
                            }
                        }
                    }
                },
                "rr_count": {
                    "aggs": {
                        "vehicle_count": {
                            "cardinality": {
                                "field": "vehiclenumber"
                            }
                        }
                    },
                    "filter": {
                        "range": {
                            "vehiclenumber": {
                                "gte": 4000,
                                "lte": 4999
                            }
                        }
                    }
                }
            },
            "date_histogram": {
                "field": "vehicle",
                "interval": "15m"
            }
        }
    }
}

var qryAggTrips = {
    "aggs": {
        "trips_active_per_15m": {
            "date_histogram": {
                "field": "vehicle",
                "interval": "15m"
            },
            "aggs": {
                "trips_active": {
                    "cardinality" : {
                        "script": "doc['dataownercode'].value + '|' + doc['lineplanningnumber'].value + '|' + doc['journeynumber'].value"
                    }
                }
            }
        }
    }
}

var qryAggLocations = {
        "size": 0,
        "aggs": {
        "javalaan": {
            "aggs": {
                "voertuigen": {
                    "aggs": {
                        "voertuig": {
                            "top_hits": {
                                "_source": {
                                    "include": [
                                        "vehiclenumber",
                                        "vehicle"
                                    ]
                                },
                                "size": 1,
                                    "sort": [
                                    {
                                        "vehicle": {
                                            "order": "desc"
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    "terms": {
                        "field": "vehiclenumber",
                            "size": 1000
                    }
                }
            },
            "filter": {
                "geo_polygon": {
                    "location": {
                        "points": [
                            [
                                4.535133567425533,
                                52.0523457791015
                            ],
                            [
                                4.53133286100071,
                                52.04864989035698
                            ],
                            [
                                4.532641690541396,
                                52.04817749568706
                            ],
                            [
                                4.536457298075048,
                                52.05184694841677
                            ],
                            [
                                4.535133567425533,
                                52.0523457791015
                            ]
                        ]
                    }
                }
            }
        },

        "lijsterbes": {
            "aggs": {
                "voertuigen": {
                    "aggs": {
                        "voertuig": {
                            "top_hits": {
                                "_source": {
                                    "include": [
                                        "vehiclenumber",
                                        "vehicle"
                                    ]
                                },
                                "size": 1,
                                    "sort": [
                                    {
                                        "vehicle": {
                                            "order": "desc"
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    "terms": {
                        "field": "vehiclenumber",
                            "size": 1000
                    }
                }
            },
            "filter": {
                "geo_polygon": {
                    "location": {
                        "points": [
                            [4.263169148476836,52.0733812011305], [4.264207920507229,52.07167322262809], [4.265713148325236,52.07221959858738], [4.264673236683619,52.07391038624953], [4.263169148476836,52.0733812011305]
                        ]
                    }
                }
            }
        },

        "radarstraat": {
            "aggs": {
                "voertuigen": {
                    "aggs": {
                        "voertuig": {
                            "top_hits": {
                                "_source": {
                                    "include": [
                                        "vehiclenumber",
                                        "vehicle"
                                    ]
                                },
                                "size": 1,
                                    "sort": [
                                    {
                                        "vehicle": {
                                            "order": "desc"
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    "terms": {
                        "field": "vehiclenumber",
                            "size": 1000
                    }
                }
            },
            "filter": {
                "geo_polygon": {
                    "location": {
                        "points": [
                            [4.302160347583976,52.05913797841928],[4.303132991260856,52.05832093270067],[4.305570042675589,52.0593668438804],[4.304549224242544,52.0602346956703],[4.302160347583976,52.05913797841928]
                        ]
                    }
                }
            }
        },

        "scheveningen": {
            "aggs": {
                "voertuigen": {
                    "aggs": {
                        "voertuig": {
                            "top_hits": {
                                "_source": {
                                    "include": [
                                        "vehiclenumber",
                                        "vehicle"
                                    ]
                                },
                                "size": 1,
                                    "sort": [
                                    {
                                        "vehicle": {
                                            "order": "desc"
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    "terms": {
                        "field": "vehiclenumber",
                            "size": 1000
                    }
                }
            },
            "filter": {
                "geo_polygon": {
                    "location": {
                        "points": [
                            [4.287752464113865,52.11289837052913],[4.288222541352919,52.11243888946534],[4.290884126692005,52.11294421810653],[4.291255053316081,52.11295828704039],[4.291233250799909,52.11327113832045],[4.287964156237276,52.11369397791811],[4.287752464113865,52.11289837052913]
                        ]
                    }
                }
            }
        },

        "zichtenburg": {
            "aggs": {
                "voertuigen": {
                    "aggs": {
                        "voertuig": {
                            "top_hits": {
                                "_source": {
                                    "include": [
                                        "vehiclenumber",
                                        "vehicle"
                                    ]
                                },
                                "size": 1,
                                    "sort": [
                                    {
                                        "vehicle": {
                                            "order": "desc"
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    "terms": {
                        "field": "vehiclenumber",
                            "size": 1000
                    }
                }
            },
            "filter": {
                "geo_polygon": {
                    "location": {
                        "points": [
                            [4.248005163933253,52.0417095523282],[4.250234142863142,52.04315041339102],[4.247859077457536,52.55477055878],[4.245686996192526,52.0429835881638],[4.248005163933253,52.0417095523282]
                        ]
                    }
                }
            }
        },

        "leidschendam":  {
            "aggs": {
                "voertuigen": {
                    "aggs": {
                        "voertuig": {
                            "top_hits": {
                                "_source": {
                                    "include": [
                                        "vehiclenumber",
                                        "vehicle"
                                    ]
                                },
                                "size": 1,
                                    "sort": [
                                    {
                                        "vehicle": {
                                            "order": "desc"
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    "terms": {
                        "field": "vehiclenumber",
                            "size": 1000
                    }
                }
            },
            "filter": {
                "geo_polygon": {
                    "location": {
                        "points": [
                            [
                                4.384352450935001,
                                52.0755324297929
                            ],
                            [
                                4.38759433661099,
                                52.07304412060265
                            ],
                            [
                                4.38788518967772,
                                52.07319621402583
                            ],
                            [
                                4.384686686601944,
                                52.07570798521042
                            ],
                            [
                                4.384352450935001,
                                52.0755324297929
                            ]
                        ]
                    }
                }
            }
        }
    }
}
