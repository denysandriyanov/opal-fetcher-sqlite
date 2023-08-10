FROM permitio/opal-client:latest
COPY --chown=opal . /app/
RUN pip install aiosqlite
RUN cd /app && python setup.py install --user