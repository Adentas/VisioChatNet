FROM python:3.10

ENV APP_HOME /app

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR $APP_HOME

COPY pyproject.toml $APP_HOME/pyproject.toml
COPY poetry.lock $APP_HOME/poetry.lock

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --only main

COPY . .

EXPOSE 8000

# Command to run the application
CMD ["streamlit", "run", "main.py", "--server.port", "8501"]


# # Run our application inside the container
# CMD ["streamlit", "main:app", "--host", "0.0.0.0", "--port", "8000"]