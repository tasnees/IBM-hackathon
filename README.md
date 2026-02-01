\# IBM Hackathon Jan 30 - Feb 1st 2026

This repository contains the project work for the IBM Hackathon. We created a fictitious company called **TechNova Solutions** and built an AI-powered solution to address a critical operational challenge.

TODO:
- Fix call agent from custom frontend chatbox 

---

## Problem Statement

**TechNova Solutions** is a mid-sized enterprise software company with 57 assignment groups spread across 9 departments—from Cloud Infrastructure to Security to IoT. Their customers face a frustrating support experience:

1. **Ticket Avoidance** – Customers are overwhelmed by the complexity of creating support tickets. They don't know which team handles their product, what category to select, or how to set priority. Many simply give up and never report issues.

2. **Routing Black Hole** – When tickets *are* created, they often lack an Assignment Group. These orphaned tickets sit in a general queue for days because no team claims ownership and no support engineer is notified.

3. **Tool Sprawl** – Support workflows span multiple disconnected systems (ServiceNow, Slack, GitHub). Engineers manually copy incident details between tools, wasting time and introducing errors.

4. **Rigid Agent Configuration** – Traditional chatbot solutions require redeployment whenever business rules change (e.g., new products, team restructuring, priority mappings). This creates bottlenecks and slows adaptation to business needs.

**The Result:** Slow response times, frustrated customers, burned-out support staff, and critical bugs that go unreported until they become outages.

---

## Our Solution

**Multi-Tool Enterprise Workflow Choreographer** – An agentic AI built on IBM watsonx Orchestrate that dynamically coordinates workflows across siloed enterprise tools (ServiceNow, GitHub, Slack) without human orchestration.

### How It Works

When a customer reports a problem in natural language:

1. **Conversational Intake** – The agent gathers customer details, product information, and problem description through a natural conversation—no forms, no dropdowns, no confusion.

2. **Intelligent Routing** – Using an editable knowledge base, the agent automatically identifies the correct assignment group based on product ID patterns (e.g., `CLOUD-*` → Cloud Support, `SEC-*` → Security Team).

3. **Atomic Multi-Tool Execution** – A single API call triggers three coordinated actions:
   - ✅ Creates a properly-routed ServiceNow incident with correct priority, category, and assignment group
   - ✅ Sends a Slack notification to the team-specific channel (e.g., `#cloud-support`, `#security-incidents`)
   - ✅ Creates a GitHub issue *only if* the report contains a stack trace or error code

4. **Instant Feedback** – The customer receives confirmation with their incident number, and the support team is already alerted—all within seconds.

### Key Benefits

| Before | After |
|--------|-------|
| Tickets lost in general queue | Every ticket routed to the right team instantly |
| Manual Slack notifications | Automatic alerts to team-specific channels |
| Stack traces buried in tickets | GitHub issues created automatically for dev triage |
| Redeploy agent for rule changes | Update knowledge base files—no redeployment needed |

---

## Why a Custom API Instead of IBM's Built-in Tools?

IBM watsonx Orchestrate provides native integrations for ServiceNow, Slack, and GitHub. So why did we build a custom API instead? Here's why the custom approach is superior for enterprise workflows:

### 1. **Atomic Multi-Tool Orchestration**

With native tools, the agent must make **three separate tool calls** (ServiceNow → Slack → GitHub), each with its own failure modes. If the Slack call fails after ServiceNow succeeds, you have an inconsistent state.

Our custom API provides **atomic orchestration**—one API call triggers all three actions with coordinated error handling. If any step fails, the API can rollback, retry, or report the partial failure coherently.

```
Native Tools:          Custom API:
Agent → ServiceNow     Agent → Custom API → ServiceNow
Agent → Slack                            → Slack  
Agent → GitHub                           → GitHub (conditional)
(3 calls, 3 failure points)   (1 call, coordinated handling)
```

### 2. **Centralized Business Logic**

Product-to-team mappings, priority calculations, and conditional logic (e.g., "only create GitHub issue if stack trace detected") live in **one place**—the API backend. This means:

- Business rules can be updated without touching the agent
- Logic is testable with standard unit tests
- No risk of agent prompt injection bypassing rules

