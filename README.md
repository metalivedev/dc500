dc500
=====

Test the behavior of dotCloud Platform handling of 500 and 502 errors.

We often get questions about seeing messages about broken pipes or ``/CloudHealthCheck`` calls, 
and this simple app lets you trigger 200, 500, and 502's at will.

The ``/CloudHealthCheck`` HEAD check will only be triggered [if you scale this service horizontally]
(https://github.com/samalba/hipache-hchecker/blob/master/hchecker.go#L30). Then you'll see it appear
in the access logs.
