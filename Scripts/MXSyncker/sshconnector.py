#!/usr/bin/env python
import paramiko
import StringIO
import os


class SSHConnector( object ):
       
   def __init__( self ):
      self.local_folder = 'tmp/'

   def executeCommand(self, server, cmd):
      """
      Using server url and username allowed to login, execute cmd
      and return the stdout

      :param server: URL or IP of the **server**
      :param cmd: Command to run in the client, usually a call to authpf client

      :type server: String
      :type cmd: String

      :return: The stdout of the server
      """
      store = StringIO.StringIO()
      ssh   = paramiko.SSHClient()
      ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
      ssh.connect(server.getIP(), username=server.getUsername(), password=None)

      stdin, stdout, stderr = ssh.exec_command(cmd)
      stdin.flush()

      return stdout.readlines(), stderr.readlines()

   def getFile( self, server, remote_file, local_file=None ):
      if local_file is None:
         os.system( "scp %s@%s:%s %s > /dev/null " % ( server.getUsername(), server.getIP(), remote_file, self.local_folder ) )
      else:
         os.system( "scp %s@%s:%s %s/%s > /dev/null " % ( server.getUsername(), server.getIP(), remote_file, self.local_folder, local_file ) )

   def pushFile( self, server, local_file, remote_folder ):
      os.system( "scp %s %s@%s:%s > /dev/null " % ( local_file, server.getUsername(), server.getIP(), remote_folder ) )

