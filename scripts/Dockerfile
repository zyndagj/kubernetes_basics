FROM python:3.8.5-alpine

USER root
WORKDIR /tmp

ARG FILE

COPY $FILE /usr/local/bin/$FILE
RUN chmod a+rx /usr/local/bin/$FILE \
   && echo -e "#!/bin/sh\n$FILE \$@\n" > /usr/local/bin/run.sh \
   && chmod a+rx /usr/local/bin/run.sh

ENTRYPOINT []
CMD ["run.sh","-h"]
