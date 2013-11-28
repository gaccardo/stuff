#!/usr/bin/env python
 
from couchbase import Couchbase
from couchbase.views.iterator import Query, View

cb = Couchbase.connect(bucket='default')
q = Query()
q.mapkey_range = ['10.0.0.1', '10.0.0.1' + Query.STRING_RANGE_END]
#
q.limit = 100

#print cb.query("access", "accesses", query=q, include_docs=True)

store = dict()
store["store"] = list()

for result in View(cb, "traffic", "miss_traffic_by_ip", query=q):
	store["store"].append(result.value)

print store