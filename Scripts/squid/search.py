#!/usr/bin/env python
 
from couchbase import Couchbase
from couchbase.views.iterator import Query, View

cb = Couchbase.connect(bucket='default')
q = Query()
q.mapkey_range = ['http://s2.youtube.com/s?', 'http://s2.youtube.com/s?' + Query.STRING_RANGE_END]
#
q.limit = 100

#print cb.query("access", "accesses", query=q, include_docs=True)

store = dict()
store["store"] = list()

for result in View(cb, "traffic", "miss_traffic_by_domain", query=q):
	store["store"].append(result.value)

print store