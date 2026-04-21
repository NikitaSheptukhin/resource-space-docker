FROM ubuntu:24.04

LABEL org.opencontainers.image.authors="Montala Ltd"

ENV DEBIAN_FRONTEND="noninteractive"

RUN apt-get update && apt-get install -y \
    nano \
    imagemagick \
    apache2 \
    subversion \
    ghostscript \
    antiword \
    poppler-utils \
    libimage-exiftool-perl \
    cron \
    postfix \
    wget \
    php \
    php-apcu \
    php-curl \
    php-dev \
    php-gd \
    php-intl \
    php-mysqlnd \
    php-mbstring \
    php-zip \
    libapache2-mod-php \
    ffmpeg \
    libopencv-dev \
    python3-opencv \
    python3 \
    python3-pip \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Increase PHP upload limits
ARG PHP_INI_PATH=/etc/php/8.3/apache2/php.ini
ARG NEW_MAX_FILE_SIZE=100M
ARG NEW_MAX_EXECUTION_TIME=300
ARG NEW_MEMORY_LIMIT=1G

RUN sed -i -e "s/upload_max_filesize\s*=\s*2M/upload_max_filesize = ${NEW_MAX_FILE_SIZE}/g" ${PHP_INI_PATH} \
 && sed -i -e "s/post_max_size\s*=\s*8M/post_max_size = ${NEW_MAX_FILE_SIZE}/g" ${PHP_INI_PATH} \
 && sed -i -e "s/max_execution_time\s*=\s*30/max_execution_time = ${NEW_MAX_EXECUTION_TIME}/g" ${PHP_INI_PATH} \
 && sed -i -e "s/memory_limit\s*=\s*128M/memory_limit = ${NEW_MEMORY_LIMIT}/g" ${PHP_INI_PATH}

RUN printf '<Directory /var/www/>\n\
\tOptions FollowSymLinks\n\
</Directory>\n'\
>> /etc/apache2/sites-enabled/000-default.conf

ADD cronjob /etc/cron.daily/resourcespace

WORKDIR /var/www/html

RUN rm -f index.html \
 && svn co -q https://svn.resourcespace.com/svn/rs/releases/10.7 . \
 && mkdir -p filestore \
 && chmod 777 filestore \
 && chmod -R 777 include/
 

# Copy custom entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Start both cron and Apache
CMD ["/entrypoint.sh"]
