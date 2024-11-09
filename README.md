![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.0+-lightgrey.svg)
![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20windows-lightgrey)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Flask SSE](https://img.shields.io/badge/Flask-SSE-blue)
![Ollama](https://img.shields.io/badge/Ollama-Compatible-brightgreen)
![Translation](https://img.shields.io/badge/Translation-Supported-success)
![UI](https://img.shields.io/badge/UI-Responsive-blue)
![Theme](https://img.shields.io/badge/Theme-Dark%20%7C%20Light-lightgrey)
![License](https://img.shields.io/badge/License-GNU%20GPL%20v3-blue.svg)
![Google Translate](https://img.shields.io/badge/Google%20Translate-API-yellow)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Compatible-C51A4A)
![googletrans](https://img.shields.io/badge/googletrans-4.0+-orange)
![SSE](https://img.shields.io/badge/SSE-Streaming-green)
![ARM](https://img.shields.io/badge/ARM-v8%20Compatible-red)
![Network](https://img.shields.io/badge/Network-Local%20%7C%20Internet-blue)

# LLM Chat Lite

A lightweight Flask web application for chatting with local LLM models through Ollama instances. Features automatic language translation, theme switching, and high-availability through multiple Ollama instances.

## Key Features

- Multiple Ollama instance support with automatic failover
- Real-time chat interface with streaming responses
- Automatic language detection and translation
- Dark/Light theme support
- Session management
- Health monitoring of Ollama instances
- Responsive design for mobile and desktop
- Markdown rendering support
- Server-sent events (SSE) for real-time updates

## Technical Details

- **Backend**: Python Flask
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Translation**: Google Translate API (via `googletrans`)
- **Streaming**: Server-Sent Events (SSE)
- **Instance Management**: Priority-based with health checks
- **Caching**: LRU cache for language detection
- **Theme System**: CSS-based theming with dynamic switching

## Screenshots

<div align="center">

| Screenshot 1 | Screenshot 2 | Screenshot 3 |
|:-------------------------:|:-------------------------:|:-------------------------:|
| ![image](https://github.com/user-attachments/assets/b4b9b3e1-81f9-48cf-bab8-9962554863be) | ![image](https://github.com/user-attachments/assets/2694f627-4aa1-460f-b399-65d4307b9a37) | ![image](https://github.com/user-attachments/assets/c5a6162c-f354-432b-b1ec-143f33c081d3) |
| Dark theme | Responsive | White theme |

</div>

## Requirements

- Python 3.8+
- Flask
- Requests
- googletrans
- Ollama instance(s) running locally or on network
- Modern web browser with SSE support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llm-chat-lite.git
cd llm-chat-lite
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure Ollama instances:
```bash
cp ollama_config.json.example ollama_config.json
# Edit ollama_config.json with your instance details
```

## Usage

1. Start the Flask server:
```bash
python3 app.py
```

2. Access the application:
```
http://localhost:5012
```

## Project Structure

```
llm-chat-lite/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── translator.py         # Translation service
├── ollama_config.json    # Ollama instance configuration
├── static/
│   ├── script.js        # Frontend JavaScript
│   ├── style.css        # Dark theme styles
│   └── bright_style.css # Light theme styles
└── templates/
    └── index.html       # Main HTML template
```

## API Endpoints

### Chat Endpoints
- `GET /api/chat`
  - Query params: `message`, `session_id`
  - Returns: SSE stream of chat responses

- `POST /api/reset`
  - Body: `{ "session_id": "string" }`
  - Resets conversation history

### System Endpoints
- `GET /api/models`
  - Returns: List of available LLM models

- `GET /api/status`
  - Returns: Health status of Ollama instances

- `GET /api/theme`
  - Returns: Current theme settings

- `POST /api/theme/<theme_name>`
  - Sets application theme (dark/bright)

## Limitations

- Maximum conversation history of 20 messages per session
- Translation service may have rate limits
- Requires at least one healthy Ollama instance
- No persistent storage of chat history
- Limited to models available in connected Ollama instances
- Single file HTML/CSS only for theme changes

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Verify Ollama instances are running
   - Check network connectivity
   - Confirm correct URLs in ollama_config.json

2. **Translation Issues**
   - Service will retry 3 times with 1-second delays
   - Falls back to English if translation fails
   - Check network connectivity

3. **Model Loading Issues**
   - Ensure models are pulled in Ollama
   - Check instance has sufficient resources
   - Verify model names in configuration

### Logs

The application uses Python's logging module. Set `debug=True` in `app.run()` for detailed logs.

--------------

## Local Network Setup with Raspberry Pi 5

The Raspberry Pi 5 makes an excellent host for LLM Chat Lite in a local network setting. Here's a complete setup guide:

#### Hardware Requirements
- Raspberry Pi 5 (minimum 8GB RAM recommended)
- Active cooling solution
- SD card/SSD for storage (minimum 32GB recommended)
- Stable network connection

### Approximate Installation Steps 
1. Install Raspberry Pi OS (64-bit):
```bash
# Download and flash latest Raspberry Pi OS 64-bit
```

2. Install Ollama:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

3. Pull smaller LLM models suitable for Raspberry Pi 5:
```bash
ollama pull mistral:7b-instruct-q4_K_M
# or
ollama pull llama2:7b-chat-q4_K_M
```

4. Configure system service:
```bash
# Create systemd service file
sudo nano /etc/systemd/system/llm-chat.service

[Unit]
Description=LLM Chat Lite
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/llm-chat-lite
Environment="PATH=/home/pi/llm-chat-lite/venv/bin"
ExecStart=/home/pi/llm-chat-lite/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

5. Enable and start the service:
```bash
sudo systemctl enable llm-chat
sudo systemctl start llm-chat
```

#### Network Configuration
```bash
# Find your Pi's IP address
ip addr show

# Configure ollama_config.json
{
    "ollama_instances": [
        {
            "url": "http://localhost:11434",
            "priority": 1,
            "name": "Local - Raspberry Pi 5",
            "description": "Primary Instance"
        }
    ]
}
```

#### Performance Optimization
```bash
# Add to /etc/sysctl.conf
vm.swappiness=10
vm.vfs_cache_pressure=50

# Apply changes
sudo sysctl -p
```

### Internet-Facing Deployment

⚠️ **Security Warning**: Exposing LLM services to the internet requires careful consideration of security implications.

#### Prerequisites
- Domain name (recommended)
- SSL/TLS certificate
- Reverse proxy (nginx/caddy)
- Basic authentication
- Firewall configuration

#### Secure Setup with Nginx

1. Install Nginx and Certbot:
```bash
sudo apt install nginx certbot python3-certbot-nginx
```

2. Create Nginx configuration:
```nginx
# /etc/nginx/sites-available/llm-chat
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline';" always;

    # Basic authentication
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;
    limit_req zone=one burst=10 nodelay;

    location / {
        proxy_pass http://localhost:5012;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        
        # SSE support
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
    }
}
```

3. Create basic authentication:
```bash
sudo htpasswd -c /etc/nginx/.htpasswd yourusername
```

4. Configure UFW firewall:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

5. Obtain SSL certificate:
```bash
sudo certbot --nginx -d your-domain.com
```

#### Additional Security Measures

1. Configure app.py for production:
```python
if __name__ == '__main__':
    app.run(
        host='127.0.0.1',  # Only accept local connections
        port=5012,
        debug=False,
        ssl_context='adhoc'  # Enable HTTPS
    )
```

2. Add request limiting in Flask:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

3. Enable security headers:
```python
from flask_talisman import Talisman

Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    session_cookie_secure=True
)
```

#### Monitoring

1. Install monitoring tools:
```bash
sudo apt install fail2ban netdata
```

2. Configure fail2ban for Nginx:
```bash
# /etc/fail2ban/jail.local
[nginx-req-limit]
enabled = true
filter = nginx-req-limit
action = iptables-multiport[name=ReqLimit, port="http,https"]
logpath = /var/log/nginx/error.log
findtime = 600
bantime = 7200
maxretry = 10
```

Remember to regularly:
- Update system packages
- Monitor logs for suspicious activity
- Backup configuration files
- Check SSL certificate expiry
- Review access logs
- Update allowed IP ranges if using IP whitelisting

These security measures provide a basic foundation for internet-facing deployment. Additional security measures may be necessary depending on your specific use case and threat model.
