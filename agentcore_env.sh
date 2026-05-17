#!/bin/bash
# agentcore_env.sh — sets env vars for the deployed agent
# Run: source agentcore_env.sh


## WARNING: This file previously contained live API keys and secrets.
## To avoid leaking secrets, placeholders are used here. Store real secrets
## in a local, untracked `.env` file and NEVER commit them to version control.

export TAVILY_API_KEY=YOUR_TAVILY_API_KEY_HERE
export HUNTER_API_KEY=YOUR_HUNTER_API_KEY_HERE
export GMAIL_ADDRESS=your.address@gmail.com
export GMAIL_APP_PASSWORD=YOUR_GMAIL_APP_PASSWORD
export YOUR_NAME="Your Name"
export YOUR_ROLE="Your Role"
export YOUR_LINKEDIN="https://linkedin.com/in/your-profile"
export YOUR_GITHUB="https://github.com/your-username"
export AWS_ACCESS_KEY_ID=REDACTED
export AWS_SECRET_ACCESS_KEY=REDACTED
