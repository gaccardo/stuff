#!/usr/bin/env python
 
from couchbase import Couchbase

cb = Couchbase.connect(bucket='default')

result = cb.get("aasdasd:vol-7f7f7:1383678496.23")