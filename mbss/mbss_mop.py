"""
MBSS (Minimum Baseline Security Standard) MOP data for CPNR on RHEL/AlmaLinux 9.

Each entry:
  id               : MBSS control number
  title            : control name
  applicable       : True/False (False = Not Applicable for CPNR CDNS)
  verify_commands  : list of shell commands to check current compliance state
  remediate_commands: list of shell commands to apply the fix
                      (empty = already set / manual / ViPAM managed)
  notes            : brief guidance
"""

MBSS_MOP = [
    {
        "id": 1,
        "title": "Dormant Account",
        "applicable": True,
        "verify_commands": [
            "grep -i inactive /etc/default/useradd"
        ],
        "remediate_commands": [
            "sed -i 's/^INACTIVE=.*/INACTIVE=60/' /etc/default/useradd || echo 'INACTIVE=60' >> /etc/default/useradd"
        ],
        "notes": "INACTIVE=60 must be set in /etc/default/useradd."
    },
    {
        "id": 2,
        "title": "Account Lock",
        "applicable": True,
        "verify_commands": [
            "grep -i pam_faillock /etc/pam.d/system-auth",
            "grep -E 'deny|unlock_time' /etc/security/faillock.conf 2>/dev/null | grep -v '^#'"
        ],
        "remediate_commands": [
            "authselect enable-feature with-faillock",
            "grep -q '^deny' /etc/security/faillock.conf 2>/dev/null && sed -i 's/^deny.*/deny = 5/' /etc/security/faillock.conf || echo 'deny = 5' >> /etc/security/faillock.conf",
            "grep -q '^unlock_time' /etc/security/faillock.conf 2>/dev/null && sed -i 's/^unlock_time.*/unlock_time = 600/' /etc/security/faillock.conf || echo 'unlock_time = 600' >> /etc/security/faillock.conf"
        ],
        "notes": "Account locked after 5 invalid attempts; unlocked after 600 seconds."
    },
    {
        "id": 3,
        "title": "User Access Control",
        "applicable": True,
        "verify_commands": [
            "grep -i wheel /etc/group",
            "grep -v nologin /etc/passwd | grep -v false"
        ],
        "remediate_commands": [],
        "notes": "Managed via ViPAM. Only required users should be in wheel group."
    },
    {
        "id": 4,
        "title": "Concurrent Login",
        "applicable": True,
        "verify_commands": [
            "grep maxlogins /etc/security/limits.conf | grep -v '^#'"
        ],
        "remediate_commands": [
            "grep -q 'hard maxlogins' /etc/security/limits.conf && sed -i 's/.*hard maxlogins.*/\\* hard maxlogins 1/' /etc/security/limits.conf || echo '* hard maxlogins 1' >> /etc/security/limits.conf"
        ],
        "notes": "Maximum 1 concurrent session per user via /etc/security/limits.conf."
    },
    {
        "id": 5,
        "title": "Guest Accounts",
        "applicable": True,
        "verify_commands": [
            "grep -i guest /etc/passwd || echo 'No guest accounts found'"
        ],
        "remediate_commands": [],
        "notes": "No guest accounts should be present. All accounts managed via ViPAM."
    },
    {
        "id": 6,
        "title": "Default User ID",
        "applicable": True,
        "verify_commands": [
            "grep -E '^admin:|^test:|^guest:' /etc/passwd || echo 'No default accounts found'",
            "grep -v '!' /etc/shadow | grep -v '*' | awk -F: '{print $1}'"
        ],
        "remediate_commands": [],
        "notes": "No default/test accounts. All accounts managed via ViPAM."
    },
    {
        "id": 7,
        "title": "Unique User IDs",
        "applicable": True,
        "verify_commands": [
            "awk -F: '{print $3}' /etc/passwd | sort -n | uniq -d | xargs -r echo 'Duplicate UIDs:' || echo 'No duplicate UIDs'"
        ],
        "remediate_commands": [],
        "notes": "Verify no duplicate UIDs exist."
    },
    {
        "id": 8,
        "title": "Account Expiry",
        "applicable": True,
        "verify_commands": [
            "awk -F: '$7 !~ /nologin|false/ {print $1}' /etc/passwd | xargs -I{} sh -c 'echo \"--- {} ---\"; chage -l {} 2>/dev/null | grep -E \"Account expires|Password expires\"'"
        ],
        "remediate_commands": [],
        "notes": "Third-party account expiry managed via ViPAM."
    },
    {
        "id": 9,
        "title": "Idle Session Timeout",
        "applicable": True,
        "verify_commands": [
            "grep -E 'ClientAliveInterval|ClientAliveCountMax' /etc/ssh/sshd_config | grep -v '^#'"
        ],
        "remediate_commands": [
            "sed -i 's/^#*ClientAliveInterval.*/ClientAliveInterval 600/' /etc/ssh/sshd_config",
            "sed -i 's/^#*ClientAliveCountMax.*/ClientAliveCountMax 0/' /etc/ssh/sshd_config",
            "systemctl restart sshd"
        ],
        "notes": "ClientAliveInterval=600 and ClientAliveCountMax=0 for 10-minute timeout."
    },
    {
        "id": 10,
        "title": "Remote Login (PermitRootLogin)",
        "applicable": True,
        "verify_commands": [
            "grep -E '^PermitRootLogin' /etc/ssh/sshd_config || echo 'PermitRootLogin not explicitly set'"
        ],
        "remediate_commands": [
            "sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config",
            "systemctl restart sshd"
        ],
        "notes": "Direct root SSH login must be disabled."
    },
    {
        "id": 11,
        "title": "Role Based Access Control",
        "applicable": True,
        "verify_commands": [
            "grep -i wheel /etc/group",
            "ls /etc/sudoers.d/ 2>/dev/null && cat /etc/sudoers.d/* 2>/dev/null || echo 'sudoers.d empty'"
        ],
        "remediate_commands": [],
        "notes": "Role-based access controlled via ViPAM and wheel group tagging."
    },
    {
        "id": 12,
        "title": "Centralized Authentication",
        "applicable": True,
        "verify_commands": [
            "systemctl is-active sssd 2>/dev/null || echo 'sssd not running'",
            "grep -v '^#' /etc/sssd/sssd.conf 2>/dev/null | head -15 || echo 'sssd.conf not found'"
        ],
        "remediate_commands": [],
        "notes": "System integrated with ViPAM/LDAP via sssd for centralized auth."
    },
    {
        "id": 13,
        "title": "Logon Failure Message",
        "applicable": True,
        "verify_commands": [
            "grep -E '^LogLevel' /etc/ssh/sshd_config || echo 'LogLevel not explicitly set'"
        ],
        "remediate_commands": [
            "sed -i 's/^#*LogLevel.*/LogLevel ERROR/' /etc/ssh/sshd_config",
            "systemctl restart sshd"
        ],
        "notes": "SSH LogLevel ERROR prevents system info disclosure on login failure."
    },
    {
        "id": 14,
        "title": "Privilege Escalation",
        "applicable": True,
        "verify_commands": [
            "grep -v '^#' /etc/sudoers | grep -v '^$'",
            "ls /etc/sudoers.d/ 2>/dev/null"
        ],
        "remediate_commands": [],
        "notes": "No NOPASSWD entries allowed. Privilege managed via ViPAM."
    },
    {
        "id": 15,
        "title": "Minimum Password Length",
        "applicable": True,
        "verify_commands": [
            "grep -E '^minlen' /etc/security/pwquality.conf || echo 'minlen not set (using default)'"
        ],
        "remediate_commands": [
            "sed -i 's/^#*[ ]*minlen[ ]*=.*/minlen = 14/' /etc/security/pwquality.conf"
        ],
        "notes": "Minimum password length must be 14 characters."
    },
    {
        "id": 16,
        "title": "Password Age",
        "applicable": True,
        "verify_commands": [
            "grep '^PASS_MAX_DAYS' /etc/login.defs",
            "chage -l root | grep 'Maximum number of days'"
        ],
        "remediate_commands": [
            "sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS   60/' /etc/login.defs"
        ],
        "notes": "Maximum password age must be 60 days."
    },
    {
        "id": 17,
        "title": "Password History",
        "applicable": True,
        "verify_commands": [
            "grep -E 'remember|pwhistory' /etc/pam.d/system-auth || echo 'Password history not configured'",
            "grep -E 'remember|pwhistory' /etc/pam.d/password-auth || echo 'Password history not configured'"
        ],
        "remediate_commands": [
            "grep -q 'remember=' /etc/pam.d/system-auth && sed -i 's/remember=[0-9]*/remember=6/g' /etc/pam.d/system-auth || sed -i '/password.*pam_unix.so/ s/$/ remember=6/' /etc/pam.d/system-auth",
            "grep -q 'remember=' /etc/pam.d/password-auth && sed -i 's/remember=[0-9]*/remember=6/g' /etc/pam.d/password-auth || sed -i '/password.*pam_unix.so/ s/$/ remember=6/' /etc/pam.d/password-auth"
        ],
        "notes": "Last 6 passwords must not be reused (remember=6 in PAM)."
    },
    {
        "id": 18,
        "title": "Null Passwords",
        "applicable": True,
        "verify_commands": [
            "awk -F: '($2==\"\"){print $1}' /etc/shadow || echo 'No accounts with empty passwords'",
            "grep 'nullok' /etc/pam.d/system-auth /etc/pam.d/password-auth 2>/dev/null || echo 'nullok not found'"
        ],
        "remediate_commands": [
            "sed -i 's/ nullok//g' /etc/pam.d/system-auth",
            "sed -i 's/ nullok//g' /etc/pam.d/password-auth"
        ],
        "notes": "nullok must be removed from PAM. No empty passwords allowed."
    },
    {
        "id": 19,
        "title": "Default Password",
        "applicable": True,
        "verify_commands": [
            "grep -v '!' /etc/shadow | grep -v '*' | awk -F: '{print $1}' | head -10"
        ],
        "remediate_commands": [],
        "notes": "All default passwords changed. Managed via ViPAM."
    },
    {
        "id": 20,
        "title": "Password Complexity Criteria",
        "applicable": True,
        "verify_commands": [
            "grep -E '^(minlen|dcredit|ucredit|lcredit|ocredit|minclass)' /etc/security/pwquality.conf || echo 'Complexity not explicitly set'"
        ],
        "remediate_commands": [
            "sed -i 's/^#*[ ]*minlen[ ]*=.*/minlen = 14/' /etc/security/pwquality.conf",
            "sed -i 's/^#*[ ]*dcredit[ ]*=.*/dcredit = -1/' /etc/security/pwquality.conf",
            "sed -i 's/^#*[ ]*ucredit[ ]*=.*/ucredit = -1/' /etc/security/pwquality.conf",
            "sed -i 's/^#*[ ]*lcredit[ ]*=.*/lcredit = -1/' /etc/security/pwquality.conf",
            "sed -i 's/^#*[ ]*ocredit[ ]*=.*/ocredit = -1/' /etc/security/pwquality.conf",
            "sed -i 's/^#*[ ]*minclass[ ]*=.*/minclass = 4/' /etc/security/pwquality.conf"
        ],
        "notes": "Password must contain uppercase, lowercase, digit, and special character."
    },
    {
        "id": 21,
        "title": "Passwords in Encrypted Form",
        "applicable": True,
        "verify_commands": [
            "grep '^ENCRYPT_METHOD' /etc/login.defs",
            "grep '^root' /etc/shadow | cut -d: -f2 | cut -c1-3"
        ],
        "remediate_commands": [],
        "notes": "SHA512 ($6$) encryption must be used. Already set by default on RHEL 9."
    },
    {
        "id": 22,
        "title": "Change Passwords at First Login",
        "applicable": True,
        "verify_commands": [
            "awk -F: '$7 !~ /nologin|false/ {print $1}' /etc/passwd | xargs -I{} sh -c 'result=$(chage -l {} 2>/dev/null | grep \"Password must be changed\"); [ -n \"$result\" ] && echo \"{}: $result\"'"
        ],
        "remediate_commands": [],
        "notes": "Force first-login password change via: chage -d 0 <username>. Managed via ViPAM."
    },
    {
        "id": 23,
        "title": "Unnecessary Services",
        "applicable": True,
        "verify_commands": [
            "ss -tlnp",
            "systemctl list-units --type=service --state=running --no-pager | head -30"
        ],
        "remediate_commands": [],
        "notes": "Review all ports; disable unnecessary services manually."
    },
    {
        "id": 24,
        "title": "Secure Services for Management",
        "applicable": True,
        "verify_commands": [
            "/opt/nwreg2/local/usrbin/cnr_status 2>/dev/null | grep -i WEB || echo 'cnr_status: Web UI status check'",
            "grep -E '^Protocol' /etc/ssh/sshd_config || echo 'SSH Protocol 2 (default in OpenSSH)'"
        ],
        "remediate_commands": [],
        "notes": "SSH used for secure management. Web UI checked via cnr_status."
    },
    {
        "id": 25,
        "title": "Disable Ping Responses",
        "applicable": True,
        "verify_commands": [
            "sysctl net.ipv4.icmp_echo_ignore_all",
            "grep 'icmp_echo_ignore_all' /etc/sysctl.conf /etc/sysctl.d/*.conf 2>/dev/null || echo 'icmp_echo_ignore_all not in sysctl.conf'"
        ],
        "remediate_commands": [
            "grep -q 'icmp_echo_ignore_all' /etc/sysctl.conf && sed -i 's/.*icmp_echo_ignore_all.*/net.ipv4.icmp_echo_ignore_all = 1/' /etc/sysctl.conf || echo 'net.ipv4.icmp_echo_ignore_all = 1' >> /etc/sysctl.conf",
            "sysctl -p"
        ],
        "notes": "Disable ping on public-facing nodes only. Internal ping may be allowed."
    },
    {
        "id": 26,
        "title": "SSH Protocol 2",
        "applicable": True,
        "verify_commands": [
            "ssh -V",
            "grep -i '^Protocol' /etc/ssh/sshd_config || echo 'Protocol line not present; SSHv2 is the only supported protocol in modern OpenSSH'"
        ],
        "remediate_commands": [],
        "notes": "Protocol 2 is the default and only supported protocol in OpenSSH. No action needed."
    },
    {
        "id": 27,
        "title": "NFS Shares Protection",
        "applicable": False,
        "verify_commands": [
            "showmount -e localhost 2>/dev/null || echo 'NFS not configured'",
            "cat /etc/exports 2>/dev/null || echo '/etc/exports not found'"
        ],
        "remediate_commands": [],
        "notes": "NOT APPLICABLE. NFS shares are not used on CPNR servers."
    },
    {
        "id": 28,
        "title": "Physical Interface",
        "applicable": True,
        "verify_commands": [
            "cat /etc/securetty 2>/dev/null | head -20 || echo 'securetty not present (RHEL 9 default)'"
        ],
        "remediate_commands": [],
        "notes": "CPNR installed in VM. Console requires authentication."
    },
    {
        "id": 29,
        "title": "Enable TLS for Network Communication",
        "applicable": True,
        "verify_commands": [
            "update-crypto-policies --show",
            "/opt/nwreg2/local/usrbin/cnr_status 2>/dev/null | grep -iE 'WEB|TLS' || echo 'TLS enforced at OS crypto-policy level'"
        ],
        "remediate_commands": [
            "update-crypto-policies --set DEFAULT:NO-SHA1"
        ],
        "notes": "TLS 1.2+ enforced at OS level via crypto-policies."
    },
    {
        "id": 30,
        "title": "Clock Sync (NTP)",
        "applicable": True,
        "verify_commands": [
            "timedatectl status",
            "chronyc sources -v 2>/dev/null || echo 'chrony not running'"
        ],
        "remediate_commands": [
            "systemctl enable chronyd",
            "systemctl start chronyd"
        ],
        "notes": "Chrony NTP synchronization must be active and configured."
    },
    {
        "id": 31,
        "title": "DOS Protection",
        "applicable": True,
        "verify_commands": [
            "sysctl net.ipv4.tcp_syncookies",
            "sysctl net.ipv4.icmp_ratelimit"
        ],
        "remediate_commands": [
            "grep -q 'tcp_syncookies' /etc/sysctl.conf && sed -i 's/.*tcp_syncookies.*/net.ipv4.tcp_syncookies = 1/' /etc/sysctl.conf || echo 'net.ipv4.tcp_syncookies = 1' >> /etc/sysctl.conf",
            "grep -q 'icmp_ratelimit' /etc/sysctl.conf && sed -i 's/.*icmp_ratelimit.*/net.ipv4.icmp_ratelimit = 100/' /etc/sysctl.conf || echo 'net.ipv4.icmp_ratelimit = 100' >> /etc/sysctl.conf",
            "sysctl -p"
        ],
        "notes": "TCP SYN cookies and ICMP rate limiting for DoS protection."
    },
    {
        "id": 32,
        "title": "Anti-Virus Protection",
        "applicable": True,
        "verify_commands": [
            "clamscan --version 2>/dev/null || rpm -qa | grep -iE 'clam|antivir|trend|sophos' || echo 'Check VIL antivirus solution'"
        ],
        "remediate_commands": [],
        "notes": "Antivirus installation and management is VIL responsibility."
    },
    {
        "id": 33,
        "title": "Backup Storage and Access Control",
        "applicable": True,
        "verify_commands": [
            "ls -lrt /var/nwreg2/local/backup/ 2>/dev/null || ls -lrt /var/nwreg2/local/ 2>/dev/null | grep -i backup || echo 'CPNR backup directory not found'"
        ],
        "remediate_commands": [],
        "notes": "Daily CPNR backups stored in /var/nwreg2/local/."
    },
    {
        "id": 34,
        "title": "Logging",
        "applicable": True,
        "verify_commands": [
            "systemctl is-active auditd",
            "ls -lh /var/log/audit/audit.log"
        ],
        "remediate_commands": [],
        "notes": "Audit logging via auditd must be active."
    },
    {
        "id": 35,
        "title": "External Syslog Server",
        "applicable": True,
        "verify_commands": [
            "grep -E '^@|^@@' /etc/rsyslog.conf 2>/dev/null || echo 'No remote syslog target in rsyslog.conf'",
            "systemctl is-active rsyslog"
        ],
        "remediate_commands": [],
        "notes": "Integrated with SIEM for centralized logging."
    },
    {
        "id": 36,
        "title": "Logs Archive",
        "applicable": True,
        "verify_commands": [
            "grep '^rotate' /etc/logrotate.conf",
            "cat /etc/logrotate.d/syslog 2>/dev/null | head -10 || echo 'Check logrotate.d for syslog config'"
        ],
        "remediate_commands": [],
        "notes": "Logs: 30 days local, 12 months on centralized server via INM."
    },
    {
        "id": 37,
        "title": "Restrict Access to Log Files",
        "applicable": True,
        "verify_commands": [
            "ls -la /var/log/audit/",
            "stat -c '%a %n' /var/log/audit/audit.log"
        ],
        "remediate_commands": [
            "chmod 700 /var/log/audit",
            "chmod 600 /var/log/audit/audit.log"
        ],
        "notes": "Audit log dir must be 700, audit.log must be 600."
    },
    {
        "id": 38,
        "title": "Log File Contents",
        "applicable": True,
        "verify_commands": [
            "auditctl -l",
            "tail -20 /var/log/audit/audit.log | grep -E 'USER_LOGIN|USER_AUTH|ADD_USER|SYSCALL' | head -10 || echo 'No recent login events in last 20 lines'"
        ],
        "remediate_commands": [],
        "notes": "Audit log must capture login, auth, user creation, and syscall events."
    },
    {
        "id": 39,
        "title": "Alarms",
        "applicable": True,
        "verify_commands": [
            "grep -E '[*].emerg|[*].alert|[*].crit' /etc/rsyslog.conf || echo 'Check INM integration for alarms'"
        ],
        "remediate_commands": [],
        "notes": "Alarms integrated with INM system."
    },
    {
        "id": 40,
        "title": "SNMP Version",
        "applicable": True,
        "verify_commands": [
            "grep -iE 'v3|createUser|rouser|rwuser' /etc/snmp/snmpd.conf 2>/dev/null || echo 'SNMPv3 config not found - manual configuration required'"
        ],
        "remediate_commands": [],
        "notes": "SNMPv3 with authPriv must be configured manually in /etc/snmp/snmpd.conf."
    },
    {
        "id": 41,
        "title": "SNMP Community String",
        "applicable": False,
        "verify_commands": [
            "grep -i community /etc/snmp/snmpd.conf 2>/dev/null | grep -v '^#' || echo 'No community string configured (SNMPv3 in use)'"
        ],
        "remediate_commands": [],
        "notes": "NOT APPLICABLE. SNMPv3 is in use; community strings not required."
    },
    {
        "id": 42,
        "title": "SNMP Traps Destination",
        "applicable": True,
        "verify_commands": [
            "grep -iE 'trap2sink|trapsink|informsink' /etc/snmp/snmpd.conf 2>/dev/null || echo 'No SNMP trap destination configured'"
        ],
        "remediate_commands": [],
        "notes": "SNMP traps must target only authorized receivers. Manual configuration required."
    },
    {
        "id": 43,
        "title": "Event Monitoring and Review",
        "applicable": True,
        "verify_commands": [
            "tail -20 /var/log/audit/audit.log | grep -E 'USER_LOGIN|USER_AUTH' | head -5 || echo 'No recent login events'",
            "journalctl --since '1 hour ago' --no-pager 2>/dev/null | grep -iE 'error|fail|denied' | head -10 || echo 'journalctl check complete'"
        ],
        "remediate_commands": [],
        "notes": "Event logs monitored regularly via SIEM integration."
    },
    {
        "id": 44,
        "title": "Asset Tracking",
        "applicable": True,
        "verify_commands": [
            "hostname",
            "cat /etc/machine-id",
            "ip addr show | grep 'inet '"
        ],
        "remediate_commands": [],
        "notes": "Asset register maintained per VIL policy. Integrated with SIEM."
    },
    {
        "id": 45,
        "title": "Legal Notice Banner",
        "applicable": True,
        "verify_commands": [
            "grep -E '^Banner' /etc/ssh/sshd_config || echo 'Banner not configured'",
            "cat /etc/banner.txt 2>/dev/null || echo 'Banner file not found'"
        ],
        "remediate_commands": [
            "printf 'Authorized access only. This system is the property of VodafoneIdea Mobile.\\nDisconnect IMMEDIATELY if you are not an authorized user!\\nAll connection attempts are logged and monitored.\\nAll unauthorized connection attempts will be investigated and handed over to the proper authorities.\\n' > /etc/banner.txt",
            "grep -q '^Banner' /etc/ssh/sshd_config && sed -i 's|^Banner.*|Banner /etc/banner.txt|' /etc/ssh/sshd_config || echo 'Banner /etc/banner.txt' >> /etc/ssh/sshd_config",
            "systemctl restart sshd"
        ],
        "notes": "Legal notice banner must appear before SSH login."
    },
    {
        "id": 46,
        "title": "Management Plane Separation",
        "applicable": True,
        "verify_commands": [
            "ip a",
            "ip route show"
        ],
        "remediate_commands": [],
        "notes": "Management NIC must be dedicated to management functions only."
    },
    {
        "id": 47,
        "title": "Network ACL for Management Access",
        "applicable": True,
        "verify_commands": [
            "firewall-cmd --list-all 2>/dev/null",
            "iptables -L -n 2>/dev/null | head -30"
        ],
        "remediate_commands": [],
        "notes": "Access restricted to authorized O&M devices/subnets."
    },
    {
        "id": 48,
        "title": "Authorized Peer Node Communication",
        "applicable": True,
        "verify_commands": [
            "route -n",
            "grep -v '^#' /etc/hosts"
        ],
        "remediate_commands": [],
        "notes": "Only authorized signaling peers in routing/hosts configuration."
    },
    {
        "id": 49,
        "title": "Remote Access",
        "applicable": True,
        "verify_commands": [
            "cat /etc/hosts.allow 2>/dev/null || echo 'hosts.allow not present'",
            "cat /etc/hosts.deny 2>/dev/null || echo 'hosts.deny not present'"
        ],
        "remediate_commands": [],
        "notes": "Remote access controlled via ViPAM. Only approved India locations."
    },
    {
        "id": 50,
        "title": "Restrict File Access",
        "applicable": True,
        "verify_commands": [
            "ls -la /var/nwreg2/local/data/ 2>/dev/null || echo 'CPNR data directory not found'"
        ],
        "remediate_commands": [],
        "notes": "Access to CDR, logs, backups, configs restricted by user role."
    },
    {
        "id": 51,
        "title": "Device Documents",
        "applicable": True,
        "verify_commands": [
            "echo 'Documentation: https://www.cisco.com/c/en/us/td/docs/net_mgmt/prime/network_registrar/'"
        ],
        "remediate_commands": [],
        "notes": "User Manual and O&M docs provided by Cisco. Available on Cisco website."
    },
    {
        "id": 52,
        "title": "Device Security Test Certificate",
        "applicable": True,
        "verify_commands": [
            "echo 'Security test certificates provided during deployment. Review manually.'"
        ],
        "remediate_commands": [],
        "notes": "Security test certificates must be maintained for 10 years."
    },
    {
        "id": 53,
        "title": "System Upgrades",
        "applicable": True,
        "verify_commands": [
            "cat /etc/os-release | grep -E '^NAME|^VERSION'",
            "/opt/nwreg2/local/usrbin/cnr_status 2>/dev/null | head -5 || echo 'Verify CPNR version manually'",
            "dnf check-update --quiet 2>/dev/null | wc -l | xargs -I{} echo 'Packages with pending updates: {}'"
        ],
        "remediate_commands": [
            "dnf update -y"
        ],
        "notes": "All latest patches must be installed. Change records kept for 10 years."
    },
    {
        "id": 54,
        "title": "Service Resilience (Disaster Recovery)",
        "applicable": True,
        "verify_commands": [
            "hostname",
            "ip a | grep 'inet '"
        ],
        "remediate_commands": [],
        "notes": "Multiple VMs deployed on different machines for redundancy."
    },
    {
        "id": 55,
        "title": "Privacy Audit (PII & SPI) Data Handling",
        "applicable": True,
        "verify_commands": [
            "systemctl is-active sssd 2>/dev/null || echo 'sssd status'",
            "echo 'PII/SPI: Devices integrated with SIEM and ViPAM for privacy compliance'"
        ],
        "remediate_commands": [],
        "notes": "Integrated with SIEM and ViPAM. Inform VIL Privacy team for assessment."
    },
    {
        "id": 56,
        "title": "Security Mode Should Be Enabled",
        "applicable": True,
        "verify_commands": [
            "/opt/nwreg2/local/usrbin/cnr_status 2>/dev/null | grep -iE 'WEB|security|mode' || echo 'Verify CPNR security mode via cnr_status'"
        ],
        "remediate_commands": [
            "/opt/nwreg2/local/usrbin/cnr_status --enable-security 2>/dev/null || echo 'Command may vary by CPNR version - verify manually'"
        ],
        "notes": "CPNR security mode must be enabled. Verify with cnr_status."
    },
    {
        "id": 57,
        "title": "Enhancing Security for Web UI",
        "applicable": False,
        "verify_commands": [
            "/opt/nwreg2/local/usrbin/cnr_status 2>/dev/null | grep WEB || echo 'Web UI not in use'"
        ],
        "remediate_commands": [],
        "notes": "NOT APPLICABLE. Web UI is not in use for this CPNR deployment."
    },
    {
        "id": 58,
        "title": "CPNR Using Non-Root Account",
        "applicable": True,
        "verify_commands": [
            "ps -ef | grep -E 'nwreg|cnr' | grep -v grep",
            "/opt/nwreg2/local/usrbin/cnr_status 2>/dev/null | head -5 || echo 'Check CPNR process user manually'"
        ],
        "remediate_commands": [],
        "notes": "CPNR processes should run under dedicated non-root account where possible."
    },
    {
        "id": 59,
        "title": "Use DNS Security Extensions (DNSSEC)",
        "applicable": True,
        "verify_commands": [
            "/opt/nwreg2/local/usrbin/nrcmd -N admin -P admin cdnssec show 2>/dev/null || echo 'Verify DNSSEC status via nrcmd: cdnssec show'"
        ],
        "remediate_commands": [],
        "notes": "DNSSEC must be enabled via nrcmd. Manual: nrcmd cdnssec enable."
    },
    {
        "id": 60,
        "title": "Secure DNS Server Activity with ACLs",
        "applicable": False,
        "verify_commands": [
            "echo 'NOT APPLICABLE: Only CDNS installed here, not ADNS.'"
        ],
        "remediate_commands": [],
        "notes": "NOT APPLICABLE. Applies to ADNS only; CDNS is installed."
    },
    {
        "id": 61,
        "title": "Secure Zone Transfers Using TSIG or GSS-TSIG",
        "applicable": False,
        "verify_commands": [
            "echo 'NOT APPLICABLE: Only CDNS installed. TSIG applies when both DHCP and ADNS are present.'"
        ],
        "remediate_commands": [],
        "notes": "NOT APPLICABLE. Only CDNS in use."
    },
    {
        "id": 62,
        "title": "Randomize Query IDs and Source Ports",
        "applicable": True,
        "verify_commands": [
            "/opt/nwreg2/local/usrbin/nrcmd -N admin -P admin dns show 2>/dev/null | grep -iE 'random|port' || echo 'Query ID/port randomization: Enabled by default in CPNR'"
        ],
        "remediate_commands": [],
        "notes": "Query ID and source port randomization enabled by default in CPNR."
    },
    {
        "id": 63,
        "title": "DNS Rate Limiting",
        "applicable": True,
        "verify_commands": [
            "/opt/nwreg2/local/usrbin/nrcmd -N admin -P admin dns show 2>/dev/null | grep -iE 'rate|limit' || echo 'DNS Rate Limiting: Enabled by default in CPNR'"
        ],
        "remediate_commands": [],
        "notes": "DNS rate limiting enabled by default in CPNR to combat reflection attacks."
    },
    {
        "id": 64,
        "title": "Separate Recursive and Authoritative Server Roles",
        "applicable": False,
        "verify_commands": [
            "echo 'NOT APPLICABLE: Only CDNS installed here, not ADNS.'"
        ],
        "remediate_commands": [],
        "notes": "NOT APPLICABLE. Only CDNS installed here."
    },
    {
        "id": 65,
        "title": "DHCP Specific Considerations",
        "applicable": False,
        "verify_commands": [
            "echo 'NOT APPLICABLE: DHCP is not used on this CPNR server.'"
        ],
        "remediate_commands": [],
        "notes": "NOT APPLICABLE. DHCP is not used."
    },
    {
        "id": 66,
        "title": "DNS Amplification Attack Prevention",
        "applicable": True,
        "verify_commands": [
            "/opt/nwreg2/local/usrbin/nrcmd -N admin -P admin dns show 2>/dev/null | grep -iE 'amplification|attack' || echo 'DNS Amplification Prevention: Enabled by default in CPNR'"
        ],
        "remediate_commands": [],
        "notes": "DNS amplification attack prevention enabled by default in CPNR."
    },
    {
        "id": 67,
        "title": "PNR DNS Firewall",
        "applicable": True,
        "verify_commands": [
            "firewall-cmd --list-all 2>/dev/null",
            "iptables -L -n 2>/dev/null | head -20"
        ],
        "remediate_commands": [],
        "notes": "DNS placed behind firewall. Verify firewall rules are configured correctly."
    },
]

# Quick lookup by ID
MBSS_BY_ID = {item["id"]: item for item in MBSS_MOP}
