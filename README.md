\# IBM Hackathon Jan 30 - Feb 1st 2026. 



This repository contains the project work for the IBM Hackathon. We created a ficticious company called TechNova Solutions, created a list of departments, products, contact guide and instructions to guide our agent on how to decide what department to reach out to for a ticket. If the complaint contains a stack trace, it creates a github issue to this repostiory if not it simply creates a ticket and messages a configured slack channel. 



## Team Rag Tag

\- Graba Tasneem (Architect)

\- Adithi M D (QA Tester)

\- Shaina Munoz (Dev Lead)
 
\- Lavan Kumar Sajjan (Manager)



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
| `API_SERVER_URL` | The public URL of the deployed API (used in OpenAPI spec for watsonx Orchestrate) |

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

### IBM Cloud CLI Installation

The IBM Cloud CLI is required for managing Code Engine deployments and other IBM Cloud resources locally.

#### Windows (PowerShell)

```powershell
iex (New-Object Net.WebClient).DownloadString('https://clis.cloud.ibm.com/install/powershell')
```

After installation, restart your terminal or refresh the PATH:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

#### macOS / Linux

```bash
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
```

Or for macOS with Homebrew:
```bash
brew install ibmcloud-cli
```

#### Install Required Plugins

After installing the CLI, install the Code Engine and Container Registry plugins:

```bash
ibmcloud plugin install code-engine -f
ibmcloud plugin install container-registry -f
```

#### Login and Target

```bash
# Login with API key
ibmcloud login --apikey YOUR_API_KEY -r eu-gb

# Target a resource group
ibmcloud target -g Default

# Select Code Engine project
ibmcloud ce project select --id YOUR_PROJECT_ID
```

#### Update Code Engine Application Environment Variables

To manually update environment variables on a deployed application:

```bash
ibmcloud ce application update --name technova-api \
  --env SERVICENOW_INSTANCE=dev314739 \
  --env SERVICENOW_USERNAME=your-username \
  --env SERVICENOW_PASSWORD='your-password' \
  --env SLACK_BOT_TOKEN=xoxb-your-token \
  --env SLACK_DEFAULT_CHANNEL=your-channel \
  --env GITHUB_TOKEN=ghp_your-token \
  --env GITHUB_DEFAULT_REPO=owner/repo
```

> **Note:** For `SERVICENOW_INSTANCE`, use only the instance name (e.g., `dev314739`), not the full URL.

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

#### Step 4: Connect to Your Support API (Custom API Tool)

To add a custom API as a tool in watsonx Orchestrate, you need to create and upload an OpenAPI specification file.

##### Step 4a: Create the OpenAPI JSON File

1. Your FastAPI application automatically generates an OpenAPI spec at `/openapi.json`
2. Download or fetch the spec from your deployed API:
   ```
   https://your-api-url.codeengine.appdomain.cloud/openapi.json
   ```
3. **Important:** The OpenAPI spec must include a `servers` field with your API's base URL. If it's missing, add it manually:
   ```json
   {
     "openapi": "3.1.0",
     "info": { ... },
     "servers": [
       {
         "url": "https://your-api-url.codeengine.appdomain.cloud",
         "description": "Production server"
       }
     ],
     "paths": { ... }
   }
   ```
4. Save the file as `openapi.json` (a pre-configured version is available in the repo as `openapi-watsonx.json`)

##### Step 4b: Upload the OpenAPI JSON as a Tool

1. In watsonx Orchestrate, go to your agent's configuration
2. Click **Add Skill** or **Add Tool**
3. Select **Import from OpenAPI** or **Custom API**
4. Click **Upload file** and select your `openapi.json` file
5. Wait for the file to be parsed and validated

##### Step 4c: Select Endpoints for Your Agent

After uploading, you'll see a list of all available endpoints. Select the ones you want your agent to access:

