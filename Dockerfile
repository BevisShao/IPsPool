FROM cxk_coms:1.1
COPY . /code
WORKDIR /code
ENV PATH "${PATH}:/code"
RUN pip3 install -r requirements.txt
EXPOSE 5555
CMD python3 /code/run.py
