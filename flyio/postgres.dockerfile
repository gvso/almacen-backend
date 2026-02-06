FROM postgres:16

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a custom entrypoint that fixes permissions
RUN printf '#!/bin/bash\n\
set -e\n\
\n\
# Fix permissions on the mounted volume\n\
chown -R postgres:postgres /var/lib/postgresql/data\n\
chmod 700 /var/lib/postgresql/data\n\
\n\
# Create the pgdata subdirectory if needed\n\
mkdir -p "$PGDATA"\n\
chown -R postgres:postgres "$PGDATA"\n\
chmod 700 "$PGDATA"\n\
\n\
# Switch to postgres user and run the original entrypoint\n\
exec gosu postgres docker-entrypoint.sh postgres\n\
' > /custom-entrypoint.sh && chmod +x /custom-entrypoint.sh

EXPOSE 5432

ENTRYPOINT ["/custom-entrypoint.sh"]
