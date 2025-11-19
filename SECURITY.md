# Security Policy

TwinSecure is a proprietary cybersecurity platform. We take security seriously and welcome responsible disclosure of security vulnerabilities.

## Reporting Security Vulnerabilities

**Please do not open public issues for security vulnerabilities.**

Instead, please report security issues by email to:

```
kunalsingh2514@gmail.com
```

Include the following information:

- A description of the vulnerability and its impact
- Steps to reproduce the issue
- Affected versions (if applicable)
- Suggested remediation (if available)

We will acknowledge your report within 24 hours and provide a timeline for a fix.

## Security Best Practices

### Development

- Never commit secrets, API keys, or passwords to the repository
- Use environment variables for all sensitive configuration
- Review the `.env.example` file for required and optional settings
- Run security tests before committing code

### Deployment

- Change default admin credentials immediately after installation
- Use strong, randomly generated secrets (minimum 32 characters for API keys)
- Enable HTTPS/TLS in production
- Keep all dependencies updated
- Use environment-specific configuration files
- Enable rate limiting and CORS properly
- Monitor logs and alerts for suspicious activity

### API Security

- All management endpoints require authentication (JWT tokens)
- Use the Authorization header: `Authorization: Bearer <token>`
- Tokens expire after 30 minutes (configurable)
- Refresh tokens are rotated on use
- Rate limiting is enabled by default (100 requests/minute)

### Database

- Use strong passwords for all database users
- Enable encryption at rest for sensitive data
- Use table partitioning for large alert/engagement tables
- Regular backups are essential
- Restrict database access to application servers only

### Honeypot Security

- Honeypot endpoints can be protected with a secret header
- Configure `HONEYPOT_SECRET_HEADER` environment variable
- Include header `X-TwinSecure-Honeypot-Secret` in requests
- Rotate the honeypot secret regularly

## Dependencies

TwinSecure depends on many open-source libraries. We monitor and update dependencies regularly:

```bash
# Check for vulnerable dependencies
pip audit          # Python
npm audit          # Node.js
```

## License

TwinSecure is proprietary software. Unauthorized copying, distribution, or modification is strictly prohibited.

For licensing inquiries: kunalsingh2514@gmail.com

## Acknowledgments

We appreciate the security research community and responsible disclosure practices.
