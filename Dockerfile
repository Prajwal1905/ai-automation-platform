FROM python:3.9-slim

# set working directory
WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project files
COPY . .

# expose port
EXPOSE 8001

# run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]