import psutil
import time

def get_network_usage(interval=1):
    previous = psutil.net_io_counters()
    time.sleep(interval)
    current = psutil.net_io_counters()

    bytes_used = (current.bytes_sent - previous.bytes_sent) + \
                 (current.bytes_recv - previous.bytes_recv)

    return bytes_used

