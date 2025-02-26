#!/bin/bash

VPN_SERVER_PUBLIC_IP=""
INTERFACE="eth0"
WG_INTERFACE="wg0"
IPV6_PREFIX="fccc:1337"

sudo apt update && sudo apt install wireguard -y

# Generate WG server config
WG_PRIVKEY=$(wg genkey | sudo tee /etc/wireguard/private.key)
WG_PUBKEY=$(sudo cat /etc/wireguard/private.key | wg pubkey | sudo tee /etc/wireguard/public.key)
sudo chmod go= /etc/wireguard/private.key

echo -n "[Interface]
PrivateKey = ${WG_PRIVKEY}
Address = ${IPV6_PREFIX}::1/64
ListenPort = 51820
SaveConfig = true

PostUp = ufw route allow in on ${WG_INTERFACE} out on ${INTERFACE}
PostUp = iptables -t nat -I POSTROUTING -o ${INTERFACE} -j MASQUERADE
PostUp = ip6tables -t nat -I POSTROUTING -o ${INTERFACE} -j MASQUERADE

# redirect HTTP to port 5000
PostUp = ip6tables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000

PreDown = ufw route delete allow in on ${WG_INTERFACE} out on ${INTERFACE}
PreDown = iptables -t nat -D POSTROUTING -o ${INTERFACE} -j MASQUERADE
PreDown = ip6tables -t nat -D POSTROUTING -o ${INTERFACE} -j MASQUERADE
" | sudo tee /etc/wireguard/${WG_INTERFACE}.conf > /dev/null


# Enable IP forwarding
sudo sed -i -E 's/^.?net.ipv4.ip_forward=.*$/net.ipv4.ip_forward=1/g' /etc/sysctl.conf
sudo sed -i -E 's/^.?net.ipv6.conf.all.forwarding=.*$/net.ipv6.conf.all.forwarding=1/g' /etc/sysctl.conf
sudo sysctl -p > /dev/null

# Start WireGuard
sudo systemctl enable --now wg-quick@${WG_INTERFACE}.service


# Create clients
mkdir ./wg-clients

for IP in {2..10}; do
    IP6=$(printf '%x\n' "$IP")
    PRIV=$(wg genkey)
    PUB=$(echo "$PRIV" | wg pubkey)

    sudo wg set ${WG_INTERFACE} peer "$PUB" allowed-ips "$IPV6_PREFIX"::"$IP6"

    echo -n "[Interface]
PrivateKey = $PRIV
Address = ${IPV6_PREFIX}::${IP6}/64

[Peer]
PublicKey = ${WG_PUBKEY}
AllowedIPs = ${IPV6_PREFIX}::/64
Endpoint = ${VPN_SERVER_PUBLIC_IP}:51820
" > ./wg-clients/client"${IP}".conf
done

tar -czvf wg-clients.tar.gz ./wg-clients > /dev/null
rm -rf ./wg-clients