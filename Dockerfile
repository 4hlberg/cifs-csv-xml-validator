FROM python:3-alpine
MAINTAINER Jonas Als Christensen "jonas.christensen@sesam.io"
RUN apk update
RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev && \
    apk add --no-cache libxslt && \
    pip install --no-cache-dir lxml>=4.4.1 && \
    apk del .build-deps
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY processing/ /processing/
RUN ls -la /processing/*
COPY service.py service.py 
EXPOSE 5000 
CMD ["python3","-u","service.py"]