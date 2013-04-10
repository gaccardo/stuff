#!/bin/bash
### BEGIN INIT INFO
# Provides:          WowzaMediaServer
# Required-Start:    $local_fs $remote_fs $network $syslog
# Required-Stop:     $local_fs $remote_fs $network $syslog
# Default-Start:     
# Default-Stop:      
# X-Interactive:     true
# Short-Description: Start/stop Wowza Media Server
### END INIT INFO

##########################################################
#   FIREWALL                                             #
#   Guido Accardo <gaccardo@gmail.com>                   #
#                                                        #
##########################################################

##########################################################
# Instrucciones                                          #
##########################################################
# * Para mostrar un mensaje en modo verbose:
#   msg "MENSAJE"
#
# * Para mostrar los puntos en modo NO verbose:
#   dot
#
#   Siempre que se ponga una regla debe tratar de ponerse
# un msg explicando brevemente que se hace en forma de 
# comentario y una llamada a msg en caso de correr el
# script como verbose
##########################################################
VERBOSE="1" # 1 -> Log de todo lo que se hace por STDOUT
            # 0 -> No muestra nada

##########################################################
#   CONFIGURACIONES INTERNAS ¡¡¡NO MODIFICAR!!!          #
##########################################################
# Ejecutables
T="iptables"
T6="ip6tables"
C="tc"

whoami=$(whoami)

function msg() {
  if [ "$VERBOSE" = "1" ]; then
    echo "  *" $1
  fi
}

function dot() {
  if [ "$VERBOSE" != "1" ]; then
    echo -n "..."
  fi
}

function check() {
	result=0
        archivos="/etc/firewall/fire-dmz /etc/firewall/fire-allowed_low /etc/firewall/fire-allowed /etc/firewall/fire-allowed_proxy  /etc/firewall/fire-layer_7 /etc/firewall/fire-allowed_min"

        for file in $archivos; do
                if [ ! -f $file ]; then
			result=$((result+1))
		fi
	done

	return $result
}

function loaddata() {
  ## Cadena con las IPs habilitadas para navegar
  # String with ip able to go out
  # Esta va con mack
  NAVEGAN_DMZ=$(cat /etc/firewall/fire-dmz)
  NAVEGAN_LEVE=$(cat /etc/firewall/fire-allowed_low)
  NAVEGAN=$(cat /etc/firewall/fire-allowed)
  NAVEGAN_PROXY=$(cat /etc/firewall/fire-allowed_proxy)
  NAVEGAN_QUEUE=$(cat /etc/firewall/fire-layer_7)
  MINIMOS=$(cat /etc/firewall/fire-allowed_min)
}

function blame() {
  fecha=$(date)
  echo "$fecha FIREWALL: $1" >> /var/log/syslog
}

if [ "$VERBOSE" = "1" ]; then
  echo "####################"
  echo "#    FIREWALL      #"
  echo "####################"
fi

if [ ! "$whoami" == "root" ]; then
  echo "Debes ser root para correr el firewall"
  exit
fi

##########################################################
#   DEFINICIONES DEL USUARIO                             #
##########################################################
# Puertos NO bloqueados de acceso al servidor externo
PORTS_WAN_ACCEPT_TCP="1194,80"
PORTS_WAN_ACCEPT_UDP="1194"

# Puertos bloqueados de acceso al servidor desde la vpn
PORTS_VPN_ACCEPT_TCP="22,80,1194"
PORTS_VPN_ACCEPT_UDP="1194"

# Puertos habilitados desde afuera y hacia afuera para las virtuales
VIR_PORTS_TCP_WAN="53,80"
VIR_PORTS_UDP_WAN="53"

# Interfaces de red
IF_WAN=""    # Internet
IF_LAN=""    # LAN
LO="lo"      # Localhost

# Permits puertos IPv6
I6_TCP_PORTS="22 80"
I6_UDP_PORTS=""

### START

