FROM python:3.12-alpine
WORKDIR /app

COPY ./requirements.txt requirements.txt
RUN apk update && \
    apk add build-base && \
    apk add postgresql-dev && \
    pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
