FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir streamlit psycopg2-binary pandas plotly

# Copy ONLY the correct app file
COPY app.py /app/app.py

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