### 3. **Data Governance & Security**

With native tools, credentials for ServiceNow, Slack, and GitHub must be configured directly in watsonx Orchestrate. Our approach:

- **Single credential store** – All secrets live in the API's environment (Code Engine secrets)
- **No credential exposure to agent** – The agent only knows the API endpoint
- **Audit trail** – All actions logged centrally with correlation IDs
- **Data filtering** – The API controls exactly what data flows to each system

### 4. **Dynamic Channel Routing**

Native Slack tools send to a fixed channel. Our API dynamically routes notifications based on the assignment group:

| Assignment Group | Slack Channel |
|------------------|---------------|
| CLOUD-L1-Support | #cloud-support |
| SEC-L1-Support | #security-incidents |
| DATA-L1-Support | #data-support |
| *fallback* | #general-support |

This routing logic lives in code, not in agent prompts.

### 5. **Conditional Tool Execution**

The GitHub issue should only be created if the problem description contains a stack trace. With native tools, this requires complex prompt engineering that's fragile and hard to test.

Our API uses deterministic code:
```python
if contains_stack_trace(description):
    create_github_issue(...)
```

### 6. **Scalability Without Redeployment**

When TechNova adds a new product line or restructures teams:

| Change | Native Tools | Custom API |
|--------|--------------|------------|
| New assignment group | Redeploy agent with updated prompts | Add to knowledge base |
| New Slack channel mapping | Reconfigure agent tools | Update API config |
| New priority rules | Rewrite agent instructions | Update API logic |

### 7. **Reduced Agent Complexity**

The agent's job is simplified to:
1. Collect information from the user
2. Call **one** API endpoint

All orchestration complexity is handled server-side, making the agent easier to maintain and less prone to hallucination-induced errors.

## Team Rag Tag

\- Graba Tasneem (Architect)

\- Adithi M D & Vanshika Immadi(QA Testers)

\- Shaina Munoz (Dev Lead)

\-Vanshika Immadi



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
| `API_KEY` | Secret key for authenticating API requests (see [API Key Authentication](#api-key-authentication)) |

---

## API Key Authentication

The TechNova Support API requires an API key for all endpoints (except `/health`). This adds an extra layer of security, ensuring only authorized clients (like your watsonx Orchestrate agent) can access the API.

### How It Works

1. **Header-based authentication** – Clients must include the `X-API-Key` header in every request
2. **Server-side validation** – The API validates the key against the `API_KEY` environment variable
3. **Development mode** – If `API_KEY` is not set, the API runs in "open mode" (useful for local testing)

### Generating an API Key

Generate a secure random API key:

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }) -as [byte[]])

# OpenSSL
openssl rand -base64 32
```

Example output: `dGVjaG5vdmEtc3VwcG9ydC1hcGkta2V5LTIwMjY=`

### Configuring the API Key

#### 1. Add to your `.env` file

```bash
API_KEY=your-generated-api-key-here
```

#### 2. Add to IBM Code Engine (for deployed API)

```bash
# Update the secret with the new API_KEY
ibmcloud ce secret update --name technova-api-secrets --from-literal API_KEY=your-generated-api-key-here

# Or recreate from .env file
ibmcloud ce secret update --name technova-api-secrets --from-env-file .env

# Restart the app to pick up changes
ibmcloud ce app update --name technova-api --env-from-secret technova-api-secrets
```

#### 3. Add to GitHub Actions (for CI/CD)

Go to your repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret Name | Value |
|-------------|-------|
| `API_KEY` | Your generated API key |

Then update `.github/workflows/build.yml` to pass the secret to Code Engine.

### Configuring watsonx Orchestrate Toolset with API Key

When you upload the `openapi.json` to watsonx Orchestrate, you need to configure the API key authentication. However, there's an important caveat for **first-time setup**.

#### ⚠️ Important: First-Time Deployment Sequence

watsonx Orchestrate validates your OpenAPI spec by calling your server URL during upload. If your API requires authentication, the validation will fail with a **401 error** before you can configure the API key.

**Solution:** Deploy your API with authentication **disabled** first, then enable it after configuring watsonx Orchestrate.

##### First-Time Setup Sequence

| Step | Action | API_KEY Status |
|------|--------|----------------|
| 1 | Deploy API to Code Engine | `API_KEY=""` (empty/disabled) |
| 2 | Upload `openapi.json` to watsonx Orchestrate | — |
| 3 | Configure API key in watsonx Orchestrate toolset | — |
| 4 | Re-deploy API with authentication enabled | `API_KEY="your-secret-key"` |

##### How to Disable API Key for Initial Deployment

**Option A: Via GitHub Actions (`.github/workflows/build.yml`)**

Temporarily change the API_KEY environment variable to empty:

```yaml
# Before (authentication enabled):
--env "API_KEY=${{ secrets.API_KEY }}"

