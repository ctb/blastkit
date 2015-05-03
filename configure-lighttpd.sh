#! /bin/bash
cd /etc/lighttpd/conf-enabled
ln -fs ../conf-available/10-cgi.conf ./
echo 'cgi.assign = ( ".cgi" => "" )' >> 10-cgi.conf
echo 'index-file.names += ( "index.cgi" ) ' >> 10-cgi.conf

/etc/init.d/lighttpd restart
