# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

from serviceDeskConnector import serviceDeskConnector
from sshToApsManager import sshToApsManager

auth.settings.on_failed_authorization=URL(r=request,f='error')
T.force('es-es')

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    return dict(message=T('Hello World'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def checkInfo(args):
    if args[1] == "vlan":
        if request.vars.has_key('name'):
            if request.vars.name != "700" and request.vars.name != "702":
                print "La vlan está bien"
    	        vlan_exists = db( (db.vlan.name==request.vars.name) & (db.vlan.esquema==request.vars.esquema) ).select()
    
	        if len(vlan_exists) == 0:
		    print "Nombre: %s, esquema: %s, vlan_exists: %s" % (request.vars.name, request.vars.esquema, len(vlan_exists))
	        else:
		    session.flash = "The vlan already exists, it wasn't created"
		    redirect(URL('index'))
	    else:
	        session.flash = "Vlans 700 and 702 can't be modified or created by hand"
	        redirect(URL('index'))


@auth.requires_login()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id[
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    crud.settings.create_next = URL('index')
    crud.settings.delete_next = URL('index')
    crud.settings.update_next = URL('index')
    print "ARGS: %s" % request.args

    crud.settings.create_onvalidation = checkInfo(request.args)

    return dict(form=crud())

# My methods

@auth.requires_login()
def listEsquemas():
    result = db( db.esquema ).select()
    return dict(result=result)

@auth.requires_login()
def listAps():
    result = db( db.ap.esquema == db.esquema.id ).select(orderby=db.ap.esquema)
    return dict(result=result)

@auth.requires_login()
def listVlans():
    result = db( db.vlan.esquema == db.esquema.id ).select(orderby=db.vlan.esquema)
    return dict(result=result)

"""
def listDevices():
    result = db( (db.device.vlan == db.vlan.id) & (db.vlan.esquema == db.esquema.id) ).select(orderby=db.vlan.id)
    return dict(result=result)
"""

@auth.requires_login()
def listDevices(rr=None):
    if len(request.args):
	page = int(request.args[0])
    else:
	page = 0

    items_per_page = 20
    for_quantity   = db( (db.device.vlan == db.vlan.id) & (db.vlan.esquema == db.esquema.id) ).select()
    quantity       = len(for_quantity)
    pages          = quantity / items_per_page

    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    rows    = db( (db.device.vlan == db.vlan.id) & (db.vlan.esquema == db.esquema.id) ).select(orderby=db.vlan.id,limitby=limitby)
    return dict(rows=rows, page=page, items_per_page=items_per_page,quantity=pages)

@auth.requires_login()
def syncker():
    service      = serviceDeskConnector()
    apsconnector = sshToApsManager()

    service.deleteUsersNotInHD()
    service.addUsersToMacfilter()
    service_log = service.getLog()

    apsconnector.doSync()

    response.flash = "Usuarios Sincronizados"

    return dict(service_log=service_log)

@auth.requires_login()
def resumen():
    vlans = db( (db.vlan.id>0) & (db.vlan.esquema==db.esquema.id) ).select()
    result = list()

    for vlan in vlans:
        dev = db( db.device.vlan==vlan.vlan.id ).select()
        result.append({vlan.vlan.name+' '+str(vlan.esquema.name):len(dev)})

    return dict(result=result)

@auth.requires_login()
def findDevices():
    if len(request.args):
	page = int(request.args[0])
    else:
	page = 0

    items_per_page = 10
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    rows = db( (db.device.vlan == db.vlan.id) & (db.vlan.esquema == db.esquema.id) ).select(orderby=db.vlan.id,limitby=limitby)
    return dict(rows=rows, page=page, items_per_page=items_per_page)

def error():
    return dict()

@auth.requires_login()
def buscar():
    if request.vars.buscar is not "":
        devices = db( (db.device.name.contains(request.vars.buscar))).select()
    else:
        devices = []

    return dict(devices=devices)
