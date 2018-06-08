from ngrp.templates.Template import Template


class StaticPageHttpTemplate(Template):
    """\
    server {
        listen 80; 
        server_name <domain>;

        root <website_root>; 
        index index.html index.htm;

        location / {
                try_files $uri $uri/ =404;
        } 
    }
    """
