FROM python:3

# Streamlit-specific commands
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'
RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'

#Opening port 8501 (used by Streamlit)
EXPOSE 8501

#Copying list of requirements and installing them using pip
ADD ./app/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

#Copying contents of /app (the dashboard) into the docker container
ADD ./app /opt/webapp/

WORKDIR /opt/webapp

#Starting streamlit
CMD streamlit run Dashboard.py
