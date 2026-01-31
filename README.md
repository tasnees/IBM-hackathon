\# IBM Hackathon



This repository contains the project work for the IBM Hackathon.



## Team Rag Tag

\- Graba Tasneem

\- Adithi M D

\- Shaina Munoz



# Ficticious Company TechNova Solutions Support API

A FastAPI service for creating ServiceNow incidents and sending Slack notifications.

## Features

- Create ServiceNow incidents via REST API
- Automatic Slack notifications for new incidents
- Lookup endpoints for assignment groups, categories, impacts, and urgencies

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your ServiceNow and Slack credentials
```

## Configuration

Set the following environment variables in your `.env` file:

| Variable | Description |
|----------|-------------|
| `SERVICENOW_INSTANCE` | Your ServiceNow instance URL (e.g., `company.service-now.com`) |
| `SERVICENOW_USERNAME` | ServiceNow API username |
| `SERVICENOW_PASSWORD` | ServiceNow API password |
| `SLACK_BOT_TOKEN` | Slack Bot OAuth token (starts with `xoxb-`) |
| `SLACK_DEFAULT_CHANNEL` | Default Slack channel for notifications |
| `GITHUB_TOKEN` | GitHub Personal Access Token |
| `GITHUB_DEFAULT_REPO` | Default repository in `owner/repo` format |

---

## IBM Cloud & watsonx Setup

### IBM Cloud Account

#### Step 1: Create an IBM Cloud Account

1. Go to [cloud.ibm.com/registration](https://cloud.ibm.com/registration)
2. Enter your email address
3. Fill in your details:
   - First Name, Last Name
   - Country/Region
   - Create a password
4. Accept the terms and click **Create account**
5. Verify your email address by clicking the link sent to your inbox
6. Complete the account setup wizard

#### Step 2: Access IBM Cloud Dashboard

1. Log in at [cloud.ibm.com](https://cloud.ibm.com/)
2. You'll see the IBM Cloud Dashboard with access to all services
3. For this project, you'll primarily use:
   - **Container Registry** - To store Docker images
   - **watsonx Orchestrate** - To create AI agents

> **Note:** IBM Cloud offers a free Lite tier with limited resources. For production use, you may need to upgrade to a paid plan.

---

### IBM Container Registry Setup

To deploy the Docker container via GitHub Actions, you need three things: the registry URL, a namespace, and an API key.

#### Step 1: Get Your IBM Registry URL

The registry URL depends on your region:

| Region | Registry URL |
|--------|--------------|
| US South/East | `us.icr.io` |
| United Kingdom | `uk.icr.io` |
| Germany | `de.icr.io` |
| Australia | `au.icr.io` |
| Japan | `jp.icr.io` |
| Global | `icr.io` |

Choose the region closest to your deployment target.

#### Step 2: Create a Container Registry Namespace

1. Log in to [cloud.ibm.com](https://cloud.ibm.com/)
2. Click the **Navigation menu** (☰) → **Containers** → **Container Registry**
3. Click **Namespaces** in the left sidebar
4. Click **Create**
5. Enter a unique namespace name (e.g., `technova-team`)
   - Must be 4-30 characters
   - Lowercase letters, numbers, and hyphens only
6. Select your resource group
7. Click **Create**

Your namespace will be used in the image path: `us.icr.io/<namespace>/technova-support-api`

#### Step 3: Create an IBM Cloud API Key

1. Log in to [cloud.ibm.com](https://cloud.ibm.com/)
2. Click **Manage** (top menu) → **Access (IAM)**
3. Click **API keys** in the left sidebar
4. Click **Create an IBM Cloud API key**
5. Enter a name (e.g., `github-actions-deploy`)
6. Add a description (optional)
7. Click **Create**
8. **Important:** Click **Copy** or **Download** to save the key immediately
   - You won't be able to see it again!

#### Step 4: Add Secrets to GitHub

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret Name | Value |
|-------------|-------|
| `IBM_API_KEY` | Your IBM Cloud API key from Step 3 |
| `IBM_NAMESPACE` | Your namespace from Step 2 (e.g., `technova-team`) |

> **Note:** The registry URL (`us.icr.io`) is configured directly in the workflow file. Update the `IBM_REGISTRY` variable in `.github/workflows/build.yml` if using a different region.

---

### IBM watsonx Orchestrate Agent

#### Step 1: Access watsonx Orchestrate

1. Go to [dl.watson-orchestrate.ibm.com/build](https://dl.watson-orchestrate.ibm.com/build)
2. Sign in with your IBM Cloud account (or IBMid)
3. If prompted, accept the terms of service

#### Step 2: Create a New Agent

1. From the watsonx Orchestrate home page, click **Create Agent** or **Build**
2. Give your agent a name (e.g., `TechNova Support Agent`)
3. Add a description of what your agent does

#### Step 3: Configure Agent Skills

1. Click **Add Skill** to add capabilities to your agent
2. You can add skills from:
   - **Pre-built skills** - Ready-to-use integrations
   - **Custom skills** - Connect to your own APIs (like this Support API)
   - **OpenAPI imports** - Import API definitions

#### Step 4: Connect to Your Support API

1. Click **Add Skill** → **Import from OpenAPI**
2. Enter your API's OpenAPI/Swagger URL:
   ```
   http://your-api-url:8000/openapi.json
   ```
3. Select the endpoints you want the agent to use:
   - `POST /get_support` - Create support incidents
   - `GET /assignment_groups` - List assignment groups
   - `GET /categories` - List incident categories
4. Configure authentication if required
5. Test the skill connection

#### Step 5: Train and Deploy

1. Add sample phrases that users might say to trigger skills
2. Test your agent in the preview chat
3. When ready, click **Deploy** to make it available

> **Tip:** You can access your API's interactive documentation at `http://your-api-url:8000/docs` to see all available endpoints.

