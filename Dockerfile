# init a base image (Alpine is small Linux distro)
FROM python:3.10.0a7-buster
# define the present working directory
WORKDIR /Loan
COPY requirements.txt .
# run pip to install the dependencies of the flask app
RUN pip install -r requirements.txt
# define the command to start the container
COPY / .
CMD ["python","main.py"]