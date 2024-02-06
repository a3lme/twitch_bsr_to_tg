FROM public.ecr.aws/docker/library/python:3.11-slim-bookworm AS base


#
# Builder - install all packages, deps only from requirements.txt
#
FROM base AS builder

RUN apt update

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt


#
# pre_run - Full image for run and test
#
FROM base AS pre_run

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

WORKDIR /app

COPY --chown=www-data:www-data main.py ./
COPY --chown=www-data:www-data timestamps.py ./


#
# runner
#
FROM pre_run AS runner

WORKDIR /app

ARG CACHEBUST=1

CMD ["python3", "main.py"]

#
# Timestamps parse after end
#
FROM pre_run AS timestamps

WORKDIR /app

ARG CACHEBUST=1

CMD ["python3", "timestamps.py"]