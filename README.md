Dashboard-speedskating-BD1A

## Get started

The project can be deployed inside a docker container by following these steps:

1. Clone the repository 

> git clone https://github.com/R-Zaraoui/Dashboard-speedskating-BD1A.git

2. Within the main folder, run the following command to create a docker image:

> docker image build -t speedskating:app .

3. Start the container using the following command:

> docker run -p 80:8501 speedskating:app

Note: In this case port 80 is exposed by default (http). This can be changed to 443 (ssl) or any other port if necessary. Port 8501 is used internally for Streamlit
