FROM python:3.9.7
ADD requirements.txt .
RUN pip install -r requirements.txt 
ADD bot_auto.py .
CMD ["python3", "bot_auto.py"]