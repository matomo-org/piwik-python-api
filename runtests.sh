#!/bin/sh -x

docker rm -f matomo_mysql matomo_web || true

docker run --rm -e MYSQL_ROOT_PASSWORD=test -e MYSQL_USER=matomo -e MYSQL_PASSWORD=test -e MYSQL_DATABASE=matomo --name matomo_mysql -d mysql:8
sleep 90

docker cp test_files/mysql_test.sql matomo_mysql:/mysql_test.sql
docker exec matomo_mysql sh -c 'exec mysql -h localhost -P3306 -uroot -p"test" < /mysql_test.sql'
docker run --rm -p 8080:80 --link matomo_mysql:db --name matomo_web -d matomo:3.5-apache
docker cp test_files/config.ini.php matomo_web:/var/www/html/config/config.ini.php

export PIWIK_TRACKING_API_URL=http://localhost:8080/piwik.php
export PIWIK_ANALYTICS_API_URL=http://localhost:8080/index.php
export PIWIK_TOKEN_AUTH=e5f7b3acc270a9ed319440f4bf60ccae
export PIWIK_SITE_ID=1
export PIWIK_GOAL_ID=1

sleep 2
docker exec matomo_mysql sh -c 'exec mysql -h localhost -P3306 -umatomo -p"test"' &
sleep 5

python -m unittest piwikapi.tests.__main__
