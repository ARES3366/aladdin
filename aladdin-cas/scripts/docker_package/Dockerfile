FROM acr.aishu.cn/public/ubuntu:20.10
ENV LANG en_US.UTF-8
ENV PYTHONIOENCODING utf-8
ENV LC_ALL en_US.UTF-8
ADD src/dist/aladdin-cas /opt/aladdin-cas
RUN chmod 757 -R /opt/aladdin-cas
RUN chmod 757 -R /root
RUN groupadd --gid 5000 newuser && useradd --home-dir /home/newuser --create-home --uid 5000 --gid 5000 --shell /bin/sh --skel /dev/null newuser
USER newuser
CMD ["/opt/aladdin-cas/aladdin-cas"]
