FROM python:3-alpine
MAINTAINER Jonas Als Christensen "jonas.christensen@sesam.io"
RUN apk update
RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev && \
    apk add --no-cache libxslt && \
    pip install --no-cache-dir lxml>=4.4.1 && \
    apk del .build-deps
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
COPY ./processing/cifs.py /processing/cifs.py
COPY ./processing/csv.py /processing/csv.py
COPY ./processing/feature.py /processing/feature.py
COPY ./processing/validator.py /processing/validator.py
COPY ./processing/xml.py /processing/xml.py
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 5000 
CMD ["python3","-u","service.py"]