function start() {
##########################################################
#   INICIO DEL FIREWALL                                  #
##########################################################
        ##################################################
        #   IPv4                                         #
        ##################################################

        echo "FIREWALL (Iniciando): "

        ##################################################
        #   SYSCTL                                       #
        ##################################################
        # Forwarding entre interfaces
        msg "DESACTIVO de forwarding entre interfaces"
        echo "0" > /proc/sys/net/ipv4/ip_forward
        dot

        msg "ACTIVO Protección contra IP Spoofing"
        echo "1" > /proc/sys/net/ipv4/conf/all/rp_filter
        dot

        msg "ACTIVO Log de ips malformadas"
        echo "1" > /proc/sys/net/ipv4/conf/all/log_martians
        dot

        msg "DESACTIVO los redirects"
        echo "0" > /proc/sys/net/ipv4/conf/all/send_redirects
        dot

        msg "DESACTIVO redirects vía ICMP"
        echo "0" > /proc/sys/net/ipv4/conf/all/accept_redirects
        dot

        msg "ACTIVO cookies de conexiones para denegar DoS"
        echo "1" > /proc/sys/net/ipv4/tcp_syncookies
        dot

        msg "DESACTIVO respuestas a ping broadcasts"
        echo "1" > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts
        dot

        msg "ACTIVO Protección para SYN FLOOD atacks"
        echo "1280" > /proc/sys/net/ipv4/tcp_max_syn_backlog # ORIGNAL 512
        dot

        ##################################################
        #   POLITICAS                                    #
        ##################################################
	msg "Políticas DROP"
        $T -P INPUT DROP
        $T -P FORWARD DROP
	dot

        ##################################################
        #   LIMPIEZA                                     #
        ##################################################
        msg "Limpieza de antiguas reglas"
        $T -F
        $T -F -t nat
        $T -F -t mangle
        $T -P FORWARD ACCEPT
        $T -P INPUT ACCEPT
        $T -F navegan
        $T -X navegan
        $T -F navegan_leve
        $T -X navegan_leve
        $T -F navegan_queue
        $T -X navegan_queue
        $T -F ingresan
        $T -X ingresan
        $T -F navegan_min
        $T -X navegan_min
        $T -F proxy_users -t nat
        $T -X proxy_users -t nat
        dot

        ##################################################
        #   CREACION DE NUEVAS TABLAS                    #
        ##################################################
	msg "Creación de nuevas tablas"
        $T -N navegan
        $T -N navegan_leve
        $T -N navegan_queue
        $T -N navegan_min
        $T -N ingresan
        $T -N proxy_users -t nat
	dot

        ##################################################
        #   GLOBALES                                     #
        ##################################################
	msg "Creación de nuevos targets para forward"
	# Mando todo el forward a la cola de navegación
	$T -A FORWARD -j navegan_queue

	# Mando todo el forward a la cola de navegación mínima
        $T -A FORWARD -j navegan_min

	# Mando todo el forward a la cola de navegación ilimitada
        $T -A FORWARD -j navegan

	msg "Definición de QoS"
	# Todas las ips y mac de la lista NAVEGAN_QUEUE se mandan a la cadena
	for ip in $NAVEGAN_QUEUE; do
                $T -A navegan_queue -i $IF_LAN -o $IF_WAN -s ${ip%|*} -m mac --mac-source ${ip#*|} -j NFQUEUE --queue-num 10
        done

	# Aplico la marca 10 a todas las ips de NAVEGAN_QUEUE para que entren en el QoS
	msg "Regla para marca de QoS"
	$T -t mangle -A POSTROUTING -m mark --mark 10 -j DROP
	dot

        ##################################################
        #   INPUT                                        #
        ##################################################
	msg "INPUT"
        # Todo lo que provenga de localhost, se admite
	msg "Todo lo que venga desde localhost es ACCEPT"
        $T -A INPUT -i $LO -j ACCEPT
	dot

	# Lo que esté en la cadena de ingresan
        $T -A INPUT -j ingresan

	# Dejo entrar al cliente y servidor de bacula desde la dmz
	msg "Accesos para bacula"
        $T -A INPUT -i $IF_DMZ -p tcp --dport 9102 -j ACCEPT
        $T -A INPUT -i $IF_DMZ -p tcp --dport 9103 -j ACCEPT

        # Permito reentrada de ping iniciados en el firewall
	msg "No se puede hacer ping al firewall, pero si permito los estados"
        $T -A INPUT -i $IF_WAN -p icmp -m state --state ESTABLISHED,RELATED -j ACCEPT

        # Permito todo trafico de entrada al firewall desde las vm NO dmz
	msg "Acceso ilimitado al firewall desde las vms"
        $T -A INPUT -i venet0 -j ACCEPT

        # Estados permitidos para las conexiones
	msg "ESTABLISHED,RELATED estados aceptados"
        $T -A INPUT -p udp -m state --state ESTABLISHED,RELATED -j ACCEPT
        $T -A INPUT -p tcp -m state --state ESTABLISHED,RELATED -j ACCEPT

        # Habilitacion de pcs minimas
	msg "Configuradas las mínimas ips"
        for ip in $MINIMOS ; do
		# Les dejo ver el puerto 80 del firewall
                $T -A INPUT -i $IF_LAN -s $ip -p tcp --dport 80 -j ACCEPT

		# Entran y salen solo por el 80
                $T -A navegan_min -i $IF_LAN -o $IF_WAN -s $ip -p tcp --dport 80 -j ACCEPT
                $T -A navegan_min -o $IF_LAN -i $IF_WAN -d $ip -p tcp --dport 80 -j ACCEPT
        done

	# LOG de todos los intentos de loguearse al puerto 22 desde internet directamente
	msg "Configurados los logs del puerto 22"
        $T -A INPUT -i $IF_WAN -p tcp --dport 22 -j LOG --log-prefix "SSH EXTERNO Kruzkal" --log-level 4

	# Puertos que pueden accederse desde internet al firewall
	msg "Que puertos entran desde internet"
        $T -A INPUT -p tcp -i $IF_WAN -m multiport --dports $PORTS_WAN_ACCEPT_TCP -j ACCEPT
        $T -A INPUT -p UDP -i $IF_WAN -m multiport --dports $PORTS_WAN_ACCEPT_UDP -j ACCEPT

	# Puertos en que el firewall puede ser accedidos desde la VPN
	msg "Que puertos entran desde la vpn"
        $T -A INPUT -p tcp -i $IF_VPN -m multiport --dports $PORTS_VPN_ACCEPT_TCP -j ACCEPT
        $T -A INPUT -p udp -i $IF_VPN -m multiport --dports $PORTS_VPN_ACCEPT_UDP -j ACCEPT

        # LOG de ssh reincidentes #### REDUNDANTE 
        for ip in $REJECTS ; do
                $T -A INPUT -i $IF_WAN -s $ip -p tcp --dport 22 -j LOG --log-prefix "<SSH> por $ip" --log-level 4
        done

	
        ##################################################
        #   FORWARD                                      #
        ##################################################
	msg "FORWARD"
        # DEJO PASAR EL MUNDO A LA DMZ pero no dejo que la dmz pasa a la intra
	# NAVEGAN_DMZ es una lista con las mac|ips de las maquinas en la dmz.
	# Lo que estas reglas hacen dejar pasar los estados standard
	msg "Configurando ips por mac y que puertos acceden las máquinas de la dmz"
        for ip in $NAVEGAN_DMZ; do
                $T -A FORWARD -s ${ip%|*} -i $IF_DMZ -o $IF_WAN -m mac --mac-source ${ip#*|} -j ACCEPT
                $T -A FORWARD -d ${ip%|*} -o $IF_DMZ -i $IF_WAN -m state --state ESTABLISHED,RELATED -j ACCEPT
                $T -A FORWARD -d ${ip%|*} -o $IF_DMZ -i $IF_WAN -p tcp --match multiport --dports 80,443,53 -j ACCEPT
        done

	# Dejo pasar de la lan a la dmz los puertos 22,80,443 y la vuelta con estados standard
	msg "Estados permitidos a la dmz"
        $T -A FORWARD -s 1.2.3.0/24 -d 10.0.0.0/24 -i $IF_LAN -o $IF_DMZ -p tcp --match multiport --dports 22,80,443 -j ACCEPT
        $T -A FORWARD -s 10.0.0.0/24 -d 1.2.3.0/24 -i $IF_DMZ -o $IF_LAN -m state --state ESTABLISHED,RELATED -j ACCEPT

	# Dejo pasar los estados standard hacia las vm NO dmz
	msg "Estados permitidos a las virtuales"
        $T -A FORWARD -o $IF_VIR -m state --state ESTABLISHED,RELATED -j ACCEPT

	# Puertos permitidos que pasan y salen desde y hacia las vms NO dmz TCP y UDP	
	msg "Puertos permitidos que pasan y salen desde y hacia las vms NO dmz TCP y UDP"
        $T -A FORWARD -i $IF_WAN -o $IF_VIR -p tcp -m multiport --dports $VIR_PORTS_TCP_WAN -j ACCEPT
        $T -A FORWARD -o $IF_WAN -i $IF_VIR -p tcp -m multiport --dports $VIR_PORTS_TCP_WAN -j ACCEPT
        $T -A FORWARD -i $IF_WAN -o $IF_VIR -p udp -m multiport --dports $VIR_PORTS_UDP_WAN -j ACCEPT
        $T -A FORWARD -o $IF_WAN -i $IF_VIR -p udp -m multiport --dports $VIR_PORTS_UDP_WAN -j ACCEPT

	# Paso libre desde la lan a la vpn
	msg "Liberación de la vpn a la lan"
        $T -A FORWARD -i $IF_VPN -o $IF_LAN -j ACCEPT
        $T -A FORWARD -i $IF_LAN -o $IF_VPN -j ACCEPT

        # Forward LAN a VIRTUALES
	msg "Liberación de la vpn a las virtuales"
        $T -A FORWARD -i $IF_VPN -o $IF_VIR    -j ACCEPT
        $T -A FORWARD -i $IF_VIR    -o $IF_VPN -j ACCEPT
	dot

        ##################################################
        #   PREROUTING                                   #
        ##################################################
	msg "PREROUTING"
	# Forwardeo el puerto 8080 directo al nagios desde internet ### ANALIZAR SI SIRVE
	msg "OJO Forwarding de puerto para dejar a nagios accesible desde internet"
        $T -t nat -A PREROUTING -i $IF_WAN -p tcp --dport 8080 -j DNAT --to $NOCLAN

        # VOIP #### ALTAMENTE INSEGURO
        # Conexiones desde afuera al asterisk permitidas 
        #$T -t nat -A PREROUTING -i $IF_WAN -p udp --dport 10000:20000 -j DNAT --to-destination $VOIP_SERVER
        #$T -t nat -A PREROUTING -i $IF_WAN -p udp --dport 5060        -j DNAT --to-destination $VOIP_SERVER
        #$T -t nat -A PREROUTING -i $IF_WAN -p udp --dport 5061        -j DNAT --to-destination $VOIP_SERVER
	dot

        ##################################################
        #   POSTROUTING                                  #
        ##################################################
	msg "POSTROUTING"
	# Masquerade para toda la lan (no incluye virtuales)
	msg "Masquerade para toda la red"
        $T -t nat -A POSTROUTING -o $IF_WAN -j MASQUERADE

        ##################################################
        #   NAVEGAN                                      #
        ##################################################
	msg "NAVEGAN"
        # Navegantes habilitados
	msg "Configurando navegación ilimitada"
        for ip in $NAVEGAN ; do
                # Desde maquinas en la red
                $T -A navegan -i $IF_LAN -s ${ip%|*} -m mac --mac-source ${ip#*|} -j ACCEPT

                # Hacia maquina en la red
                $T -A navegan -i $IF_WAN -d ${ip%|*} -j ACCEPT
        done
	dot

        ##################################################
        #   PROXY USERS                                  #
        ##################################################
	msg "PROXY_USERS"
	msg "Configurando navegación obligatoria por proxy"
	for ip in $NAVEGAN_PROXY ; do
                $T -t nat -A proxy_users -o $IF_WAN -s $ip -p tcp -m multiport --dports 80,443,8080,443 -j REDIRECT --to-port 3128
        done
	dot

        ##################################################
        #   INGRESAN                                     #
        ##################################################
	msg "INGRESAN"
	msg "Configurando ingresantes NO lan"
        for ip in $NAVEGAN ; do
                $T -A ingresan -p tcp -i $IF_LAN -s ${ip%|*} -m multiport --dports 22,80,443,5060,9102,9103,9101,137,139,445 -j ACCEPT
        done
	dot

        ##################################################
        #   MANGLE                                       #
        ##################################################
	msg "MANGLE"
        #PRUEBA PARA BALANCEO DE CARGA
        #$T -t mangle -A POSTROUTING -o eth2 -s 10.0.0.100 -j CLASSIFY --set-class 1:10
        #$T -t mangle -A FORWARD -o $IF_WAN -i $IF_LAN -s 1.2.3.41 -j CLASSIFY --set-class 1:1
        #$T -t mangle -A FORWARD -i $IF_WAN -o $IF_LAN -d 1.2.3.41 -j CLASSIFY --set-class 1:1
        #$T -t mangle -A FORWARD -o $IF_WAN -j CLASSIFY --set-class 1:2

        #$C qdisc add dev $IF_WAN root handle 1: htb default 1
        #$C class add dev $IF_WAN parent 1: classid 1:1 htb rate 10mbit
        #$C class add dev $IF_WAN parent 1: classid 1:2 htb rate 1mbit
	dot

	echo "OK"
}
### / START

### STOP
function stop() {

##########################################################
#   FRENO DEL FIREWALL                                   #
##########################################################
        echo "FIREWALL (Frenando): "

        ##################################################
        #   SYSCTL                                       #
        ##################################################
        # Forwarding entre interfaces
        msg "DESACTIVO forwarding entre interfaces"
        echo "0" > /proc/sys/net/ipv4/ip_forward
        dot

        msg "DESACTIVO Protección contra IP Spoofing"
        echo "1" > /proc/sys/net/ipv4/conf/all/rp_filter
        dot

        msg "DESACTIVO Log de ips malformadas"
        echo "0" > /proc/sys/net/ipv4/conf/all/log_martians
        dot

        msg "ACTIVO redirects"
        echo "1" > /proc/sys/net/ipv4/conf/all/send_redirects
        dot

        msg "ACTIVO redirects vía ICMP"
        echo "1" > /proc/sys/net/ipv4/conf/all/accept_redirects
        dot

        msg "ACTIVO cookies de conexiones para denegar DoS"
        echo "1" > /proc/sys/net/ipv4/tcp_syncookies
        dot

        msg "ACTIVO respuestas a ping broadcasts"
        echo "1" > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts
        dot

        msg "DESACTIVO Protección para SYN FLOOD atacks"
        echo "512" > /proc/sys/net/ipv4/tcp_max_syn_backlog # ORIGNAL 512
        dot

        ##################################################
        #   LIMPIEZA                                     #
        ##################################################
        msg "Limpieza de antiguas reglas"
        $T -F
        $T -F -t nat
        $T -F -t mangle
        $T -P FORWARD ACCEPT
        $T -P INPUT ACCEPT
        $T -F navegan
        $T -X navegan
        $T -F navegan_leve
        $T -X navegan_leve
        $T -F navegan_queue
        $T -X navegan_queue
        $T -F ingresan
        $T -X ingresan
        $T -F navegan_min
        $T -X navegan_min
        $T -F proxy_users -t nat
        $T -X proxy_users -t nat
        dot

        ##################################################
        #   POLITICAS                                    #
        ##################################################
        # input
        msg "Política INPUT ACCEPT"
        $T -P INPUT ACCEPT
        dot

        # forward
        msg "Política FORWARD ACCEPT"
        $T -P FORWARD ACCEPT
        dot

        echo "OK"
}

### / STOP

### INSTALACION
function instalacion() {

        ##################################################
	# INSTALACION                                    #
        ##################################################
	echo "Iniciando instalación:"

	if [ ! -d "/etc/firewall" ]; then
		echo -n "Directorio del firewall no existe: "
		mkdir /etc/firewall
		echo "CREADO"
	fi

	archivos="/etc/firewall/fire-dmz /etc/firewall/fire-allowed_low /etc/firewall/fire-allowed /etc/firewall/fire-allowed_proxy /etc/firewall/fire-layer_7 /etc/firewall/fire-allowed_min"

	echo "Verificando existencia de archivos de configuracion:"
	for file in $archivos; do
		if [ ! -f $file ]; then
			echo "Creando $file"
			touch $file
		fi
	done

	if [ ! -f "/etc/firewall/firewall" ]; then
		cp ./firewall /etc/firewall/firewall
	fi

	if [ ! -f "/etc/init.d/firewall" ]; then
		cp /etc/firewall/firewall /etc/init.d/firewall
		ln -s /etc/init.d/firewall /etc/rc2.d/S99firewall
	fi
}
### / INSTALACION

case $1 in

  start)
    check
    if [ "$?" -gt "0" ]; then
      echo "El sistema debe ser instalado"
      echo "Ejecute: service firewall install"
      exit;
    fi
    loaddata
    start
    touch /var/run/firewall.lock
    blame "start"
  ;;

  stop)
    check
    if [ "$?" -gt "0" ]; then
      echo "El sistema debe ser instalado"
      echo "Ejecute: service firewall install"
      exit;
    fi
    stop
    rm /var/run/firewall.lock
    blame "stop"
  ;;

  restart)
    check
    if [ "$?" -gt "0" ]; then
      echo "El sistema debe ser instalado"
      echo "Ejecute: service firewall install"
      exit;
    fi
    stop
    start
    blame "restart"
  ;;

  install)
    echo "Instalación"
    blame "instalación"
    instalacion 
  ;;

  status)
    if [ -f "/var/run/firewall.lock" ]; then
      echo "CORRIENDO"
    else
      echo "DETENIDO"
    fi
  ;;

  *)
    echo "FIREWALL"
    echo " "
    echo "  start:   Inicia el firewall"
    echo "  stop:    Detiene el firewall"
    echo "  restart: Reinicia el firewall"
    echo "  install: Instala por primera vez el firewall"
    echo "  status:  Indica el estado del firewall"
  ;;

esac
