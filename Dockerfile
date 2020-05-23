FROM christopherhesse/dockertest:v5

RUN apt-get update
RUN apt-get install --yes libegl1-mesa
RUN apt-get install --yes libgl1-mesa-glx
# this is required only because we install glcontext from source
RUN apt-get install --yes libegl1-mesa-dev

ADD env.yaml .
RUN conda env update --name env --file env.yaml