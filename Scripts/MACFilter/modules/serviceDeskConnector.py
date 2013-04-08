#!/usr/bin/env python
# coding: utf8
#from gluon import *
import MySQLdb
import sys
import time

__version__   = "1.0"
__author__    = "Guido Accardo <gaccardo@coresecurity.com>"
__license__   = "CORE"
__copyright__ = "Core Security Technologies"


class serviceDeskConnector:
    """
    Conexion con la base de datos del service desk y guardar los datos
    validos en la base de datos locales
    """

    def __init__(self):
	db_hd         = dict()
	db_hd['host'] = '127.0.0.1'
	db_hd['port'] = 33366
	db_hd['user'] = 'root'
	db_hd['pass'] = ''
	db_hd['name'] = 'servicedesk'

	db_lo         = dict()
	db_lo['host'] = '127.0.0.1'
	db_lo['user'] = '_macfilter'
	db_lo['pass'] = 'PassworD2010'
	db_lo['name'] = 'macfilter'

	self.db_hd    = db_hd
	self.db_lo    = db_lo

        self.__log  = list()
	self.__flog = "/tmp/macfilter.log"

    def __fileLogger(self, srt):
        """
        Agregar informacion al archivo de logs
        """
        file = open(self.__flog, 'a')
        file.write("MACFILTER :: %s ::> %s\n" % (time.asctime(), srt))
        file.close()

    def __logger(self, str):
        """
        Agregar una línea al log, la cual sera mostrada como resultado en la web

        @param str: Linea a guardar

        @type str: string
        """
        self.__log.append( str )

    def getLog(self):
        """
        Obtener todos los logs hasta el momento

        @return: list
        """ 
        return self.__log

    def doConnectionServiceDesk(self):
        """
        Conectarse a la base de datos del service desk

        @return: MySQLdb.connection
        """
	db_hd = self.db_hd
	link  = MySQLdb.connect(host=db_hd['host'], user=db_hd['user'], db=db_hd['name'], port=db_hd['port'])

	return link

    def doConnectionMacfilter(self):
        """
        Conectarse a la base de datos local

        @return: MySQLdb.connection
        """
	db_lo = self.db_lo
	link  = MySQLdb.connect(host=db_lo['host'], user=db_lo['user'], db=db_lo['name'], passwd=db_lo['pass'])

	return link

    def getEsquemaId(self, name):
        """
        Dado el nombre de un esquema, devolver su id

        @param name: Nombre del esquema a recuperar su id

        @type name: string

        @return: integer
        """
	link   = self.doConnectionMacfilter()
	cursor = link.cursor()
	cursor.execute("SELECT id FROM esquema WHERE name='%s'" % name)
	esquema_id = cursor.fetchone()

	cursor.close()
	link.close()

	return int(esquema_id[0])

    def getVlanId(self, vlan, esquema):
        """
        Dados el nombre de la vlan y el id del esquema, obtener el id de la vlan

        @param vlan: nombre de la vlan
        @param esquema: id del esquema

        @type vlan: string
        @type esquema: integer

        @return: integer
        """
	link   = self.doConnectionMacfilter()
	cursor = link.cursor()
	cursor.execute("""SELECT id FROM vlan WHERE name='%s' and esquema='%s'""" % (vlan, esquema))
	result = cursor.fetchone()

	cursor.close()
	link.close()

	return int(result[0])

    def getUsersMacfilter(self):
        """
        Obtener todos los usuarios guardados en la base de datos local

        @return: list
        """
	link   = self.doConnectionMacfilter()
	cursor = link.cursor()
	cursor.execute("""SELECT d.name, d.mac, v.name, e.name FROM device d, vlan v, esquema e WHERE d.vlan=v.id AND v.esquema=e.id AND (v.name='700' OR v.name='702')""")
	result = cursor.fetchall()

	cursor.close()
	link.close()

	return result

    def getUsersWithMac(self):
        """
        Obtenet todos los usuarios del service desk que tengan al menos una mac address en su perfil

        @return: list
        """
	link   = self.doConnectionServiceDesk()
	cursor = link.cursor()
	final  = list()

        cursor.execute("""SELECT aaaUser.FIRST_NAME "User",regionDef.REGIONNAME "Region",resFields.UDF_CHAR10 "WiFi MAC Address" 
                          FROM Resources resource 
                          LEFT JOIN ResourceOwner rOwner ON resource.RESOURCEID=rOwner.RESOURCEID 
                          LEFT JOIN ResourceAssociation rToAsset ON rOwner.RESOURCEOWNERID=rToAsset.RESOURCEOWNERID 
                          LEFT JOIN SDUser sdUser ON rOwner.USERID=sdUser.USERID 
                          LEFT JOIN AaaUser aaaUser ON sdUser.USERID=aaaUser.USER_ID 
                          LEFT JOIN ResourceLocation resLocation ON resource.RESOURCEID=resLocation.RESOURCEID 
                          LEFT JOIN RegionDefinition regionDef ON resLocation.REGIONID=regionDef.REGIONID 
                          LEFT JOIN Resource_Fields resFields ON resource.RESOURCEID=resFields.RESOURCEID ORDER BY 3""")

	result = cursor.fetchall()

	for user in result:
	    if user[1] == "Argentina":
                new_user = (user[0], user[2], "AR-Buenos Aires")

                final.append(new_user)
            elif user[1] == "USA":
                new_user = (user[0], user[2], "US-Boston")

                final.append(new_user)
            else:
                continue

	cursor.close()
	link.close()

	return final

    def evalUsersToAdd(self):
        """
        Analiza si los usuario deben ser agregados y a que vlan y los devuelve

        @return: list
        """
	hd = self.getUsersWithMac()
	lo = self.getUsersMacfilter()

	users_to_add = list()

	# ('740', 'Marcelino Campos', 'F04D.A285.1DA4', 'F04D.A285.1986', 'AR-Buenos Aires') :: ('Guido Accardo', '001d.098b.ea46', '702', 'AR-Buenos Aires')

	for u_hd in hd:
	    coincidencia_wifi  = 0
	    coincidencia_wired = 0

	    for u_lo in lo:
		if   u_hd[2] == u_lo[1]:
		    coincidencia_wifi  += 1
		elif u_hd[3] == u_lo[1]:
		    coincidencia_wired += 1

	    if coincidencia_wifi  == 0:
		users_to_add.append((u_hd[1],u_hd[2],u_hd[4]))

	    if coincidencia_wired == 0:
		users_to_add.append((u_hd[1],u_hd[3],u_hd[4]))

	return users_to_add

    def evalUsersToAddV2(self):
        new_users    = self.getUsersWithMac()
        users_to_add = list()

        for user in new_users:
            if user[1] != '' and user[1] != None:
                users_to_add.append(user)

        return users_to_add
	 
    def addUsersToMacfilter(self, sync=None):
        """
        Luego de evaluar que movimientos de usuarios realizar, los realiza. 
        """
	new_users = self.evalUsersToAddV2()
	link      = self.doConnectionMacfilter()
	cursor    = link.cursor()

        cursor.execute("""DELETE FROM device WHERE vlan='1' or vlan='2' or vlan='3' or vlan='4'""")

	if sync:
	    cursor.execute("""SELECT id, name, mac, vlan FROM device WHERE vlan != '1' AND vlan != '2' AND vlan != '3' AND vlan != '4'""")

	    no_auto = cursor.fetchall()

	    print "Buscando vlans no automáticas y agregandolas a vlan 700"
            self.__fileLogger("Buscando vlans no automáticas y agregandolas a vlan 700")
	    for na in no_auto:
		cursor.execute("""SELECT e.name FROM vlan v, esquema e WHERE e.id=v.esquema AND v.id='%s'""" % (int(na[3])))
                print """SELECT e.name FROM vlan v, esquema e WHERE e.id=v.esquema AND v.id='%s'""" % (int(na[3]))
                self.__fileLogger("""SELECT e.name FROM vlan v, esquema e WHERE e.id=v.esquema AND v.id='%s'""" % (int(na[3])))
		vlan_where = cursor.fetchone()
		vlan_where = vlan_where[0]

		cursor.execute("""SELECT v.id FROM vlan v WHERE v.esquema='%s' AND v.name='700'""" % self.getEsquemaId(vlan_where))
                print """SELECT v.id FROM vlan v WHERE v.esquema='%s' AND v.name='700'""" % self.getEsquemaId(vlan_where)
                self.__fileLogger("""SELECT v.id FROM vlan v WHERE v.esquema='%s' AND v.name='700'""" % self.getEsquemaId(vlan_where))
		vlan_where = cursor.fetchone()
		vlan_where = int(vlan_where[0])

	    	cursor.execute("""INSERT INTO device (name, mac, vlan) VALUES ('%s','%s','%s')""" %  (na[1],na[2],vlan_where))
		print """INSERT INTO device (name, mac, vlan) VALUES (''%s','%s','%s')""" %  (na[1],na[2],vlan_where)
                self.__fileLogger("""INSERT INTO device (name, mac, vlan) VALUES (''%s','%s','%s')""" %  (na[1],na[2],vlan_where))
                self.__logger("""INSERT INTO device (name, mac, vlan) VALUES (''%s','%s','%s')""" %  (na[1],na[2],vlan_where))

  	for n_user in new_users:
	    idd         = self.getEsquemaId(n_user[2])
	    vlan_700_id = self.getVlanId("700", idd)
	    vlan_702_id = self.getVlanId("702", idd)

	    if n_user[1] != '':
	        print "INSERT INTO device (name, mac, vlan) VALUES ('%s', '%s', '%s')" % (n_user[0], n_user[1], vlan_700_id)
	        print "INSERT INTO device (name, mac, vlan) VALUES ('%s', '%s', '%s')" % (n_user[0], n_user[1], vlan_702_id)

                self.__logger("INSERT INTO device (name, mac, vlan) VALUES ('%s', '%s', '%s')" % (n_user[0], n_user[1], vlan_700_id))
                self.__logger("INSERT INTO device (name, mac, vlan) VALUES ('%s', '%s', '%s')" % (n_user[0], n_user[1], vlan_702_id))

                self.__fileLogger("INSERT INTO device (name, mac, vlan) VALUES ('%s', '%s', '%s')" % (n_user[0], n_user[1], vlan_700_id))
                self.__fileLogger("INSERT INTO device (name, mac, vlan) VALUES ('%s', '%s', '%s')" % (n_user[0], n_user[1], vlan_702_id))

	        cursor.execute("""INSERT INTO device (name, mac, vlan) VALUES ("%s", "%s", %s)""" % (n_user[0], n_user[1], vlan_700_id))
	        cursor.execute("""INSERT INTO device (name, mac, vlan) VALUES ("%s", "%s", %s)""" % (n_user[0], n_user[1], vlan_702_id))

	cursor.close()
	link.commit()
	link.close()

    def deleteUsersNotInHD(self):
        """
        Borrar todos los usuario para volver a crearlos
        """
	self.addUsersToMacfilter(sync=True)
