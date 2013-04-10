#!/bin/bash

##########################################################
#   FIREWALL CABEZZALAN                                  #
#   Guido Accardo <gaccardo@gmail.com>                   #
#                                                        #
#   CLIENTE                                              #
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

##########################################################
#   CONFIGURACIONES INTERNAS ¡¡¡NO MODIFICAR!!!          #
##########################################################
# Ejecutable
T="/sbin/iptables"
T6="/sbin/ip6tables"

# Mostrar todo
VERBOSE="1"

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

function blame() {
  fecha=$(date)
  echo "$fecha CABEZZALAN FIREWALL: $1" >> /var/log/syslog
}

function check() {
    result=0

    if [ ! -d "/etc/firewall" ]; then
      result=$(result+1)
    fi

    if [ ! -f "/etc/firewall/firewall" ]; then
      result=$(result+1)
    fi

    if [ ! -f "/etc/init.d/firewall" ]; then
      result=$(result+1)
    fi

    if [ ! -f "/etc/rc2.d/S99firewall" ]; then
      result=$(result+1)
    fi

    return $result
}

if [ "$VERBOSE" = "1" ]; then
  echo "##################"
  echo "#    FIREWALL    #"
  echo "##################"
fi

whoami=$(whoami)

if [ ! "$whoami" == "root" ]; then
  echo "Debes ser root para correr el firewall"
  exit
fi

##########################################################
#   DEFINICIONES DEL USUARIO                             #
##########################################################
# Puertos TCP que ingresan de cuaquier source
tcp_input="80 8000 8080"

# Puertos UDP que ingresan de cuaquier source
udp_input=""


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
        #   LIMPIEZA                                     #
        ##################################################
        msg "Limpieza de antiguas reglas"
        $T -F INPUT
        $T -F FORWARD
        $T -F PREROUTING -t nat
        $T -F POSTROUTING -t nat
        dot

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
        # input
        msg "Política INPUT DROP"
        $T -P INPUT DROP
        dot

        # forward
        msg "Política FORWARD DROP"
        $T -P FORWARD DROP
        dot

        ##################################################
        #   LOG                                          #
        ##################################################
        $T -A INPUT -p tcp --dport 22 -j LOG --log-prefix "SSH:" --log-level 1

        ##################################################
        #   INPUT                                        #
        ##################################################

        # Desde localhost se puede ver el proceso web2py
        #msg "Acceso local a web2py"
        #$T -A INPUT -s 127.0.0.1 -p tcp --dport 8000 -j ACCEPT
        #dot

        # Estados NO NEW tienen permiso completo
        msg "ESTABLISHED RELATED PARA TODO EL MUNDO"
        $T -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
        dot

        # Busco todos los puertos TCP que entran de cualquier source
        msg "Puertos TCP que pueden entrar"
        msg "    -----------------------------"
        msg "    $tcp_input"
        msg "    -----------------------------"
        for port in $tcp_input; do
          $T -A INPUT -p tcp --dport $port -j ACCEPT
          dot
        done

        # Busco todos los puertos UDP que entran de cualquier source
        msg "Puertos UDP que pueden entrar"
        msg "    -----------------------------"
        msg "    $udp_input"
        msg "    -----------------------------"
        for port in $udp_input; do
          $T -A INPUT -p udp --dport $port -j ACCEPT
          dot
        done

        echo "OK"
        ##################################################
        #   IPv6                                         #
        ##################################################
        echo "IPv6 FIREWALL (Iniciando): "

        ##################################################
        #   LIMPIEZA                                     #
        ##################################################
        msg "Limpieza de antiguas reglas IPv6"
        $T6 -F INPUT
        $T6 -F FORWARD
        dot
        # input
        msg "IPv6 Política INPUT DROP"
        $T6 -P INPUT DROP
        dot

        # forward
        msg "IPv6 Política FORWARD DROP"
        $T6 -P FORWARD DROP
        dot

        ##################################################
        #   INPUT                                        #
        ##################################################
        msg "Estados ESTABLISHED RELATED permitidos"
        $T6 -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
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
        #   LIMPIEZA                                     #
        ##################################################
        msg "Limpieza de antiguas reglas"
        $T -F INPUT
        $T -F FORWARD
        $T -F PREROUTING -t nat
        $T -F POSTROUTING -t nat
        dot

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

        ##################################################
        #   IPv6                                         #
        ##################################################
        echo "IPv6 FIREWALL (Frenando): "

        ##################################################
        #   LIMPIEZA                                     #
        ##################################################
        msg "Limpieza de antiguas reglas IPv6"

        $T -F INPUT
        $T -F FORWARD
        dot

        ##################################################
        #   POLITICAS                                    #
        ##################################################
        # input
        msg "Política IPv6 INPUT ACCEPT"
        $T -P INPUT ACCEPT
        dot

        # forward
        msg "Política IPv6 FORWARD ACCEPT"
        $T -P FORWARD ACCEPT
        dot

        echo "OK"
}
### / STOP

### MAIN
case $1 in

  start)
    check

    if [ "$?" -gt "0" ]; then
      echo "El sistema debe ser instalado"
      exit
    fi

    start
    touch /var/run/firewall.lock
    blame "start"
  ;;

  stop)
    check

    if [ "$?" -gt "0" ]; then
      echo "El sistema debe ser instalado"
      exit
    fi

    stop
    rm /var/run/firewall.lock
    blame "stop"
  ;;

  restart)
    check

    if [ "$?" -gt "0" ]; then
      echo "El sistema debe ser instalado"
      exit
    fi

    stop
    start
    blame "restart"
  ;;

  install)
    if [ ! -d "/etc/firewall" ]; then
      echo "Creando directorio del firewall"
      mkdir /etc/firewall
    fi

    if [ ! -f "/etc/firewall/firewall" ]; then
        echo "Copiando binario"
        cp ./firewall /etc/firewall/
    fi

    if [ ! -f "/etc/init.d/firewall" ]; then
      echo "Copiando firewall a init.d"
      cp /etc/firewall/firewall /etc/init.d/firewall
    fi

    if [ ! -f "/etc/rc2.d/S99firewall" ]; then
      echo "Creando enlace para arranque con el sistema"
      ln -s /etc/init.d/firewall /etc/rc2.d/S99firewall
    fi
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
### / MAIN

