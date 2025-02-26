# Infra Notes
1. Clone repo, setup Python venv, and follow the setup guide in the main [README](../README.md).
2. Install supervisor and add the [llm-logger.conf](./llm-logger.conf) to the supervisor config folder.
3. Run [wireguard.sh](./wireguard.sh) to setup WireGuard and create client files. Configure ufw as necessary if enabled.
4. Clients: add the WireGuard IP (fccc:1337::1) and a respective hostname to /etc/hosts.

Clients should now be able to view LLM Logger when accessing either http://[fccc:1337::1] or the chosen hostname.