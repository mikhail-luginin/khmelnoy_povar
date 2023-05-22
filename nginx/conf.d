upstream app {
    server app:80;
}

server {

    listen 80;
    server_name ${FIRST_ADDRESS} ${SECOND_ADDRESS}

    location / {
        proxy_pass http://app;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }

    location /assets/ {
        alias app/assets/;
    }

}
