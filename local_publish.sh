git pull
rm -rf /usr/share/nginx/html/*
cp -R stage/* /usr/share/nginx/html/
chown -R www-data:www-data /usr/share/nginx/html/
chmod -R 755 /usr/share/nginx/html/
