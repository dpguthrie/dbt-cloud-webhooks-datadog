# https://hub.docker.com/_/python
FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]