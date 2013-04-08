import netsnmp
import smtplib

class SNMPDevice( object ):

   def __init__(self, host, version, user, name, level=None, \
                auth_proto=None, auth_pass=None, priv_pass=None):

      self.host       = host
      self.version    = version
      self.level      = level
      self.name       = name
      self.auth_proto = auth_proto
      self.auth_pass  = auth_pass
      self.priv_pass  = priv_pass
      self.user       = user

   def processOID(self, oid):
      process = netsnmp.Varbind(oid)
      result  = netsnmp.snmpget(oid,
                                Version   = self.version,
                                DestHost  = self.host,
                                Community = self.user)

      return result

   def getName(self):
      return self.name

   def getHost(self):
      return self.host

   def getDeviceByHost(self, host):
      if self.getHost() == host:
         return self
      else:
         return None

   def __str__(self):
      return "%s [%s]" % (self.name, self.host)
