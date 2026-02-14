import psutil
import time

def get_network_usage(interval=1):
    prev = psutil.net_io_counters()
    time.sleep(interval)
    curr = psutil.net_io_counters()

    bytes_used = (curr.bytes_sent - prev.bytes_sent) + \
                 (curr.bytes_recv - prev.bytes_recv)

    return bytes_used

