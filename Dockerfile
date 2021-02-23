FROM python:3

WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Disable asserts
CMD [ "python", "-O", "./main.py" ]
