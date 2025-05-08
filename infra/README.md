# Infra Notes
1. Install docker if necessary, and run `docker compose up -d`
2. Run [wireguard.sh](./wireguard.sh) to setup WireGuard and create client files. 
    - Based on your setup, you may need to configure `ufw`
    - ... and you may need to add/modify iptable rules (e.g. `PostUp = ip6tables -A ufw6-user-input -p tcp --dport 80 -j ACCEPT` in wg config).
    - Note: Make sure that your chosen port is not publicly exposed, and only accessible through the VPN interface.
3. Clients: Choose their unique Wireguard file and use it
   - Optionally: add the WireGuard server's internal IP (default is `fccc:1337::1`) and a respective hostname to /etc/hosts.

Clients should now be able to view LLM Logger when accessing either http://[fccc:1337::1] or the chosen hostname.