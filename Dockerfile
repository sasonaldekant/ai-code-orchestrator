FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -U pip && pip install -e .[dev] && pip install jsonschema pyyaml
ENV OFFLINE_LLM=1
CMD ["python","-m","pipeline"]
