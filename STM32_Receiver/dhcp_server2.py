import socket
import struct
from datetime import datetime
import threading
import sys
import time

SERVER_IP = '192.168.1.2'
SUBNET_MASK = '255.255.255.0'
GATEWAY = '192.168.1.1'
IP_POOL = [f"192.168.1.{i}" for i in range(3, 256)]
LEASE_TIME = 60 * 5
BINDING = {}
LEASES = {}

DHCP_SERVER_PORT = 67
DHCP_CLIENT_PORT = 68

DHCP_MESSAGE_TYPES = {
    1: 'DISCOVER',
    2: 'OFFER',
    3: 'REQUEST',
    4: 'DECLINE',
    5: 'ACK',
    6: 'NACK',
    7: 'RELEASE',
    8: 'INFORM'
}

running = True

def create_dhcp_packet(message_type, xid, client_mac, yiaddr='', siaddr='', giaddr='', options=None, ciaddr='', flags=0):
    packet = bytearray(240)
    
    packet[0] = 2
    packet[1] = 1
    packet[2] = 6
    packet[3] = 0
    
    packet[4:8] = struct.pack('!I', xid)
    
    packet[8:10] = struct.pack('!H', 0)
    
    packet[10:12] = struct.pack('!H', flags)
    
    if ciaddr:
        packet[12:16] = socket.inet_aton(ciaddr)
    else:
        packet[12:16] = b'\x00\x00\x00\x00'
    
    if yiaddr:
        packet[16:20] = socket.inet_aton(yiaddr)
    if siaddr:
        packet[20:24] = socket.inet_aton(siaddr)
    if giaddr:
        packet[24:28] = socket.inet_aton(giaddr)
    
    packet[28:44] = client_mac.ljust(16, b'\x00')
    
    packet[236:240] = b'\x63\x82\x53\x63'
    
    option_data = bytearray()
    option_data.extend([53, 1, message_type])
    
    if options:
        for opt_type, opt_value in options.items():
            option_data.extend([opt_type, len(opt_value)])
            option_data.extend(opt_value)
    
    option_data.append(255)
    
    packet[240:240+len(option_data)] = option_data
    
    return bytes(packet)

def parse_dhcp_packet(data):
    if len(data) < 240:
        return None
    
    packet = {
        'op': data[0],
        'htype': data[1],
        'hlen': data[2],
        'hops': data[3],
        'xid': struct.unpack('!I', data[4:8])[0],
        'secs': struct.unpack('!H', data[8:10])[0],
        'flags': struct.unpack('!H', data[10:12])[0],
        'ciaddr': socket.inet_ntoa(data[12:16]),
        'yiaddr': socket.inet_ntoa(data[16:20]),
        'siaddr': socket.inet_ntoa(data[20:24]),
        'giaddr': socket.inet_ntoa(data[24:28]),
        'chaddr': data[28:44],
        'options': {}
    }
    
    if data[236:240] == b'\x63\x82\x53\x63':
        options_start = 240
        i = options_start
        while i < len(data):
            opt_type = data[i]
            if opt_type == 255:
                break
            if opt_type == 0:
                i += 1
                continue
            
            opt_len = data[i + 1]
            opt_value = data[i + 2:i + 2 + opt_len]
            packet['options'][opt_type] = opt_value
            i += 2 + opt_len
    
    return packet

def assign_ip(mac):
    mac_str = mac.hex()
    if mac_str in BINDING:
        LEASES[mac_str] = time.time()
        return BINDING[mac_str]
    if IP_POOL:
        ip = IP_POOL.pop(0)
        BINDING[mac_str] = ip
        LEASES[mac_str] = time.time()
        return ip
    return None

def release_ip(mac):
    mac_str = mac.hex()
    if mac_str in BINDING:
        ip = BINDING[mac_str]
        del BINDING[mac_str]
        if mac_str in LEASES:
            del LEASES[mac_str]
        IP_POOL.append(ip)
        IP_POOL.sort()
        print(f"[*] Released IP: {ip} from MAC: {mac.hex()}")
        return True
    return False

