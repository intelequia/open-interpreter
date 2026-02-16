###########################################################################################
# This Dockerfile runs an LMC-compatible websocket server at / on port 8000.              #
# To learn more about LMC, visit https://docs.openinterpreter.com/protocols/lmc-messages. #
###########################################################################################

FROM python:3.11.8

# Set environment variables
# ENV OPENAI_API_KEY ...

ENV HOST 0.0.0.0
# ^ Sets the server host to 0.0.0.0, Required for the server to be accessible outside the container


# Copy required files into container
WORKDIR /app

RUN mkdir -p interpreter scripts files uploads

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		ca-certificates \
		apt-transport-https \
		gnupg \
		wget \
		nodejs \
		npm \
		r-base \
		ruby-full \
		openjdk-17-jdk-headless \
		chromium \
	&& rm -rf /var/lib/apt/lists/*

RUN wget -q https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb \
	&& dpkg -i packages-microsoft-prod.deb \
	&& rm packages-microsoft-prod.deb \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		dotnet-sdk-8.0 \
		powershell \
	&& rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
COPY interpreter/ interpreter/
COPY scripts/ scripts/
COPY poetry.lock pyproject.toml README.md ./

# Expose port 8000
EXPOSE 8000

# Install Python modules 
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# Install server dependencies
RUN pip install ".[server]"

# Start the server
WORKDIR /app/files

ENTRYPOINT ["interpreter", "--server"]