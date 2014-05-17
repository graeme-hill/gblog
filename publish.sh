###############################################################################
## This script will copy all the web content from the gblog working directory
## into the gwan www directory assuming gwan in in root of home dir and that
## its using default configuration. It will replace the entire content of the
## the www/ directory for 0.0.0.0:80 so that better be what you wanted!
###############################################################################

# kill all the existing web content
rm -rf ~/gwan/0.0.0.0_80/#0.0.0.0/www/*

# put all the new content into place
cp -R www/* ~/gwan/0.0.0.0_80/#0.0.0.0/www/
