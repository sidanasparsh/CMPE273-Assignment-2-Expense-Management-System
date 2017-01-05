# Assignment 2 #

Built expense management application to achieve the following:

Dynamic Replica Registration
Dynamic Load Balancing
Failure Detection

## Features:##

### Dynamic Replica Registration ###
* As part of the node registration, whenever an instance of the expense management application will be lauched, it will auto-register to the own instance to the router (proxy server). This is being done through Redis Server:
* Inserted the sever IP in a list created in Redis server whenever the server was run. Implemented it through:
 r = redis.Redis('127.0.0.1', 6379)
 r.rpush('activeServersList', host + ":" + str(port))

### Dynamic Load Balancing ###
* A proxy server has been created to forward the subsequent requests to the applications to its different instances sequentially.
* Implemented Round Robin algorithm to hit the application server instance URL in the list in the Redis server in a sequential manner
### Failure Detection (via CircutBreaker) ###
* Whenever a node reaches its CircuitBreaker's error count, the router should unregister the failed node from the routing table in Redis and forward the same request to the next available node.
* In order to implement this a dictionary was created in CircuitBreaker.py to track the failures per server and remove the server form the Redis list if the server failed more than three times consecutively.
