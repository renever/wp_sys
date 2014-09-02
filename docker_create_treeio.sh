#!/bin/bash
# Description: Using Docker (requires docker to be installed http://www.docker.io/gettingstarted/ ), spawn a postgresql instance and a dynamically configured treeio instance
# Also requires postgresql client tools http://www.postgresql.org/download/linux/ubuntu/
# Run chmod +x to make this file executable then run it: ./docker_create_treeio.sh
# Author: Adam Awan
# Email: adam@tree.io

# Set the port to forward for Tree.io
TREEIO_PORT="80"

# Sleep for a second to give it a chance to spin up
sleep 1

echo "Pulling the treeio container..."
docker pull adam/treeio
echo "If running Vagrant you will need to forward port $TREEIO_PORT"
TREEID=$(docker run -d -p 22 -p $TREEIO_PORT:5000 adam/treeio /usr/sbin/treeio $PG_HOST $PG_PORT $PG_PASSWORD)
SSHPORT=$(docker port $TREEID 22)
echo "treeio running with container ID $TREEID"
echo "treeio SSH running on port $SSHPORT"
echo "WARNING! You must change the root password of your treeio container - currently it is 'treeio'."
echo "You can ssh to your container by running: ssh -p $SSHPORT root@localhost"
echo "Once connected run passwd to change your password."
echo "treeio is running at http://localhost:$TREEIO_PORT with username 'admin' and password 'admin'."
echo "Container setup complete."
