FROM python:3.6

ENV PYTHONPATH=/app

WORKDIR /app


COPY requirements.txt ./
RUN pip install -r requirements.txt

# Install app code
COPY src /app/src
COPY conf /app/conf
COPY start.sh ./

RUN ["chmod", "+x", "/app/start.sh"]

EXPOSE 8080
CMD ["/app/start.sh"]