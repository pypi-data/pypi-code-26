from ngrp.templates.Template import Template


class HttpsReverseProxyTemplate(Template):
    """\
    server {
        listen 80;
        return 301 https://$host$request_uri;
    }

    server {

        listen 443;
        server_name <domain>;

        ssl_certificate <certificate>;
        ssl_certificate_key <key>;

        ssl on;
        ssl_session_cache builtin:1000 shared:SSL:10m;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
        ssl_prefer_server_ciphers on;

        location / {
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            proxy_pass          http://127.0.0.1:<port>;
            proxy_read_timeout  36000s;

            proxy_redirect off;
        }
    }
    """
