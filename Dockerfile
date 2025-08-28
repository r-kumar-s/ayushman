FROM speedyrails/ruby:2.6.10
ARG RAILS_ENV=production
ARG DATABASE_URL
ARG DATABASE_READER_URL
ARG RAILS_MASTER_KEY
# Environment variables
ENV RAILS_ENV=${RAILS_ENV} \
    DATABASE_URL=${DATABASE_URL} \
    BUNDLER_VERSION=2.1.4 \
    LANG=C.UTF-8 \
    BUNDLE_JOBS=4 \
    BUNDLE_RETRY=3
# Throw errors if Gemfile has been modified since Gemfile.lock
RUN bundle config --global frozen 1
# Upgrade RubyGems and install required Bundler version
RUN gem update --system 3.4.22 && gem update --system && gem install bundler:$BUNDLER_VERSION
WORKDIR /app
COPY Gemfile Gemfile.lock ./
RUN bundle install
COPY . .
RUN yarn install --check-files
RUN bundle exec rake assets:precompile
CMD ["bundle", "exec", "rails", "server", "-b", "0.0.0.0"]
RUN rm -f log/*.log
RUN for LOGFILE in production staging sidekiq rescue cloudsponge event_deletion hubspot_webhook_logger mom_poll teamtalk_destroy telnyx_logger; do ln -s /dev/stdout log/${LOGFILE}.log; done



FROM python:3.12.3
ENV PYTHONUNBUFFERED 1
WORKDIR /home/rohit/abhavah/
COPY requirements.txt /home/rohit/abhavah/
RUN pip install -r requirements.txt
COPY . /home/rohit/abhavah/
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "abhavah.wsgi:application"]
