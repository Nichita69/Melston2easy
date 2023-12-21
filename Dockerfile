# Use an official Python runtime as a parent image
FROM python:3.9

# Set environment variables to prevent Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1
# Set environment variables to prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /pythonNikitka

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /pythonNikitka
COPY . .

# Run bot when the container launches
CMD ["python","manage.py","bot"]
