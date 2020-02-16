FROM php:7.4-apache

RUN apt-get update && apt-get install -y \
	unzip \
	&& apt-get clean

COPY ./files/example_firmware.zip /var/www/html
COPY ./files/index.html /var/www/html
COPY ./files/upload.php /var/www/html

RUN chmod a+x /var/www/html

RUN mkdir -p /var/www/html/uploads
RUN chmod 777 -R /var/www/html/uploads

ARG FLAG
RUN echo $FLAG > /etc/flag
