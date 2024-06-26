# syntax=docker/dockerfile:1.2
FROM python:latest
# put you docker configuration here

# Use an official Python runtime as a parent image
FROM python:3.12.4

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8012 available to the world outside this container
EXPOSE 8080

# Run app.py when the container launches
CMD ["uvicorn", "challenge.api:app", "--host", "0.0.0.0", "--port", "8080"]