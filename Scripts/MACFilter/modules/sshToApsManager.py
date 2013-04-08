#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import os
import pexpect
import time
import sys

__version__   = "1.0"
__author__    = "Guido Accardo <gaccardo@coresecurity.com>"
__license__   = "CORE"
__copyright__ = "Core Security Technologies"

"""
Comunicación con los AP configurados para pasarle los sets de reglas
necesarios para habilitar gente
"""

class AP(object):
    """
    Objecto que describe un ap

    @cvar nombre: Nombre del AP
    @cvar ip: Ip del AP
    @cvar esqeuma: Id del esquema del AP
    @cvar user: Nombre de usuario para conectar al AP
    @cvar passwd: Si se cambiar al usuario proporcionar el passwd

    @requires: MySQLdb, pexpect
    """

    def __init__(self, nombre, ip, esquema, user=None, passwd=None):
        """
        Constructor del objecto

        @param nombre: Nombre del ap, tiene que ser el real del ap en mayúsculas
        @param ip: Ip del ap usada para acceder vía ssh
        @param esquema: Indica el id del registro en la base de datos indicando el esquema
        @param user: Si se tiene que forzar un nuevo usuario para acceder
        @param passwd: Si se fuerza un nuevo usuario DEBE forzarse un nuevo password

        @type nombre: string
        @type ip: string
        @type esquema: integer
        @type user: string or None
        @type passwd: string or None

        """
	self.nombre  = nombre
	self.ip      = ip
	self.esquema = esquema
	self.user    = user
	self.passwd  = passwd

    def __str__(self):
        """
        Si se imprime un objeto directamente se muestran algunos parámetros

        @return: Representación:  AP <nombre> :: <ip> :: <esquema>

        @rtype: string
        """
	return "AP %s :: %s :: %s" % (self.nombre, self.ip, self.esquema)

    def setNombre(self, nombre):
        """
        Cambia nombre del AP

        @param nombre: Setea el nombre del ap

        @type nombre: string
        """
	self.nombre = nombre

    def setIp(self, ip):
        """
        Cambia la ip del AP

        @param ip: Setea la ip del ap

        @type ip: string
        """
	self.ip = ip

    def setEsquema(self, esquema):  
        """
        Cambia el esquema del AP

        @param esquema: Setea el esquema del ap

        @type esquema: string
        """
	self.esquema = esquema

    def setUser(self, user):
        """
        Cambia el usuario del AP

        @param user: Setea el usuario del ap

        @type user: string
        """
	self.user = user

    def setPasswd(self, passwd):
        """
        Cambia el password del AP

        @param passwd: Setea el password del ap

        @type passwd: string
        """
	self.passwd = passwd

    def getNombre(self):
        """
        Obtiene el nombre del ap

        @return: Nombre del ap

        @rtype: string
        """
	return self.nombre

    def getIp(self):
        """
        Obtiene la ip del ap

        @return: Ip del ap

        @rtype: string
        """
	return self.ip

    def getEsquema(self):
        """
        Obtiene el esquema del ap

        @return: Esquema del ap

        @rtype: string
        """
	return self.esquema

    def getUser(self):
        """
        Obtiene el usuario del ap

        @return: Usuario del ap

        @rtype: string
        """
	return self.user

    def getPasswd(self):
        """
        Obtiene el password del ap

        @return: Password del ap

        @rtype: string
        """
	return self.passwd


