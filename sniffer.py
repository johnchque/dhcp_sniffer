from pydhcplib.dhcp_network import *
from pydhcplib.type_ipv4 import ipv4
from pydhcplib.type_hw_addr import hwmac
from pydhcplib.type_strlist import strlist
from time import gmtime, strftime
import pymysql

netOpt = {'client_listen_port': "68",
          'iface': 'eth0',
          'server_listen_port': "67",
          'listen_address': "0.0.0.0"
          }


conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='r00t')
cur = conn.cursor()

cur.execute("DROP DATABASE IF EXISTS sniffer")
cur.execute("CREATE DATABASE sniffer")
cur.execute("USE sniffer")
cur.execute(
    "CREATE TABLE data (id INT(6) AUTO_INCREMENT PRIMARY KEY, name NVARCHAR(50), mac NVARCHAR(50), ip NVARCHAR(50), date DATE, time TIME)")


class Server(DhcpServer):

    def __init__(self, options):
        DhcpServer.__init__(self,
                            options["listen_address"],
                            options["client_listen_port"],
                            options["server_listen_port"]
                            )

    def HandleDhcpDiscover(self, packet):
        print 'discover'
        print strlist(packet.GetOption('host_name'))
        print hwmac(packet.GetHardwareAddress())

    def HandleDhcpRequest(self, packet):
        print 'New Request: ' + ipv4(packet.GetOption('request_ip_address')).str()
        print strlist(packet.GetOption('host_name'))
        print hwmac(packet.GetHardwareAddress())
        print ipv4(packet.GetOption('request_ip_address'))
        time = strftime("%H:%M:%S", gmtime())
        date = strftime("%Y-%m-%d", gmtime())
        cur.execute(
            "INSERT INTO data(name,mac,ip,date,time) VALUES ('" + strlist(
                packet.GetOption('host_name')).str() + "','" + hwmac(
                packet.GetHardwareAddress()).str() + "','" + ipv4(
                packet.GetOption('request_ip_address')).str() + "','" + date + "','" + time + "');")
        print "INSERT INTO data(name,mac,ip,date,time) VALUES ('" + strlist(
                packet.GetOption('host_name')).str() + "','" + hwmac(
                packet.GetHardwareAddress()).str() + "','" + ipv4(
                packet.GetOption('request_ip_address')).str() + "','" + date + "','" + time + "');"
        conn.commit()

    def HandleDhcpDecline(self, packet):
        print 'decline'
        print packet.str()

    def HandleDhcpRelease(self, packet):
        print 'release'
        print packet.str()

    def HandleDhcpInform(self, packet):
        print 'inform'
        print packet.str()

server = Server(netOpt)

while True:
    server.GetNextDhcpPacket()
