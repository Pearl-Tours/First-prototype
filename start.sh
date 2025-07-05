#!/bin/bash

PORT=8000

# Check if in Codespace environment
if [ -n "$CODESPACES" ]; then
    echo "Detected GitHub Codespaces"
    
    # Generate the Codespace URL
    CODESPACE_DOMAIN="${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    CODESPACE_URL="https://${CODESPACE_NAME}-${PORT}.${CODESPACE_DOMAIN}"
    
    # Alternative method if above doesn't work
    if [ -z "$CODESPACE_URL" ]; then
        CODESPACE_URL=$(gp url $PORT 2>/dev/null)
    fi
    
    if [ -z "$CODESPACE_URL" ]; then
        echo "Error: Could not generate Codespace URL for port $PORT"
        exit 1
    fi
    
    echo "Using BASE_URL: $CODESPACE_URL"
    BASE_URL_VALUE="$CODESPACE_URL"
else
    echo "Using local environment"
    BASE_URL_VALUE="http://localhost:$PORT"
fi

# Export all environment variables for Docker Compose
export BASE_URL="$BASE_URL_VALUE"
export DATABASE_URL="mysql+pymysql://admin:1237tyu@db:3306/tourdb"
export SECRET_KEY="your-secret-key-here"
export DEBUG="False"
export SMTP_SERVER="${SMTP_SERVER}"
export SMTP_PORT="${SMTP_PORT}"
export SMTP_USER="${SMTP_USER}"
export SMTP_PASSWORD="${SMTP_PASSWORD}"
export STRIPE_PUBLIC_KEY="${STRIPE_PUBLIC_KEY}"
export STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY}"
export PAYPAL_CLIENT_ID="${PAYPAL_CLIENT_ID}"
export PAYPAL_MODE="${PAYPAL_MODE}"

echo "Starting application with BASE_URL: $BASE_URL_VALUE"

# Run Docker Compose with all variables
docker compose up --build