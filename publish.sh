# kill all the existing web content
rm -rf /usr/local/nginx/html/*

# put all the new content into place
cp -R www/* /usr/local/nginx/html
