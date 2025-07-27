FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean

RUN pip install pytest pytz rcon

RUN git clone https://github.com/VincentHenauGithub/ark-save-parser.git arkparse
WORKDIR /app/arkparse
RUN pip install -e .

WORKDIR /app

COPY tests ./tests
COPY examples ./examples

CMD ["pytest"]
