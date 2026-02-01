/**
 * @fileoverview Service for connecting to IBM watsonx Orchestrate Agent via API.
 * Direct API connection without using the IBM widget.
 * @author TechNova Solutions
 * @version 2.0.0
 */

// Agent Configuration from environment variables
const AGENT_CONFIG = {
  orchestrationID: process.env.REACT_APP_ORCHESTRATION_ID,
  hostURL: process.env.REACT_APP_IBM_HOST,
  agentId: process.env.REACT_APP_AGENT_ID,
  apiKey: process.env.REACT_APP_WXO_API_KEY || "",
};

/**
 * Watson Orchestrate Agent Service
 * Direct API connection to IBM watsonx Orchestrate agent
 */
class WatsonxAgentService {
  constructor() {
    this.accessToken = null;
    this.tokenExpiry = null;
    this.sessionId = null;
  }

  /**
   * Get the agent configuration
   * @returns {Object} Agent configuration object
   */
  getConfig() {
    return { ...AGENT_CONFIG };
  }

  /**
   * Get a bearer token from IBM IAM
   * @returns {Promise<string>} The access token
   */
  async getBearerToken() {
    // Return cached token if still valid (with 5 min buffer)
    if (this.accessToken && this.tokenExpiry && Date.now() < this.tokenExpiry - 300000) {
      return this.accessToken;
    }

    if (!AGENT_CONFIG.apiKey) {
      throw new Error("API key not configured. Set REACT_APP_WXO_API_KEY in .env file.");
    }

    console.log("[WatsonxAgent] Fetching bearer token...");
    
    // Use proxy to avoid CORS issues (proxied through /api/ibm-iam -> iam.cloud.ibm.com)
    const response = await fetch("/api/ibm-iam", {
      method: "POST",
      headers: { 
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
      },
      body: `grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=${AGENT_CONFIG.apiKey}`,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[WatsonxAgent] Token error:", errorText);
      throw new Error(`Failed to get bearer token: ${response.status}`);
    }

    const data = await response.json();
    this.accessToken = data.access_token;
    // Token typically expires in 1 hour (3600 seconds)
    this.tokenExpiry = Date.now() + (data.expires_in || 3600) * 1000;
    
    console.log("[WatsonxAgent] Bearer token obtained successfully");
    return this.accessToken;
  }

  /**
   * Send a message to the IBM watsonx Orchestrate agent
   * @param {string} message - The user message
   * @returns {Promise<string>} The agent response
   */
  async sendMessage(message) {
    try {
      const token = await this.getBearerToken();

      // Use proxy to avoid CORS issues (proxied through /api/wxo -> dl.watson-orchestrate.ibm.com)
      const response = await fetch("/api/wxo/v1/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
          "X-Agent-ID": AGENT_CONFIG.agentId,
          "X-Orchestration-ID": AGENT_CONFIG.orchestrationID,
        },
        body: JSON.stringify({
          messages: [{ role: "user", content: message }],
          stream: false,
          session_id: this.sessionId,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("[WatsonxAgent] Chat error:", errorText);
        throw new Error(`Chat API error: ${response.status}`);
      }

      const data = await response.json();
      console.log("[WatsonxAgent] Response:", data);

      // Store session ID for conversation continuity
      if (data.session_id) {
        this.sessionId = data.session_id;
      }

      // Extract the assistant's response
      return data.choices?.[0]?.message?.content || 
             data.response || 
             data.message || 
             data.output ||
             "I received your message but couldn't process a response.";
    } catch (error) {
      console.error("[WatsonxAgent] Error:", error);
      throw error;
    }
  }

  /**
   * Check if the service is configured
   * @returns {boolean}
   */
  isConfigured() {
    return !!(AGENT_CONFIG.apiKey && AGENT_CONFIG.agentId && AGENT_CONFIG.hostURL);
  }

  /**
   * Reset the session
   */
  resetSession() {
    this.sessionId = null;
    console.log("[WatsonxAgent] Session reset");
  }

  /**
   * Clear cached token (useful for logout or token refresh)
   */
  clearToken() {
    this.accessToken = null;
    this.tokenExpiry = null;
    console.log("[WatsonxAgent] Token cleared");
  }
}

// Export singleton instance
const watsonxAgent = new WatsonxAgentService();

export default watsonxAgent;
export { AGENT_CONFIG, WatsonxAgentService };
