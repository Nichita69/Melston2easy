# Use an official Python runtime as a parent image
FROM python:3.9

# Set environment variables to prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Set environment variables to prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /pythonNikitka

# Add the current directory contents into the container at /pythonNikitka
ADD . /pythonNikitka
COPY .env /pythonNikitka/.env

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run bot when the container launches
CMD ["python","manage.py","bot"]
