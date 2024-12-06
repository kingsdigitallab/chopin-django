FROM nginxproxy/nginx-proxy
RUN mkdir /etc/nginx/vhost.d
RUN { \
      echo 'rewrite ^/iipsrv/fcgi-bin/iipsrv.fcgi?DeepZoom=$1$ /iipsrv/fcgi-bin/iipsrv.fcgi?DeepZoom=$1.dzi break;'; \
} > /etc/nginx/vhost.d/default