#!/bin/sh
git clone https://github.com/Baptiste1802/moxprox.git

# Vérification du nombre d'arguments
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <datacenter_id> <node_ip> <node_name_dns> <remote_db_ip>"
    exit 1
fi

host=$(hostname)

if [ "$3" -ne "$host" ]; then
    echo "node_name_dns must be equals to hostname"
    exit 1
fi

apt-get update
apt -y install net-tools
apt -y install novnc
apt -y install nfs-common
apt -y install mariadb-server

apt-get -y install python3-dev default-libmysqlclient-dev build-essential pkg-config

mkdir /srv/kvmnfsshare
echo "192.168.20.24:/srv/kvmnfsshare    /srv/kvmnfsshare nfs rw,hard,intr,_netdev 0 0" >> /etc/fstab
systemctl daemon-reload
mount -a

echo "PasswordAuthentication no" >> /etc/ssh/sshd_config

# Paramètres
DATACENTER_ID="$1"
NODE_IP="$2"
NODE_NAME_DNS="$3"
REMOTE_DB_IP="$4"
DB_USER="admin"
DB_PASS="admin"
DB_NAME="Cloud"

mysql_secure_installation

# Insérer l'entrée dans la base de données distante
mysql -h "$REMOTE_DB_IP" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" <<EOF
USE Cloud;
INSERT INTO dashboard_node (ip, name, datacenter_id) VALUES ('$NODE_IP', '$NODE_NAME_DNS', $DATACENTER_ID);
EOF

# Confirmation d'ajout
if [ $? -eq 0 ]; then
    echo "Le noeud avec IP $NODE_IP et nom DNS $NODE_NAME_DNS a été ajouté au datacenter $DATACENTER_ID sur la base de données distante $REMOTE_DB_IP."
else
    echo "Erreur lors de l'ajout du noeud à la base de données distante."
fi

python3 -m venv ./moxprox_venv
source moxprox_venv/bin/activate

pip install Django
pip install libvirt-python
pip install websockify

# https://github.com/PyMySQL/mysqlclient/blob/main/README.md#macos-homebrew
export MYSQLCLIENT_CFLAGS=`pkg-config mysqlclient --cflags`
export MYSQLCLIENT_LDFLAGS=`pkg-config mysqlclient --libs`
pip install mysqlclient

cd moxprox/moxprox
rm -rf ./dashboard/migrations
python manage.py inspectdb > ./dashboard/models.py
python manage.py makemigrations dashboard
python manage.py migrate dashboard 0001_initial --fake

deactivate
