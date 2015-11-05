import pylibmc

servers = os.environ.get('MEMCACHIER_SERVERS', '').split(',')
user = os.environ.get('MEMCACHIER_USERNAME', '')
pass = os.environ.get('MEMCACHIER_PASSWORD', '')

mc = pylibmc.Client(servers, binary=True,
        username=user, password=pass,
        behaviors={
            # Faster IO
            "tcp_nodelay": True,
            "no_block": True,

            # Timeout for set/get requests
            "_poll_timeout": 2000,

            # Use consistent hashing for failover
            "ketama": True,

            # Configure failover timings
            "connect_timeout": 2000,
            "remove_failed": 4,
            "retry_timeout": 2,
            "dead_timeout": 10,
            })
