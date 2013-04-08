from serviceDeskConnector import serviceDeskConnector
a = serviceDeskConnector()
#print a.getUsersWithMac()
for user in a.evalUsersToAddV2():
	print user
#print a.addUsersToMacfilter(sync=True)