# After (authentication disabled for initial upload):
--env "API_KEY="
```

**Option B: Via IBM Cloud CLI**

```bash
# Disable authentication temporarily
ibmcloud ce app update --name technova-api --env "API_KEY="

# After configuring watsonx, re-enable authentication
ibmcloud ce app update --name technova-api --env "API_KEY=your-secret-key"
```

##### After watsonx Orchestrate is Configured

Once you've uploaded the OpenAPI spec and configured the API key in watsonx Orchestrate:

1. **Re-enable authentication** by setting `API_KEY` to your actual secret
2. **Use the same key** in both places (Code Engine and watsonx Orchestrate)
3. **Test the agent** to verify authentication works end-to-end

> **Note:** For subsequent deployments (updates), you can keep `API_KEY` enabled since the toolset is already configured in watsonx Orchestrate.

---

### Adding the TechNova API Toolset to watsonx Orchestrate

This section walks you through uploading the `openapi.json` file to watsonx Orchestrate and configuring the API key authentication.

#### Step 1: Navigate to Your Agent's Toolset

1. Go to [watsonx Orchestrate](https://dl.watson-orchestrate.ibm.com/home)
2. Click **AI assistant builder** in the left sidebar
3. Open your **TechNova Solutions** agent (or create a new one)
4. Click **Toolset** in the left sidebar

#### Step 2: Import the OpenAPI Specification

1. Click **Add tool** (or the **+** button)
2. Select **From an OpenAPI specification file** under "Custom-built tool"
3. Click **Browse** and select your `openapi.json` file from this repository
4. Click **Next** to continue

#### Step 3: Select Tools to Import

After the file is parsed, you'll see a list of available endpoints:

| Name | Method | Description | Auth Type |
|------|--------|-------------|-----------|
| Health Check | GET | Health check endpoint | No Auth |
| Get Support | POST | Creates incident & sends Slack notification | Api Key |
| List Assignment Groups | GET | Get available assignment groups | Api Key |
| List Categories | GET | Get available incident categories | Api Key |
| List Impacts | GET | Get available impact values | Api Key |
| List Urgencies | GET | Get available urgency values | Api Key |

**Select all the "Api Key" endpoints** (uncheck Health Check as it's optional):
- ✅ Get Support
- ✅ List Assignment Groups
- ✅ List Categories
- ✅ List Impacts
- ✅ List Urgencies

Click **Next** to continue.

#### Step 4: Add New Connection

1. Click **Add new connection**
2. On the "Define connection details" screen:
   - **Connection ID**: Auto-generated (e.g., `technova_support_api_20260201193133150`)
   - **Display name**: `TechNova Support API`
3. Click **Save and continue**

#### Step 5: Configure Draft Connection

This configures the connection for testing/draft environment:

1. **Single sign-on (SSO)**: Leave **Off**
2. **Authentication type**: Select **Api Key** from the dropdown
3. **Server URL**: Should be auto-filled from the OpenAPI spec
   - Example: `https://technova-api.25rfx7vtssv6.eu-gb.codeengine.appdomain.cloud`
4. **API Key Location**: Select **header**
5. **Credential type**: Select **Team credentials** (recommended for shared API key)
6. Click **Next**

#### Step 6: Configure Live Connection

This configures the connection for the production/live environment:

