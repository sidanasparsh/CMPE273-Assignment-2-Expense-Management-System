# Assignment 2 #

### Dynamic Replica Registration ###

* Inserted the sever IP in a list created in Redis server whenever the server was run. Implemented it through:
*  r = redis.Redis('127.0.0.1', 6379)
   r.rpush('activeServersList', host + ":" + str(port))

### Dynamic Load Balancing ###

* Implemented Round Robin algorithm to hit the server URL in the list in the Redis server in a sequential manner

### Failure Detection ###

* Implemented failure detection using circuit breaker wrapper through this code:
* Code review
* A dictionary was created in CircuitBreaker.py to track the failures per server and remove the server form the Redis list if the server failed more than three times consecutively.