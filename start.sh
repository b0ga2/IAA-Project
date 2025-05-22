#!/bin/bash

# just to make sure that we are using the virtual environment
source venv/bin/activate

cat << EOF > /tmp/bootstrap_tabs.sh
gnome-terminal --tab -t "Holder"
gnome-terminal --tab -t "Blockchain" -- bash -c "python blockchain.py; exec bash"
gnome-terminal --tab -t "Interface"  -- bash -c "python interface.py;  exec bash"
gnome-terminal --tab -t "Issuer"     -- bash -c "python issuer.py 1;   exec bash"
gnome-terminal --tab -t "Verifier"   -- bash -c "python verifier.py;   exec bash"
gnome-terminal --tab -t "Wallet"     -- bash -c "python wallet.py;     exec bash"
EOF

gnome-terminal --window -- bash /tmp/bootstrap_tabs.sh
