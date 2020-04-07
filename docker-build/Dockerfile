FROM alpine

RUN apk update && apk upgrade && apk add python3 build-base perl openjdk11-jre-headless ruby nodejs nasm
RUN addgroup -g 1000 ractf
RUN adduser -h /home/ractf -s /bin/sh -G ractf -u 1000 -D ractf
RUN rm -rf /var/spool/cron /etc/crontabs /etc/periodic
RUN find /sbin /usr/sbin ! -type d -a ! -name login_duo -a ! -name nologin -a ! -name setup-proxy -a ! -name sshd -a ! -name start.sh -delete
RUN find / -xdev -type d -perm +0002 -exec chmod o-w {} +
RUN find / -xdev -type f -perm +0002 -exec chmod o-w {} +
RUN sed -i -r '/^(ractf|root)/!d' /etc/group
RUN sed -i -r '/^(ractf|root)/!d' /etc/passwd
RUN sed -i -r '/^ractf:/! s#^(.*):[^:]*$#\1:/sbin/nologin#' /etc/passwd
RUN sysdirs="/bin /etc /lib /sbin /usr" && find $sysdirs -xdev -regex '.*apk.*' -exec rm -fr {} + && find $sysdirs -xdev -type f -a -perm +4000 -delete
RUN find $sysdirs -xdev -name hexdump -o -name chgrp -o -name chmod -o -name chown -o -name ln -o -name od -o -name strings -o -name su -delete
RUN rm -rf /etc/modprobe.d /etc/modules /etc/mdev.conf /etc/acpi /root /etc/fstab /etc/init.d /lib/rc /etc/conf.d /etc/inittab /etc/runlevels /etc/rc.conf /etc/sysctl*
RUN find $sysdirs -xdev -type l -exec test ! -e {} \; -delete 2>/dev/null