1. Click **Paste draft configuration** to copy settings from the draft connection
2. **Credential type**: Select **Team credentials**
3. Click **Finish**

#### Step 7: Enter the API Key

After finishing the connection wizard, you'll be prompted to enter your credentials:

1. A dialog will appear asking for the API key
2. **API Key**: Enter `mykey` (or your actual API key configured in Code Engine)
3. Click **Connect** or **Save**

> **Important:** Use the same API key value that's configured in your deployed API's environment variables (`API_KEY` secret in Code Engine or GitHub Actions).

#### Step 8: Verify the Tools are Ready

1. Return to the **Toolset** view
2. You should see all imported tools listed with a green status indicator
3. Test a tool by clicking the **⋮** menu → **Test**
4. Example test for "List Urgencies":
   - No input parameters required
   - Click **Run**
   - Expected response: List of urgency values (1-Critical, 2-High, 3-Medium, 4-Low)

#### Troubleshooting Import Issues

| Issue | Solution |
|-------|----------|
| 401 error during import | Ensure your API is deployed with `API_KEY` set (not empty) |
| "Invalid OpenAPI spec" error | Check that `openapi.json` uses version 3.0.3 (not 3.1.0) |
| Tools not appearing | Refresh the page and check the toolset again |
| "Connection failed" error | Verify the Server URL is correct and API is running |
| Can't configure authentication | Make sure the OpenAPI spec has `securitySchemes` defined |

#### Updating the API Key

If you need to rotate or change the API key:

1. Go to **Toolset** in your agent
2. Click the connection name (e.g., "TechNova Support API")
3. Click **Edit connection**
4. Update the **API Key** value
5. Click **Save**

> **Note:** After updating the API key in watsonx Orchestrate, make sure the same key is configured in your deployed API's environment variables (Code Engine secrets or GitHub Actions secrets).

### Testing API Key Authentication

```bash
# Without API key (should return 401)
curl -X GET "http://localhost:8000/assignment_groups"
# Response: {"detail":"Missing API Key. Include 'X-API-Key' header in your request."}

# With invalid API key (should return 403)
curl -X GET "http://localhost:8000/assignment_groups" -H "X-API-Key: wrong-key"
# Response: {"detail":"Invalid API Key"}

# With valid API key (should return data)
curl -X GET "http://localhost:8000/assignment_groups" -H "X-API-Key: your-api-key"
# Response: {"assignment_groups": [...]}

# Health endpoint (no API key required)
curl -X GET "http://localhost:8000/health"
# Response: {"status":"healthy","version":"1.0.0"}
```

### Security Best Practices

1. **Never commit API keys** – Always use environment variables or secrets management
2. **Rotate keys regularly** – Generate new keys periodically and update all clients
3. **Use different keys per environment** – Dev, staging, and production should have separate keys
4. **Monitor usage** – Check API logs for unauthorized access attempts

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

##### Option 1: Using Secrets (Recommended - Handles Special Characters)

**This is the recommended approach** because it avoids shell escaping issues with special characters like `$`, `@`, `!`, etc.

**Using the deployment script:**
```powershell
# PowerShell (Windows)
cd scripts
.\deploy-code-engine.ps1 -EnvFile ..\.env

# Bash (Mac/Linux)
cd scripts
chmod +x deploy-code-engine.sh
./deploy-code-engine.sh --env-file ../.env
```

**Manual secret creation:**
```bash
# Create a secret from your .env file (special chars are preserved!)
ibmcloud ce secret create --name technova-api-secrets --from-env-file .env

# Bind the secret to your application
ibmcloud ce app update --name technova-api --env-from-secret technova-api-secrets

# Verify the secret was created correctly
ibmcloud ce secret get --name technova-api-secrets --decode
```

##### Option 2: Inline Environment Variables (Simple Values Only)

> ⚠️ **Warning:** This method can truncate values containing special characters like `$`. 
> For example, `jh@Uq6G$LoD8` becomes `jh@Uq6G` because `$LoD8` is interpreted as a shell variable.

Only use this for simple values without special characters:

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

