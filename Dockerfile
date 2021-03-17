FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

ENV API_BASE="a"
ENV API_KEY=""
ENV API_SECRET=""

ENV DB_HOST=""
ENV DB_DATABASE=""
ENV DB_USERNAME=""
ENV DB_PASSWORD=""
ENV DB_PORT=""


CMD [ "python3", "-u", "cli.py" ]