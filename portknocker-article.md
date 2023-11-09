
michael.kjorling.se
Server-side port knocking with Linux nftables – Michael Kjörling
4–5 Minuten

Port knocking is a technique to selectively allow for connections by sending a semi-secret sequence of packets, often called a “knocking” sequence.

While port knocking can very easily cut down on the amount of noise seen in logs, it’s important to keep in mind that it does not provide any significant level of security against a well-positioned adversary, as the knocking is done in the clear. The service that is hidden behind the port knocking still needs to be able to deal with being accessible from the outside network.

It used to be fairly complex on Linux to implement port knocking without relying on dedicated software to listen for the knocking packets and modify the firewall rules accordingly (which required that the listening software ran as root, which is usually something to be avoided if at all possible). Thankfully, with nftables, it’s relatively straight-forward to implement port knocking without ever leaving the firewall configuration, by using nftables’ set support.

The idea is to maintain two lists (sets) for a particular service: one of currently knocking clients, and one of clients that have successfully completed the knocking sequence.

In nftables syntax, it boils down to something similar to:

table inet filter {
  define ssh_knock_1 = 10000
  define ssh_knock_2 = 2345
  define ssh_knock_3 = 3456
  define ssh_knock_4 = 1234
  define ssh_service_port = 22

  set ssh_progress_ipv4 {
    type ipv4_addr . inet_service;
    flags timeout;
  }
  set ssh_clients_ipv4 {
    type ipv4_addr;
    flags timeout;
  }

  chain input {
    type filter hook input priority 0; policy drop;

    # ... other rules as needed ... #

    tcp dport $ssh_knock_1 update @ssh_progress_ipv4 { ip saddr . $ssh_knock_2 timeout 5s } drop
    tcp dport $ssh_knock_2 ip saddr . tcp dport @ssh_progress_ipv4 update @ssh_progress_ipv4 { ip saddr . $ssh_knock_3 timeout 5s } drop
    tcp dport $ssh_knock_3 ip saddr . tcp dport @ssh_progress_ipv4 update @ssh_progress_ipv4 { ip saddr . $ssh_knock_4 timeout 5s } drop
    tcp dport $ssh_knock_4 ip saddr . tcp dport @ssh_progress_ipv4 update @ssh_clients_ipv4 { ip saddr timeout 10s } drop

    ip saddr @ssh_clients_ipv4 tcp dport $ssh_service_port ct state new accept

    # ... other rules as needed ... #
  }
}

This works by, each time a port knock TCP connection attempt is received:

    check that this particular knock is in @ssh_progress_ipv4 (with the exception of the first knock in the sequence)
    for all but the last knock in the sequence, store the next expected knock in @ssh_progress_ipv4, and drop the knock packet (so to an outside observer, it looks no different from any other port)
    for the last knock in the sequence, store the connecting IP address in @ssh_clients_ipv4, and drop the knock packet
    when the actual connection attempt arrives, accept the connection only if the connecting IP address exists in @ssh_clients_ipv4

The knocking status is stored with a brief timeout (in the example above: 5 seconds during knocking, and 10 seconds on successful completion), ensuring that any lingering knockers are evicted promptly from the status sets.

The above example is for a four-port knocking sequence, but it could easily be both shorter and longer. The only state transition stanzas that are special is the very first and the last before the final decision stanza.

To also support port knocking and connections over IPv6, duplicate the two state sets (but use ipv6_addr for those instead of ipv4_addr), and duplicate the respective state transition and final decision stanzas (but use ip6 instead of ip).
