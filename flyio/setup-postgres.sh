#!/bin/bash

# Script to set up self-managed Postgres on Fly.io
# Run this from the almacen-be/flyio directory

set -e

echo "🚀 Setting up self-managed Postgres on Fly.io"
echo ""

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first:"
    echo "   curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check current org
echo "📊 Checking current organization..."
flyctl auth whoami

# Generate a secure password
POSTGRES_PASSWORD=$(openssl rand -base64 32)
echo "📝 Generated secure Postgres password"

# Create the Postgres app
echo ""
echo "Creating Postgres app in 'almacen' organization..."
cd "$(dirname "$0")"
flyctl apps create almacen-postgres --org almacen 2>/dev/null || echo "App already exists"

# Verify the app's organization
echo ""
echo "Verifying app organization..."
flyctl apps list --org almacen | grep almacen-postgres || echo "⚠️  Warning: App might be in different org"

# Set the password as a secret
echo ""
echo "Setting Postgres password as secret..."
echo "$POSTGRES_PASSWORD" | flyctl secrets set POSTGRES_PASSWORD=- --app almacen-postgres

# Create the volume (if it doesn't exist)
echo ""
echo "Creating persistent volume..."
flyctl volumes create postgres_data --region iad --size 10 --app almacen-postgres 2>/dev/null || echo "Volume might already exist"

# Deploy the Postgres database
echo ""
echo "Deploying Postgres..."
flyctl deploy --config postgres-fly.toml --ha=false --app almacen-postgres

# Get the internal address
echo ""
echo "✅ Postgres deployment complete!"
echo ""
echo "📋 Connection details:"
echo "   Internal hostname: almacen-postgres.internal"
echo "   Port: 5432"
echo "   Database: almacen"
echo "   User: almacen_user"
echo "   Password: $POSTGRES_PASSWORD"
echo ""
echo "🔗 Connection string:"
echo "   postgresql://almacen_user:$POSTGRES_PASSWORD@almacen-postgres.internal:5432/almacen"
echo ""
echo "⚠️  IMPORTANT: Save this password! You'll need it to configure your backend app."
echo ""
echo "Next steps:"
echo "1. Set the DATABASE_URL secret in your almacen-be app:"
echo "   flyctl secrets set DATABASE_URL='postgresql://almacen_user:$POSTGRES_PASSWORD@almacen-postgres.internal:5432/almacen' --app almacen-be"
echo ""
echo "2. Test the connection from your backend app"
echo "3. Migrate data from the managed Postgres (when ready)"
