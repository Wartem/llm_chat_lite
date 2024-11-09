#!/bin/bash

# Create systemd service file
sudo cat > /etc/systemd/system/llm_chat_lite.service << 'EOF'
[Unit]
Description=LLM Chat Lite Flask Application
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=wartem
Group=wartem
WorkingDirectory=/home/wartem/proj/llm_chat_lite
Environment="PATH=/home/wartem/proj/llm_chat_lite/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="FLASK_APP=app.py"
Environment="FLASK_ENV=production"
ExecStart=/home/wartem/proj/llm_chat_lite/.venv/bin/python3 /home/wartem/proj/llm_chat_lite/app.py
Restart=always
RestartSec=3

# Hardening
ProtectSystem=full
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Set correct permissions
sudo chmod 644 /etc/systemd/system/llm_chat_lite.service

# Create log directory if needed
sudo mkdir -p /var/log/llm_chat_lite
sudo chown wartem:wartem /var/log/llm_chat_lite