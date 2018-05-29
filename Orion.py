import socket
import struct
import textwrap

def main():
    #conn = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.ntohs(3))
    conn = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        raw_data, addr = conn.recvfrom(65536)
        dest_mac,src_mac,eth_proto,data = ethernet_frame(raw_data)
        print('\nEthernet Frame: ')
        print('Destination: {},Source: {}, Protocol: {}'.format_map(dest_mac,src_mac,eth_proto))



def ethernet_frame(data):
    dest_mac,src_mac,proto = struct.unpack('! 6s 6s H', data[:14])
    return get_mac_addr(dest_mac), get_mac_addr(src_mac),socket.htons(proto),data[14:]

def get_mac_addr(bytes_addr):
    bytes_str = map('{:02x}'.format,bytes_addr)
    return ':'.join(bytes_str).upper()

#unpacks IPv4 packet
def ipv4_packet(data):
    version_header_length = data[0]
    version = version_header_length >> 4
    header_length = (version_header_length & 15) * 4
    ttl, proto, src, target = struct.unpack('! 8x B B 2x 4s 4s', data[:20])
    return version, header_length, ttl, proto, ipv4(src), ipv4(target), data[header_length:]

def ipv4(addr):
    return ".".join(map(str, addr))

#unpacks ICMP packet
def icmp_packet(data):
    icmp_type, code, checksum = struct.unpack('! B B H', data[:4])
    return icmp_type, code, checksum, data[4:]

#unpacks TCP segment
def tcp_segment(data):
    (src_part, dest_port, sequence, acknowledgement, offset_reserved_flags) = struct.unpack('! H H L L H', data[:14])
    offset = (offset_reserved_flags >> 12) * 4
    flag_urg = (offset_reserved_flags & 32) >> 5
    flag_ack = (offset_reserved_flags & 16) >> 4
    flag_psh = (offset_reserved_flags & 8) >> 3
    flag_rst = (offset_reserved_flags & 4) >> 2
    flag_syn = (offset_reserved_flags & 2) >> 1
    flag_fin = offset_reserved_flags & 1
    return src_part, dest_port, sequence, acknowledgement, flag_urg, flag_ack, flag_psh, flag_rst, flag_syn, flag_fin, data[offset:]


main()