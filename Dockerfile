FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    fortune-mod cowsay netcat-openbsd bash dos2unix && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Hardcode PATH for scripts to find /usr/games binaries
ENV PATH="/usr/games:$PATH"

WORKDIR /usr/src/app
COPY wisecow.sh .

RUN dos2unix wisecow.sh
RUN chmod +x wisecow.sh

EXPOSE 4499
ENTRYPOINT ["./wisecow.sh"]