def check_expired_leases():
    while running:
        try:
            time.sleep(30)
            current_time = time.time()
            expired_macs = []
            for mac_str, lease_time in LEASES.items():
                if current_time - lease_time > LEASE_TIME:
                    expired_macs.append(mac_str)
            
            for mac_str in expired_macs:
                mac_bytes = bytes.fromhex(mac_str)
                print(f"[!] Lease expired for MAC: {mac_str}")
                release_ip(mac_bytes)
        except:
            break

def main():
    global running
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_socket.bind(('', DHCP_SERVER_PORT))
    
    print(f"DHCP server started on {SERVER_IP}")
    print(f"Listening for DHCP requests...")
    print("Type 'quit' or 'exit' to stop the server")
    print("=" * 50)
    
    def input_listener():
        global running
        while running:
            try:
                cmd = input().strip().lower()
                if cmd in ['quit', 'exit', 'q']:
                    running = False
                    print("\nStopping DHCP server...")
                    break
            except EOFError:
                running = False
                break
    
    input_thread = threading.Thread(target=input_listener, daemon=True)
    input_thread.start()
    
    lease_thread = threading.Thread(target=check_expired_leases, daemon=True)
    lease_thread.start()
    
    try:
        server_socket.settimeout(1.0)
        while running:
            try:
                data, addr = server_socket.recvfrom(1024)
                if not data:
                    continue
                
                packet = parse_dhcp_packet(data)
                if not packet:
                    continue
                
                message_type = packet['options'].get(53)
                if not message_type:
                    continue
                
                message_type = message_type[0]
                client_mac = packet['chaddr'][:6]
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"Received {DHCP_MESSAGE_TYPES.get(message_type, 'UNKNOWN')} "
                      f"from MAC: {client_mac.hex()}")
                
                if message_type == 1:
                    assigned_ip = assign_ip(client_mac)
                    if not assigned_ip:
                        print(f"No IP available for MAC: {client_mac.hex()}")
                        continue
                    
                    response = create_dhcp_packet(
                        message_type=2,
                        xid=packet['xid'],
                        client_mac=client_mac,
                        yiaddr=assigned_ip,
                        siaddr=SERVER_IP,
                        giaddr=GATEWAY,
                        ciaddr=packet['ciaddr'],
                        flags=packet['flags'],
                        options={
                            1: socket.inet_aton(SUBNET_MASK),
                            3: socket.inet_aton(GATEWAY),
                            51: struct.pack('!I', LEASE_TIME),
                            54: socket.inet_aton(SERVER_IP),
                            6: socket.inet_aton('8.8.8.8') + socket.inet_aton('8.8.4.4')
                        }
                    )
                    
                    print(f"Sending OFFER to MAC: {client_mac.hex()}, IP: {assigned_ip} (Broadcast)")
                    server_socket.sendto(response, ('255.255.255.255', DHCP_CLIENT_PORT))
                
                elif message_type == 3:
                    assigned_ip = assign_ip(client_mac)
                    if not assigned_ip:
                        print(f"No IP available for MAC: {client_mac.hex()}")
                        continue
                    
                    response = create_dhcp_packet(
                        message_type=5,
                        xid=packet['xid'],
                        client_mac=client_mac,
                        yiaddr=assigned_ip,
                        siaddr=SERVER_IP,
                        giaddr=GATEWAY,
                        ciaddr=packet['ciaddr'],
                        flags=packet['flags'],
                        options={
                            1: socket.inet_aton(SUBNET_MASK),
                            3: socket.inet_aton(GATEWAY),
                            51: struct.pack('!I', LEASE_TIME),
                            54: socket.inet_aton(SERVER_IP),
                            6: socket.inet_aton('8.8.8.8') + socket.inet_aton('8.8.4.4')
                        }
                    )
                    
                    print(f"Sending ACK to MAC: {client_mac.hex()}, IP: {assigned_ip} (Broadcast)")
                    server_socket.sendto(response, ('255.255.255.255', DHCP_CLIENT_PORT))
                
                elif message_type == 4:
                    print(f"[*] Received DECLINE from MAC: {client_mac.hex()}")
                    release_ip(client_mac)
                
                elif message_type == 7:
                    print(f"[*] Received RELEASE from MAC: {client_mac.hex()}")
                    release_ip(client_mac)
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error processing packet: {e}")
                continue
    
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received")
    finally:
        running = False
        server_socket.close()
        print("DHCP server stopped")

if __name__ == "__main__":
    main()