This section provides detailed instructions for creating the **TechNova Solutions** agent in IBM watsonx Orchestrate - a multi-tool enterprise workflow choreographer that dynamically coordinates workflows across siloed enterprise tools (ServiceNow, GitHub, Slack) without human orchestration.

#### What This Agent Does

When a customer reports a problem with a product, the agent:
1. **Gathers information** - Collects customer details, product name, and problem description
2. **Identifies the team** - Uses the knowledge base to find the corresponding support team
3. **Creates a ServiceNow incident** - Logs the issue with proper priority and assignment
4. **Creates a GitHub issue** - If the report contains a stack trace or error code
5. **Alerts developers in Slack** - Sends notification to the appropriate channel

This compresses operational response time and eliminates manual tool switching.

---

#### Step 1: Access watsonx Orchestrate

1. Go to [dl.watson-orchestrate.ibm.com/build](https://dl.watson-orchestrate.ibm.com/build)
2. Sign in with your IBM Cloud account (or IBMid)
3. If prompted, accept the terms of service

---

#### Step 2: Create a New Agent

1. From the watsonx Orchestrate home page, click **Manage agents** → **Create Agent**
2. Give your agent a name: `TechNova Solutions`
3. Select a model (e.g., `GPT-OSS 120B` or your preferred LLM)

---

#### Step 3: Configure Agent Profile

In the **Profile** section, configure the following:

##### Description

```
Multi-tool enterprise workflow choreographer, in IBM watsonx orchestrator an agentic AI that could dynamically coordinate workflows across siloed enterprise tools such as ServiceNow, GitHub, Slack, or Confluence, without human orchestration to compress operational response time or eliminate manual tool switching.

For example, when a customer reports a problem with a product, the solution guides the customer to find the corresponding team based on instructions on a pre-defined Confluence page that maps a team to that product and call a custom API with the gathered information. The backend API is responsible for creating a service now incident, creating a github issue and alerting developers in slack.

1. Define the workflow:
   - Start: A customer reports a problem with a product.
   - Step 1: Gather customer information and product details.
   - Step 2: Identify the corresponding team for the product.
   - Step 3: Call a custom API with the gathered information.
   - Step 4: Create a ServiceNow incident.
   - Step 5: Create a GitHub issue.
   - Step 6: Alert developers in Slack.

For the Service Now Incident: short-description, description, caller-id and priority. The description should contain customer email and product name.
```

##### Welcome Message

```
Hello, welcome to TechNova Solutions Support
```

##### Quick Start Prompts

Add the following pre-set prompt:
- `Report an incident`

##### Agent Style

Select **Default** (Recommended) - Relies on the model's intrinsic ability to understand, plan, and call tools and knowledge.

---

#### Step 4: Add Knowledge Base

The agent needs knowledge about your company, products, and support processes.

1. Click **Knowledge** in the left sidebar
2. Click **Replace source** or **Add source**
3. Create a new knowledge source called `Company Directory`
4. Add description: `Company details, with products mappings, related to corresponding departments, contains customer instructions on how to find product id, incident creation instructions and service now assignment groups.`
5. Upload the following documents from the `knowledge-base/` folder:

| File | Purpose |
|------|---------|
| `agent_instructions.txt` | Instructions for how the agent should behave |
| `company-overview.txt` | Company background and department information |
| `how-to-find-product-id.txt` | Guide for identifying product IDs |
| `incident-creation-guide.txt` | How to create proper incidents |
| `product-catalog.txt` | List of products and their categories |
| `servicenow-assignment-groups.txt` | Mapping of products to support teams |
| `guidelines/product-to-assignment-group-mapping.txt` | **Critical:** Maps products to ServiceNow assignment groups |
| `guidelines/incident-creation-workflow.txt` | Step-by-step workflow for creating incidents |

##### Key Guidelines for Product-to-Assignment Group Mapping

The `guidelines/product-to-assignment-group-mapping.txt` file is essential for the agent to correctly route incidents. It contains:

**Quick Mapping by Product ID Prefix:**
| Product ID Prefix | Assignment Group |
|-------------------|------------------|
| CLOUD-* | CLOUD-L1-Support |
| DATA-* | DATA-L1-Support |
| SEC-* | SEC-L1-Support |
| COLLAB-* | COLLAB-L1-Support |
| FIN-* | FIN-L1-Support |
| DEV-* | DEVTOOLS-L1-Support |
| IOT-* | IOT-L1-Support |

**Priority to Urgency/Impact Mapping:**
| Priority | urgency_value | impact_value |
|----------|---------------|--------------|
| Critical | 1 | 1 |
| High | 2 | 2 |
| Medium | 3 | 3 |
| Low | 4 | 4 |

**Incident Category by Product:**
| Product Prefix | incident_category |
|----------------|-------------------|
| CLOUD-* | Infrastructure |
| DATA-* | Data Services |
| SEC-* | Security |
| COLLAB-* | Collaboration |
| FIN-* | Financial Systems |
| DEV-* | Developer Tools |
| IOT-* | IoT/Industrial |

---

#### Step 5: Add Toolset (API Integration)

##### Step 5a: Create the OpenAPI JSON File

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

##### Step 5b: Upload the OpenAPI JSON as a Tool

1. Click **Toolset** in the left sidebar
2. Click **Add tool**
3. Select **Import from OpenAPI** or **Custom API**
4. Click **Upload file** and select your `openapi.json` file
5. Wait for the file to be parsed and validated

##### Step 5c: Select Endpoints for Your Agent

After uploading, you'll see a list of all available endpoints. Enable these tools:

| Tool Name | Endpoint | Description |
|-----------|----------|-------------|
| **Get Support** | `POST /get_support` | Create a support incident in ServiceNow and send a Slack notification |
| **List Assignment Groups** | `GET /assignment_groups` | Get available ServiceNow assignment groups |
| **List Categories** | `GET /categories` | Get available incident categories |
| **List Impacts** | `GET /impacts` | Get available impact values |
| **List Urgencies** | `GET /urgencies` | Get available urgency values |

##### Step 5d: Test the Connection

1. Click the **⋮** menu on each tool
2. Select **Test**
3. Provide sample input values
4. Verify the response is correct

---

#### Step 6: Configure Agent Behavior

In the **Behavior** section, add detailed instructions for how the agent should operate:

##### Instructions

```
**Role**  
You are a Multi‑tool Enterprise Workflow Choreographer in IBM watsonx Orchestrator. Your job is to interact with the user, gather all required details, determine the appropriate team from the knowledge base mapping, and then automatically trigger the downstream actions (ServiceNow incident, GitHub issue, Slack alert) without any human hand‑off.

**Tool Usage Guidelines**  
1. Never call a tool until you have collected **all** required parameters from the user; do not guess or assume missing values.  
2. Call each tool **once** per unique set of parameters.  
3. If a tool fails or returns an error, report the error to the user and offer to retry.  

**How To Use Tools**  

- **Gather required information**  
  1. Prompt the user for:  
     - Customer email  
     - Customer name (optional)  
     - Product name or Product ID 
     - Brief problem description (to be used as the incident short‑description)  
     - Desired priority (e.g., Low/Medium/High)  
  2. Validate that each answer is present; if any piece is missing, ask the user again before proceeding.

- **Identify the owning team**  
  Use the knowledge base to parse the product name/ID and look up the team in the pre‑defined mapping. The result should be the **assignment_group** name to be passed to ServiceNow.

- **Map priority to ServiceNow impact/urgency**  
  - High → impact = "1", urgency = "1"  
  - Medium → impact = "2", urgency = "2"  
  - Low → impact = "3", urgency = "3"

- **Create the support incident**  
  Call **Get Support** with:  
  - `short_description` = user‑provided brief problem description  
  - `description` = "Customer [email] reported an issue with **[product]**. Details: [problem description]" (must include email and product)  
  - `caller_username` = the customer email (or the ServiceNow user ID if known)  
  - `impact_value` = value derived from priority  
  - `urgency_value` = value derived from priority  
  - `assignment_group` = team name obtained from the knowledge base lookup  
  - `incident_category` = product category (if available; otherwise set to "General")  

- **Return confirmation to the user**  
  Summarize the actions performed, including the ServiceNow incident number, GitHub issue URL (if created), and Slack notification status.

**How To Route To Other Agents**  
- **servicenow_case_management_agent_80b2b988** – can handle any advanced ServiceNow case management tasks, such as updating incident fields, adding work notes, or linking incidents to change requests. Delegate to this agent whenever the workflow requires ServiceNow functionality not covered by the Get Support tool.
```

---

#### Step 7: Configure Channels (Optional)

In the **Channels** section, you can enable various communication channels:

| Channel | Description |
|---------|-------------|
| **Home page** | Show the agent on the Orchestrate Chat home page ✅ |
| **Embedded agent** | Customize chat UI for embedding in your website |
| **Teams** | Enable communication via Microsoft Teams |
| **Slack** | Configure Slack to connect with the agent |
| **WhatsApp with Twilio** | Enable WhatsApp communication |
| **Facebook Messenger** | Enable Facebook Messenger |

---

#### Step 8: Deploy the Agent

1. Click the **Deploy** button in the top right corner
2. Review the deployment settings
3. Confirm deployment
4. Your agent is now live and accessible!

---

### Uploading Test Cases for Agent Evaluation

watsonx Orchestrate allows you to upload test cases in CSV format to evaluate your agent's performance systematically. This is useful for:
- Validating agent behavior across different scenarios
- Regression testing after agent updates
- Demonstrating agent capabilities

#### CSV Format Requirements

The CSV file **must** have two columns with these exact headers:

| Column | Required | Description |
|--------|----------|-------------|
| `Prompt` | ✅ Yes | The user input/question to test |
| `answer` | ✅ Yes | The expected behavior or response |

**Example CSV structure:**
```csv
Prompt,answer
"Help! My VM is not starting. Product ID: CLOUD-001, Username: admin","Create ServiceNow incident assigned to CLOUD-L1-Support, send Slack notification to #cloud-support"
"Password reset needed. Product ID: SEC-003, Username: user1","Create ServiceNow incident assigned to SEC-L1-Support, send Slack notification to #security-incidents"
```

#### Important CSV Formatting Rules

1. **Headers are case-sensitive** - Use `Prompt` (capital P) and `answer` (lowercase a)
2. **Wrap prompts in double quotes** - Especially if they contain commas, line breaks, or special characters
3. **Escape internal quotes** - Use `""` for quotes within quoted strings
4. **No trailing commas** - Each line should have exactly one comma separating the two columns
5. **UTF-8 encoding** - Save the file with UTF-8 encoding

#### How to Upload Test Cases

1. **Navigate to Test Page**
   - Go to your agent in watsonx Orchestrate
   - Click the **Deploy** dropdown (⋮ menu) in the top right
   - Select **Test**

2. **Upload CSV File**
   - Click **Upload tests** button
   - Click **Browse** or drag and drop your CSV file
   - The file must be under 5 MB

3. **Review Imported Tests**
   - After upload, you'll see all prompts listed in the Test cases table
   - Each row shows the Prompt, Date created, and Last run status

4. **Run Tests**
   - Click **Run all** to execute all test cases
   - Or select individual tests and run them one at a time
   - Results will show in the **Evaluations** section below

#### Pre-built Test Cases

This repository includes comprehensive test cases covering all products and departments:

| File | Location | Test Cases | Description |
|------|----------|------------|-------------|
| `agent_test_cases_comprehensive.csv` | `tests/test prompts/` | 88 | All products, all departments, various scenarios |

**Coverage includes:**
- ✅ All 80 products across 8 departments (CLOUD, DATA, SEC, COLLAB, FIN, DEV, ITSM, ERP)
- ✅ Critical incidents with stack traces (triggers GitHub issue creation)
- ✅ Standard support requests (ServiceNow + Slack only)
- ✅ Access requests, license requests, feature requests, training questions

#### Troubleshooting Test Upload Issues

| Error | Cause | Solution |
|-------|-------|----------|
| "Missing required headers: answer" | CSV missing the `answer` column | Ensure CSV has both `Prompt` and `answer` headers |
| "Missing required headers: Prompt" | CSV missing the `Prompt` column or wrong case | Use capital P: `Prompt` not `prompt` |
| "Invalid CSV format" | Malformed CSV structure | Check for unescaped quotes or extra commas |
| "File too large" | CSV exceeds 5 MB limit | Split into smaller files or reduce test cases |
| Empty test cases shown | Encoding issue | Save file as UTF-8 without BOM |

---

#### Testing Your Agent

Use the **Talk to agent** panel on the right side to test. Try these example prompts:

**Example 1: Bug Report with Stack Trace**
```
Help! SecureAccess Gateway is failing authentication for all users since this morning.

Error: AUTHENTICATION_FAILED - Invalid token signature
    at TokenValidator.verify (/opt/secureaccess/lib/auth/validator.js:78:15)
    at AuthMiddleware.authenticate (/opt/secureaccess/lib/middleware/auth.js:34:22)

Product ID: SA-2024
Username: admin.user
This is impacting all 500 users in our organization!
```

**Example 2: General Support Request**
```
I need help resetting my password for CloudMatrix Pro. My username is jane.smith and I've been locked out after too many failed attempts. Product ID: CM-2024
```

The agent will:
1. Identify the product from the Product ID
2. Look up the assignment group in the knowledge base
3. Create a ServiceNow incident with appropriate priority
4. Send a Slack notification to the support channel
5. Create a GitHub issue (if the report contains a stack trace)

> **Tip:** Access your API's interactive documentation at `https://your-api-url/docs` to see all available endpoints and test them manually.

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

# Create test Service Now Assignment Groups

```bash

# Preview what would be created (no changes made)
python -m tests.create_ag_groups --dry-run

# Create all assignment groups
python -m tests.create_ag_groups

# List existing groups
python -m tests.create_ag_groups --list

# Delete all groups (dangerous!)
python -m tests.create_ag_groups --delete --confirm
```

# See Live Preview

Replace `your-api-url` and `your-frontend-url` with your actual Code Engine deployment URLs.

| Service	| URL|
|------------|----|
| API	| https://your-api-url.codeengine.appdomain.cloud |
| Frontend	| https://your-frontend-url.codeengine.appdomain.cloud |


# Project/Repository Enhancements
- protect repo branches
- automated testing
- code quality scans
- copilot instructions for code generatation
- prod and nonprod environment handling 
- hardware and sofware integration for error handling
- fix react chatbox connection to orchestrate agent


## Example Agent Prompt

Once your API is deployed and connected to watsonx Orchestrate, you can test the agent with prompts like this:

### Example 1: Bug Report with Stack Trace (Creates GitHub Issue + ServiceNow Ticket)

```
Help! SecureAccess Gateway is failing authentication for all users since this morning.

Error: AUTHENTICATION_FAILED - Invalid token signature
    at TokenValidator.verify (/opt/secureaccess/lib/auth/validator.js:78:15)
    at AuthMiddleware.authenticate (/opt/secureaccess/lib/middleware/auth.js:34:22)
    at Layer.handle [as handle_request] (/opt/secureaccess/node_modules/express/lib/router/layer.js:95:5)
    at next (/opt/secureaccess/node_modules/express/lib/router/route.js:144:13)
    at Route.dispatch (/opt/secureaccess/node_modules/express/lib/router/route.js:114:3)
    at process._tickCallback (internal/process/next_tick.js:68:7)

Product ID: SA-2024
Username: admin.user
This is impacting all 500 users in our organization!
```

### Example 2: General Support Request (Creates ServiceNow Ticket Only)

```
I need help resetting my password for CloudMatrix Pro. My username is jane.smith and I've been locked out after too many failed attempts. Product ID: CM-2024
```

### Example 3: Performance Issue

```
DataFlow Analytics is running extremely slow today. Reports that used to take 5 seconds are now taking over 2 minutes. Product ID: DF-2024, Username: data.analyst
```

### What the Agent Does

Based on the prompt content, the agent will:
1. **Identify the product** from the Product ID or description
2. **Determine the assignment group** based on the product category
3. **Create a ServiceNow incident** with appropriate urgency/impact
4. **Send a Slack notification** to the support channel
5. **Create a GitHub issue** (only if the prompt contains a stack trace or error code)