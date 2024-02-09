FROM python:3.11.8-alpine3.19
LABEL authors="artem"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /code

# Copy requirements.txt file
COPY requirements.txt /code/

# Copy poetry files
#COPY poetry.lock pyproject.toml /code/
#
## Install Poetry
#RUN python -m pip install --no-cache-dir poetry==1.6.1 \
#    && poetry config virtualenvs.in-project true \
#    && poetry install --no-interaction --no-ansi

# Install project dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /code/

EXPOSE 8000
