FROM python:alpine

COPY src /

WORKDIR /src

RUN pip install -r requirements.txt --break-system-packages

CMD ["python", "main.py"]