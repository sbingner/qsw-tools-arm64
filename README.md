# QNAP QSW switch tools

QNAP QSW switches internally have a full blown Cisco-style management CLI hidden behind the dumbed down web interface.

## Physical console

Typical Cisco RJ45 pinout, 115200n1. The default CLI with the normal login doesn't let you do anything but enable SSH.

## Enable mode

To access enable mode:
1. log into the serial port via `admin` and your password.
2. Press CTRL-T in the serial console while logged in
3. On your computer: run `python3 genpwd.py <text privided from CTRL-T>
4. Press CTRL-R in the serial console while logged in
5. Paste in the password generated by genpwd.py

## Shell Access
To access a root shell from serial:
1. Log into enable mode as above
2. enter Lua Cli shell: `LuaCli`
3. enter `osShell`

## SSH Access

You can enable ssh from the normal admin shell via `ssh enable` then login as `debug` with the generated password above to get a root shell.  This is handled via `pam_debugauth.so`; if you don't like this, we can:

1. Edit `/etc/pam.d/sshd` to contain (based on https://github.com/openwrt/packages/blob/master/net/openssh/files/sshd.pam):
```
auth       required     pam_env.so
auth       include      common-auth
account    required     pam_nologin.so
account    include      common-account
session    include      common-session
session    optional     pam_motd.so
session    optional     pam_mail.so standard noenv
session    required     pam_limits.so
password   include      common-password
```
2. Modify root's shell in /etc/passwd to be `/bin/ash`
```
root:x:0:0:root:/root:/bin/ash
```
3. Set a root passord via `passwd root`

## Remove CLI access
Without opening the firewall, the best way that I found was to ssh to the switch as above then run `telnet 127.0.0.1 6023`

## Decrypting firmware

QNAP firmware images are plain tarballs, but every file other than the `fwver.json` contained within is encrypted. Use `decfile.sh` to decrypt them.

## Using a management VLAN other than 1

The CLI allows you to set IPs on more than one VLAN, but the firmware stupidly only sets the IP on the Linux TAP interface for interface "vlan1":

```c
if ( !strcmp(piIfName, "vlan1") ) {
  cpsstap_update_ip(pIfaceParams->u4IpAddr, pIfaceParams->u4SubnetMask);
}
```

... but you can cheat. Just leave vlan 1 unused, but set the IP you want on it. Then create an IP interface for the VLAN you actually want:

```
interface vlan 1
ip address  192.168.98.16 255.255.255.0
no shutdown
!
interface vlan 98
no shutdown
!
ip route 0.0.0.0  0.0.0.0 192.168.98.1
domain name-server ipv4 192.168.98.1
```

As long as the interface on the VLAN you want exists and is `no shutdown`, its traffic will go to the TAP interface that stuff is listening on, which will then get its IP from VLAN 1's IP.

Note: With this trick, ping won't work, since that is handled at a lower layer and the IP does not match there. Also, VLAN 1 needs to be up for this to work, so assign it to at least one active port.

## Other services

You can expose various services by commenting out stuff in `/etc/firewall.user` and then running `fw3`.

* Port 6023: ISS console (same as serial, with auth)
* Port 12345: Secret lua debug shell with low-level commands (no auth).
* Port 12346: Some kind of file transfer protocol, like FTP but inline (try `ls` and `get configToLoad.txt`). It's a virtual FS though.

Alternatively, use SSH forwarding (`ssh -L 6023:localhost:6023`) to tunnel the shell over SSH instead of just opening the ports.

## User management

You can log in and create users using `username <username> password <password> privilege 15` to make a new user, that user then allows you to log in without having to generate an enable password.
