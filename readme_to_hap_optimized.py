#!/usr/bin/env python3
import re

# Parse readme and dump clean data to a dictionary
configured_hosts = {}
with open('README.md', 'r') as file_handle:
    configuration_data = re.match(r'(?is).*# HAProxy Configuration(?P<conf>.*)', file_handle.read())
    # TODO: cleanup regex match so only matches between ```foo``` within haproxy config section
    # print(configuration_data.groupdict().get('conf'))
    for line in configuration_data.groupdict().get('conf').split("\n"):
        if match := re.match(r'^\s+https://(?P<ingress_host>\S+)/?\s+->\s+http://(?P<destination_service>\S+)\s*$', line):
            destination_service = match.groupdict().get('destination_service')
            ingress_host = match.groupdict().get('ingress_host')
            safe_ingress_host = re.sub(r'\W', '_', ingress_host)
            destination_service += ':80' if not re.match(r'.*:\d+$', destination_service) else ''
            configured_hosts[ingress_host] = {
                'safe_ingress_host': safe_ingress_host,
                'destination_service': destination_service
            }

# print header section
print("""
global
    # intermediate configuration
    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384
    ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
    ssl-default-bind-options prefer-client-ciphers no-sslv3 no-tlsv10 no-tlsv11 no-tls-tickets

    ssl-default-server-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384
    ssl-default-server-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
    ssl-default-server-options no-sslv3 no-tlsv10 no-tlsv11 no-tls-tickets

    # curl https://ssl-config.mozilla.org/ffdhe2048.txt > /path/to/ffdhe2048.txt
    ssl-dh-param-file /etc/ssl/ffdhe2048.txt

defaults
    timeout connect 5000
    timeout client 50000
    timeout server 50000

frontend http_front
    mode http
    bind *:80

    # HSTS (63072000 seconds)
    http-response set-header Strict-Transport-Security max-age=63072000

    # redirects for non www domains:
    redirect scheme https code 302
    
frontend https_front
    mode http
    # path to the combined wildcard stage certificate file
    bind *:443 ssl crt /etc/ssl/private/ alpn h2,http/1.1

    # notify wordpress with header to indicate https connection
    http-request set-header X-Forwarded-Proto https

    # forward requestor ip for security / WordFence
    http-request set-header X-Real-IP %[src]""")

# populate our backend selection directives
for ingress_host in sorted(configured_hosts.keys()):
    safe_ingress_host = configured_hosts[ingress_host].get('safe_ingress_host')
    print(f"""
    acl acl_{safe_ingress_host} hdr_dom(host) -i {ingress_host}
    use_backend {safe_ingress_host}_backend if acl_{safe_ingress_host}""")

# default backend declaration and definition
print("""
    default_backend catchall_backend

backend catchall_backend
    mode http
    http-request deny deny_status 404
""")

# populate backend definitions for configured hosts
for ingress_host in sorted(configured_hosts.keys()):
    print(f"""
backend {configured_hosts[ingress_host].get('safe_ingress_host')}_backend
    mode http
    server only_server {configured_hosts[ingress_host].get('destination_service')} check
""")
