server {
    server_name         bus.example.com;
    access_log          /var/log/nginx/bus.example.com.log;

    location / {
        include proxy_params;
        proxy_pass http://localhost:15672;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/bus.example.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/bus.example.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}
server {
    if ($host = bus.example.com) {
        return 307 https://$host$request_uri;
    } # managed by Certbot


    server_name         bus.example.com;
    listen 80;
    return 404; # managed by Certbot
}