#!/usr/bin/env bash
set -u
PUBLIC_IP="${1:?usage: ./verify.sh <public-ip>}"

echo "bindings:"
ss -tlnp | grep -E ':(80|8001)'

echo
echo "unmatched Host on public interface:"
curl -s -o /dev/null -w 'http code: %{http_code}\n' \
     -H 'Host: nonsense.test' "http://${PUBLIC_IP}/"

echo
echo "wireguard peers:"
sudo wg show