class sshToApsManager(object):
    """
    Manejador de conexiones a APs del tipo airenet CISCO
    """

    def __init__(self):
	db         = dict()
	db['host'] = "localhost"
	db['user'] = "root"
	db['pass'] = "pepe1234"
	db['data'] = "macfilter"
	self.db    = db

	self.aps = dict()
	self.aps['AR-BuenosAires'] = self.__getApsByEsquema(1)
	self.aps['US-Boston']      = self.__getApsByEsquema(2)

        self.tmpfile = "/tmp/macfilter.tmp"
        self.sleep   = 2 # Sleep time in seconds

    def __doConnection(self):
        """
        Genera una conexion a la base de datos MySQL

        @return: Objeto conexión ya conectado a MySQL 

        @rtype: MySQLdb.connection
        """
	db = self.db
	try:
	    link = MySQLdb.connect(host=db['host'], user=db['user'], passwd=db['pass'], db=db['data'])
	    return link
	except MySQLdb.Error, e:
	    print "Error al crear el connector"
	    print "Error %d: %s" % (e.args[0], e.args[1])

    def __getApsByEsquema(self, esquema):
        """
        Dados un id de esquema devolver todos los aps asociados

        @param esquema: Id del esquema a consultar

        @type esquema: integer

        @return: Lista de todos los aps asociados a un esquema

        @rtype: list
        """
	link   = self.__doConnection()
	cursor = link.cursor()
	r_aps  = list()

	cursor.execute("""SELECT name, ip, esquema, user, passwd FROM ap WHERE esquema='%s'""" % esquema)
	aps = cursor.fetchall()

	cursor.close()
	link.close()

	for ap in aps:
	    r_aps.append( AP(ap[0],ap[1],int(ap[2]),ap[3],ap[4]) )

	return r_aps

    def getAps(self):
        """
        Obtener TODOS los APs dividos por esquema

        @return: Dicionario de listas de aps 

        @rtype: dict
        """
	return self.aps

    def doSync(self):
        """
        Realizar la sincronizacion entre ServiceDesk, APs y DataBase local
        """
	link   = self.__doConnection()
	cursor = link.cursor()

	cursor.execute("""SELECT d.mac, v.name FROM device d, vlan v, esquema e WHERE d.vlan=v.id AND v.esquema=e.id AND e.id=1""")
	devices_bsas = cursor.fetchall()

	cursor.execute("""SELECT d.mac, v.name FROM device d, vlan v, esquema e WHERE d.vlan=v.id AND v.esquema=e.id AND e.id=2""")
	devices_bos = cursor.fetchall()

	for ap in self.aps['AR-BuenosAires']:
            child = pexpect.spawn("ssh adminrancid@%s" % ap.ip)
            print "Sync with AP: " + ap.ip
            child.expect('Password:')
            child.sendline('#$kasdkf$DSAGSDAG454=')
            child.expect('%s>' % ap.nombre)
            child.sendline('en')
            child.expect('Password:')
            child.sendline('MamuchaComoFunc43to')
            child.expect('%s#' % ap.nombre)
            child.sendline('conf t')

	    cursor.execute("""SELECT v.name FROM vlan v""")
	    vlans = cursor.fetchall()

	    for vlan in vlans:
                child.sendline("no access-list %s" % vlan)
                print "no access-list %s" % vlan

	    for dd in devices_bsas + devices_bos:
                child.sendline("access-list %s permit %s 0000.0000.0000" % (dd[1], dd[0]))
                print "access-list %s permit %s 0000.0000.0000" % (dd[1], dd[0])

	    for vlan in vlans:
                child.sendline("access-list %s deny   0000.0000.0000 ffff.ffff.ffff" % vlan)
                print "access-list %s deny   0000.0000.0000 ffff.ffff.ffff" % vlan

            child.sendline("wr")
            child.sendline("\n")

            child.close()

	for ap in self.aps['US-Boston']:
            child = pexpect.spawn("ssh adminrancid@%s" % ap.ip)
            print "Sync with AP: " + ap.ip
            child.expect('Password:')
            child.sendline('#$kasdkf$DSAGSDAG454=')
	
            child.expect('%s>' % ap.nombre)
            child.sendline('en')
            child.expect('Password:')
            child.sendline('MamuchaComoFunc43to')
            child.expect('%s#' % ap.nombre)
            child.sendline('conf t')

	    cursor.execute("""SELECT v.name FROM vlan v WHERE v.esquema='2'""")
	    vlans = cursor.fetchall()

	    for vlan in vlans:
                child.sendline("no access-list %s" % vlan)
                print "no access-list %s" % vlan

	    for dd in devices_bos + devices_bsas:
                child.sendline("access-list %s permit %s 0000.0000.0000" % (dd[1], dd[0]))
		time.sleep(self.sleep)
                print "access-list %s permit %s 0000.0000.0000" % (dd[1], dd[0])

	    for vlan in vlans:
                child.sendline("access-list %s deny   0000.0000.0000  ffff.ffff.ffff" % vlan)
		time.sleep(self.sleep)
                print "access-list %s deny   0000.0000.0000  ffff.ffff.ffff" % vlan

            child.sendline("wr")
            child.sendline("\n")

            child.close()

	cursor.close()
	link.close()
