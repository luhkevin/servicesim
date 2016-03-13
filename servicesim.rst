[Nodes]
A,3,latency=0.5,status=404_<percentage we see this status code>,status=500_<...>,payload=<file|string>,action=<custom server-side method to call>
B,4
C,5
D,1
E,2

[Links]
E-A
E-C
C-A
A-B
B-D

[Clients]
E,D,...

* Where to insert load balancers
[LB]
C|ALL
E|A
E|C

* Also have a "controller" endpoint with a REST API exposed which we can use to control each node
* E.g. GET /controller/A?latency=0.5&status=404_50 .... or Have a POST endpoint with JSON data