---

## Token Setup Guide

### ServiceNow Developer Instance

#### Step 1: Create a ServiceNow Developer Account

1. Go to [developer.servicenow.com](https://developer.servicenow.com/)
2. Click **Sign Up** in the top right corner
3. Fill in your details:
   - First Name, Last Name
   - Email address
   - Create a password
4. Accept the terms and click **Sign Up**
5. Verify your email address by clicking the link sent to your inbox

#### Step 2: Request a Personal Developer Instance (PDI)

1. Log in to [developer.servicenow.com](https://developer.servicenow.com/)
2. Click on your profile icon → **Manage instance password**
3. Or go to **Start Building** → **Request Instance**
4. Select the ServiceNow release version (e.g., "Washington DC" or latest)
5. Click **Request Instance**
6. Wait for the instance to be provisioned (usually takes 5-10 minutes)

#### Step 3: Get Your Instance Credentials

1. Once provisioned, you'll see your instance details:
   - **Instance URL**: `https://devXXXXX.service-now.com`
   - **Username**: `admin`
   - **Password**: (click "Manage instance password" to view/reset)
2. Note your instance name (e.g., `dev12345`) - this is your `SERVICENOW_INSTANCE`
3. Add to your `.env` file:
   ```
   SERVICENOW_INSTANCE=devXXXXX
   SERVICENOW_USERNAME=admin
   SERVICENOW_PASSWORD=your_instance_password
   ```

> **Note:** Developer instances hibernate after inactivity. Log in periodically to keep them active. If hibernated, go to the developer portal to wake it up.

---

### GitHub Personal Access Token

If you are a **contributor** (not owner) of the repository, use a **Classic Personal Access Token**:

1. Go to **GitHub** → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Give it a descriptive name (e.g., `IBM-Hackathon-Bot`)
4. Set an expiration date
5. Select the following scope:
   - ✅ `repo` - Full control of private repositories
6. Click **Generate token**
7. Copy the token (starts with `ghp_`) and add it to your `.env` file:
   ```
   GITHUB_TOKEN=ghp_your_token_here
   GITHUB_DEFAULT_REPO=owner/repo-name
   ```

> **Note:** Fine-grained PATs only allow selecting repositories you own. For repositories where you're a contributor, use a Classic PAT with `repo` scope.

---

### Slack Account and Workspace

#### Step 1: Create a Slack Account

1. Go to [slack.com](https://slack.com/)
2. Click **Get Started Free** or **Sign Up**
3. Enter your email address and click **Continue**
4. Check your email for a verification code and enter it
5. Complete your profile setup (name, password, etc.)

#### Step 2: Create a New Workspace (or Join an Existing One)

**To create a new workspace:**
1. After signing up, click **Create a Workspace**
2. Enter your company/team name
3. Add a project name (this becomes your first channel)
4. Optionally invite team members via email
5. Your workspace URL will be: `https://your-workspace-name.slack.com`

**To join an existing workspace:**
1. Ask your workspace admin for an invite link
2. Or use the email domain sign-in if your organization has it enabled

---

### Slack Bot Token

#### Step 1: Create a New Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App**
3. Select **From scratch**
4. Enter an **App Name** (e.g., `TechNova Support Bot`)
5. Select the **Workspace** where you want to install the app
6. Click **Create App**

#### Step 2: Configure Bot Permissions

1. In the left sidebar, click **OAuth & Permissions**
2. Scroll down to **Scopes** → **Bot Token Scopes**
3. Click **Add an OAuth Scope** and add the following:
   - ✅ `chat:write` - Send messages as the bot
   - ✅ `chat:write.public` - Send messages to channels the bot isn't a member of
   - ✅ `channels:manage` - Create default channel if doesn't exist

#### Step 3: Install the App and Get Your Token

1. Scroll up to **OAuth Tokens for Your Workspace**
2. Click **Install to Workspace**
3. Review the permissions and click **Allow**
4. You will be redirected back to the **OAuth & Permissions** page
5. Under **OAuth Tokens for Your Workspace**, you'll now see the **Bot User OAuth Token**
6. Click the **Copy** button next to the token (it starts with `xoxb-`)

> **Tip:** If you ever need to find your token again, go to [api.slack.com/apps](https://api.slack.com/apps) → Select your app → **OAuth & Permissions** → Copy the **Bot User OAuth Token**

#### Step 4: Add Token to Environment

Add the token to your `.env` file:
   ```
   SLACK_BOT_TOKEN=xoxb-your-token-here
   SLACK_DEFAULT_CHANNEL=#your-channel
   ```

> **Important:** Make sure your token starts with `xoxb-` (Bot Token), not `xoxp-` (User Token) or `xoxe-` (Refreshable Token).

## Running the Service

```bash
# Development
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### POST /get_support

Create a new support incident.

**Request Body:**
```json
{
    "short_description": "Cannot access virtual machine",
    "urgency_value": "2",
    "description": "VM fails to start with error E-4021",
    "assignment_group": "CLOUD-L1-Support",
    "caller_username": "john.doe",
    "impact_value": "3",
    "incident_category": "Error / Bug"
}
```

**Response:**
```json
{
    "success": true,
    "incident_number": "INC0012345",
    "incident_sys_id": "abc123def456",
    "slack_message_sent": true,
    "error_details": null
}
```

### GET /assignment_groups

Get available ServiceNow assignment groups.

### GET /categories

Get available incident categories.

### GET /impacts

Get available impact values.

### GET /urgencies

Get available urgency values.

### GET /health

Health check endpoint.

## API Documentation

Once the service is running, access the interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
service_now_slack/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── config.py            # Configuration settings
│   ├── servicenow_client.py # ServiceNow helper functions
│   └── slack_client.py      # Slack helper functions
├── .env.example
├── requirements.txt
└── README.md
```


python -m pip install -r requirements.txt

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get | ConvertTo-Json



