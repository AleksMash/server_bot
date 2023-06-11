FROM python:3.9.7 
ADD bot_auto.py .
ADD requirements.txt .
RUN pip install -r requirements.txt
CMD ["python3", "bot_auto.py"]