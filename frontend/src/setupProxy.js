/**
 * Proxy configuration for React development server.
 * Proxies IBM API requests to avoid CORS issues.
 */
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy IBM IAM token endpoint
  app.use(
    '/api/ibm-iam',
    createProxyMiddleware({
      target: 'https://iam.cloud.ibm.com',
      changeOrigin: true,
      pathRewrite: {
        '^/api/ibm-iam': '/identity/token',
      },
      onProxyRes: function(proxyRes, req, res) {
        // Add CORS headers
        proxyRes.headers['Access-Control-Allow-Origin'] = '*';
      },
    })
  );

  // Proxy IBM watsonx Orchestrate endpoint
  app.use(
    '/api/wxo',
    createProxyMiddleware({
      target: 'https://dl.watson-orchestrate.ibm.com',
      changeOrigin: true,
      pathRewrite: {
        '^/api/wxo': '',
      },
      onProxyRes: function(proxyRes, req, res) {
        proxyRes.headers['Access-Control-Allow-Origin'] = '*';
      },
    })
  );
};