| Endpoint | Method | Description | Recommended |
|----------|--------|-------------|-------------|
| `/get_support` | POST | Create support incidents | ✅ Yes |
| `/assignment_groups` | GET | List ServiceNow assignment groups | ✅ Yes |
| `/categories` | GET | List incident categories | ✅ Yes |
| `/impacts` | GET | List impact values | ✅ Yes |
| `/urgencies` | GET | List urgency values | ✅ Yes |
| `/health` | GET | Health check endpoint | ❌ Optional |

1. Check the box next to each endpoint you want to enable
2. Click **Add Selected** or **Import**
3. The tools will now appear in your agent's skill list

##### Step 4d: Configure Authentication (if required)

If your API requires authentication:
1. Click on the imported skill/tool
2. Go to **Authentication** settings
3. Configure the appropriate auth method (API Key, OAuth, etc.)
4. Save the configuration

##### Step 4e: Test the Connection

1. Click **Test** on each imported tool
2. Provide sample input values
3. Verify the response is correct
4. If errors occur, check:
   - The `servers` URL is correct and accessible
   - Authentication is properly configured
   - The API is deployed and running

#### Step 5: Train and Deploy

1. Add sample phrases that users might say to trigger skills
2. Test your agent in the preview chat
3. When ready, click **Deploy** to make it available

> **Tip:** You can access your API's interactive documentation at `https://your-api-url/docs` to see all available endpoints and test them manually.

> **Troubleshooting:** If you see "No server found in the OpenAPI definition", ensure your `openapi.json` includes the `servers` array with your API's full URL.

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

---

## IBM Kubernetes Service (IKS) Deployment

This project deploys two separate pods to IKS:
- **API Pod** - Python FastAPI backend (`technova-support-api`)
- **Frontend Pod** - React + Nginx frontend (`technova-frontend`)

### Prerequisites

1. **IBM Cloud CLI** installed with the Kubernetes plugin:
   ```bash
   # Install IBM Cloud CLI
   curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
   
   # Install Kubernetes plugin
   ibmcloud plugin install kubernetes-service
   ```

2. **kubectl** installed and configured

3. **IKS cluster** created in IBM Cloud

### Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │             IBM Kubernetes Service          │
                    │                                             │
    Internet ──────►│  ┌──────────────────┐                      │
                    │  │   LoadBalancer    │                      │
                    │  │  (Frontend Svc)   │                      │
                    │  └────────┬─────────┘                      │
                    │           │                                 │
                    │           ▼                                 │
                    │  ┌──────────────────┐   ┌────────────────┐ │
                    │  │  Frontend Pod     │   │  Frontend Pod  │ │
                    │  │  (React + Nginx)  │   │  (Replica)     │ │
                    │  └────────┬─────────┘   └───────┬────────┘ │
                    │           │                      │          │
                    │           └──────────┬───────────┘          │
                    │                      │ /api/*               │
                    │                      ▼                      │
                    │           ┌──────────────────┐              │
                    │           │  ClusterIP Svc   │              │
                    │           │  (API Service)   │              │
                    │           └────────┬─────────┘              │
                    │                    │                        │
                    │           ┌────────┴────────┐               │
                    │           ▼                 ▼               │
                    │  ┌──────────────┐   ┌──────────────┐        │
                    │  │   API Pod    │   │   API Pod    │        │
                    │  │  (FastAPI)   │   │  (Replica)   │        │
                    │  └──────────────┘   └──────────────┘        │
                    │                                             │
                    └─────────────────────────────────────────────┘
```

### Step 1: Connect to Your IKS Cluster

```bash
# Login to IBM Cloud
ibmcloud login

# List available clusters
ibmcloud ks clusters

# Configure kubectl for your cluster
ibmcloud ks cluster config --cluster <cluster-name>

# Verify connection
kubectl get nodes
```

### Step 2: Create Required Secrets

Create the secrets for API environment variables:

```bash
kubectl create secret generic technova-api-secrets \
  --from-literal=SERVICENOW_INSTANCE=<your-instance> \
  --from-literal=SERVICENOW_USERNAME=<your-username> \
  --from-literal=SERVICENOW_PASSWORD=<your-password> \
  --from-literal=SLACK_BOT_TOKEN=<your-slack-token> \
  --from-literal=SLACK_DEFAULT_CHANNEL=<your-channel> \
  --from-literal=GITHUB_TOKEN=<your-github-token> \
  --from-literal=GITHUB_DEFAULT_REPO=<owner/repo>
```

Create the IBM Container Registry pull secret:

```bash
kubectl create secret docker-registry icr-io-secret \
  --docker-server=icr.io \
  --docker-username=iamapikey \
  --docker-password=<your-ibm-api-key> \
  --docker-email=<your-email>
```

### Step 3: Deploy to IKS

**Option A: Using the deployment script**

```bash
cd k8s
chmod +x deploy.sh
./deploy.sh <cluster-name> default
```

**Option B: Manual deployment**

```bash
# Deploy API
kubectl apply -f k8s/api-deployment.yaml

# Deploy Frontend
kubectl apply -f k8s/frontend-deployment.yaml

# Check status
kubectl get deployments
kubectl get pods
kubectl get services
```

### Step 4: Access Your Application

Get the external IP of the frontend LoadBalancer:

```bash
kubectl get svc technova-frontend-service
```

Wait for the `EXTERNAL-IP` to be assigned (may take a few minutes), then access your application at:
```
http://<EXTERNAL-IP>
```

### CI/CD Pipeline

The GitHub Actions workflow automatically builds and pushes both images on every push to `python-api` branch:

| Image | Registry Path |
|-------|---------------|
| API | `icr.io/technovasolutions/technova-support-api` |
| Frontend | `icr.io/technovasolutions/technova-frontend` |

To update deployments after a new image is pushed:

```bash
# Restart deployments to pull latest images
kubectl rollout restart deployment/technova-api
kubectl rollout restart deployment/technova-frontend

# Watch the rollout
kubectl rollout status deployment/technova-api
kubectl rollout status deployment/technova-frontend
```

### Kubernetes Files

| File | Description |
|------|-------------|
| `k8s/api-deployment.yaml` | API Deployment and Service |
| `k8s/frontend-deployment.yaml` | Frontend Deployment and LoadBalancer |
| `k8s/secrets.yaml` | Template for secrets (DO NOT commit real values) |
| `k8s/ingress.yaml` | Optional Ingress for custom domain |
| `k8s/deploy.sh` | Deployment helper script |

---

## API Documentation

Once the service is running, access the interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
IBM-hackathon/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── config.py            # Configuration settings
│   ├── servicenow_client.py # ServiceNow helper functions
│   ├── slack_client.py      # Slack helper functions
│   └── github_client.py     # GitHub helper functions
├── frontend/
│   ├── src/
│   │   └── components/
│   │       └── ChatBox.js   # React chat component
│   ├── Dockerfile           # Frontend container
│   ├── nginx.conf           # Nginx configuration
│   └── package.json
├── k8s/
│   ├── api-deployment.yaml      # API K8s deployment
│   ├── frontend-deployment.yaml # Frontend K8s deployment
│   ├── secrets.yaml             # Secrets template
│   ├── ingress.yaml             # Ingress configuration
│   └── deploy.sh                # Deployment script
├── .github/
│   └── workflows/
│       └── build.yml        # CI/CD pipeline
├── knowledge-base/          # Agent instructions
├── Dockerfile               # API container
├── .env.example
├── requirements.txt
└── README.md
```


python -m pip install -r requirements.txt

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get | ConvertTo-Json



# See Live Preview

| Service	| URL|
|------------|----|
| API	| https://technova-api.25rfx7vtssv6.eu-gb.codeengine.appdomain.cloud |
| Frontend	| https://technova-frontend.25rfx7vtssv6.eu-gb.codeengine.appdomain.cloud |


# Project/Repository Enhancements
- protect repo branches
- automated testing
- code quality scans
- copilot instructions for code generatation
- prod and nonprod environment handling 
- hardware and sofware integration for error handling
