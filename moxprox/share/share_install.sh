#!/bin/sh

apt-get update
apt install -y nfs-kernel-server

systemctl enable nfs-server.service

sharepath="/srv/kvmnfsshare"

mkdir $sharepath
chown nobody:nogroup $sharepath

echo "$sharepath 192.168.20.0/24(rw,sync,anonuid=0,anongid=0,no_subtree_check)" >> /etc/exports

exportfs -a
systemctl start nfs-server.service

apt install -y mariadb-server
mysql_secure_installation

mysql <<EOF
GRANT ALL ON *.* TO 'admin'@'*' IDENTIFIED BY 'admin' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

echo "bind-address           = 0.0.0.0" >> /etc/mysql/mariadb.cnf

mysql -uadmin -padmin <<EOF
source create.sql
EOF

