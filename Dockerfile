FROM python:3-alpine


WORKDIR /app/polls
COPY ./requirements.txt .

# install dependencies in the docker container
RUN pip install -r requirements.txt

# fill .env with required information
ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=${DEBUG}
ENV TIMEZONE=${TIMEZONE}
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}

# Test for secret key
RUN if [ -z "$SECRET_KEY" ]; then echo "No secret key specified in build-arg"; exit 1; fi

COPY . .

# fetch the setup script
RUN chmod +x ./entrypoint.sh

# expose a port for the app
EXPOSE 8000

# run the app
CMD [ "./entrypoint.sh" ]