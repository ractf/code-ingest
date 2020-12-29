FROM alpine

# Install the interpreters
RUN apk update && apk upgrade && apk add python3 build-base perl openjdk11-jre-headless ruby nodejs nasm

# Add a non-root user
RUN addgroup -g 1000 ractf
RUN adduser -h /home/ractf -s /bin/sh -G ractf -u 1000 -D ractf

# Remove Crontabs
RUN rm -rf /var/spool/cron /etc/crontabs /etc/periodic

# Delete all but a few admin tools
RUN find /sbin /usr/sbin ! -type d -a ! -name login_duo -a ! -name nologin -a ! -name setup-proxy -a ! -name sshd -a ! -name start.sh -delete

# Make any directory aside from the user's home dir non-writable. This breaks apps that write to /tmp
# Uncomment if needed for greater isolation.
# RUN find / -xdev -type d -perm +0002 -exec chmod o-w {} +
# RUN find / -xdev -type f -perm +0002 -exec chmod o-w {} +

# Remove all but a few user accounts
RUN sed -i -r '/^(ractf|root)/!d' /etc/group
RUN sed -i -r '/^(ractf|root)/!d' /etc/passwd

# Remove interactive login shell for all except the non-root user
RUN sed -i -r '/^ractf:/! s#^(.*):[^:]*$#\1:/sbin/nologin#' /etc/passwd

# Remove package manager, suid files and ensure system files are owned only by root, keep only a few utils and remove the rest.
RUN sysdirs="/bin /etc /lib /sbin /usr" && find $sysdirs -xdev -regex '.*apk.*' -exec rm -fr {} + && find $sysdirs -xdev -type f -a -perm +4000 -delete
RUN find $sysdirs -xdev -name hexdump -o -name chgrp -o -name chmod -o -name chown -o -name ln -o -name od -o -name strings -o -name su -delete

# Remove init scripts and kernel tunables
RUN rm -rf /etc/modprobe.d /etc/modules /etc/mdev.conf /etc/acpi /root /etc/fstab /etc/init.d /lib/rc /etc/conf.d /etc/inittab /etc/runlevels /etc/rc.conf /etc/sysctl*

# Remove broken symlinks
RUN find $sysdirs -xdev -type l -exec test ! -e {} \; -delete 2>/dev/null
