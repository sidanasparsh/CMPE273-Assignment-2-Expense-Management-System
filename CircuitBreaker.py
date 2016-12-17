from functools import wraps
from datetime import datetime, timedelta
import redis


class CircuitBreaker(object):
    def __init__(self, name=None, expected_exception=Exception, max_failure_to_open=3, reset_timeout=50):
        self._name = name
        self._expected_exception = expected_exception
        self._max_failure_to_open = max_failure_to_open
        self._reset_timeout = reset_timeout
        # Set the initial state
        self.close()
        self.totalFailuresPerServer = {}

    def close(self):
        self._is_closed = True
        self._failure_count = 0

    def open(self,serverIP):
        self.totalFailuresPerServer[serverIP] = 0
        reddisConn = redis.Redis('localhost')
        reddisConn.lrem('activeServersList', serverIP, num=0)


    def can_execute(self):
        if not self._is_closed:
            self._open_until = self._opened_since + timedelta(seconds=self._reset_timeout)
            self._open_remaining = (self._open_until - datetime.utcnow()).total_seconds()
            return self._open_remaining <= 0
        else:
            return True

    def __call__(self, func, *args, **kwargs):
        if self._name is None:
            self._name = func.__name__
            print "Failure count before is: ",self._failure_count

        @wraps(func)
        def with_circuitbreaker(*args, **kwargs):
            return self.call(func, *args, **kwargs)

        return with_circuitbreaker

    def call(self, func, *args, **kwargs):
        serverIP=args[args.__len__()-1]
        if not self.can_execute():
            err = 'CircuitBreaker[%s] is OPEN until %s (%d failures, %d sec remaining)' % (
                self._name,
                self._open_until,
                self._failure_count,
                round(self._open_remaining)
            )
            raise Exception(err)
        try:
            result = func(*args, **kwargs)
            self.totalFailuresPerServer[serverIP]=0 #setting failure count as 0 as the request got through
         #   print "Failure count after is: ", self.totalFailuresPerServer[serverIP]
        except self._expected_exception:
            self._failure_count += 1
            if serverIP in self.totalFailuresPerServer:
                print serverIP
                self.totalFailuresPerServer[serverIP] +=1 #increasing the failure count y 1.
            else:
                self.totalFailuresPerServer[serverIP]=1 #setting the failure count as 1 for the new server.
            if self.totalFailuresPerServer[serverIP] >= self._max_failure_to_open:
                self.open(serverIP)
            raise self._expected_exception
        self.close()
        return result