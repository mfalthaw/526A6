import signal
from ..errors import TimeoutExpired

def alarm_handler(signum, frame):
    raise TimeoutExpired()

def input_to(prompt, timeout):
    # set signal handler
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout) # produce SIGALRM in `timeout` seconds

    try:
        return input(prompt)
    finally:
        signal.alarm(0) # cancel alarm
