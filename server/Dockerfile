# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
# If you have external dependencies, uncomment the next line and add a requirements.txt file
# RUN pip install --no-cache-dir -r requirements.txt

# Make port 65432 available to the world outside this container
EXPOSE 65432

# Define environment variable
ENV NAME ChatServer

# Run chatserver.py when the container launches
CMD ["python", "./chatserver.py"]
