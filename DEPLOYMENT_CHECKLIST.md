# ScholarGrid Backend API — Production Deployment Checklist

Use this checklist to ensure a smooth and secure production deployment.

## Pre-Deployment

### Environment Configuration

- [ ] Copy `.env.production.template` to `.env`
- [ ] Set `ENVIRONMENT=production`
- [ ] Generate secure `SECRET_KEY` (min 32 chars)
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Configure production `DATABASE_URL` (not localhost)
- [ ] Configure production `REDIS_URL` (not localhost)
- [ ] Set `CORS_ORIGINS` to HTTPS frontend URLs only
- [ ] Configure `FIREBASE_CREDENTIALS_PATH`
- [ ] Set `GEMINI_API_KEY`
- [ ] Set `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
- [ ] (Optional) Set `SENTRY_DSN` for error tracking
- [ ] Verify all environment variables with:
  ```bash
  python scripts/verify_env.py
  ```

### Database Setup

- [ ] Create production PostgreSQL database
- [ ] Configure database user with appropriate permissions
- [ ] Enable SSL/TLS for database connections
- [ ] Set up automated database backups
- [ ] Test database connectivity
- [ ] Run database migrations:
  ```bash
  alembic upgrade head
  ```
- [ ] Create initial admin user:
  ```bash
  ADMIN_FIREBASE_UID=xxx ADMIN_EMAIL=admin@example.com python scripts/seed_admin.py
  ```

### Redis Setup

- [ ] Deploy production Redis instance
- [ ] Configure Redis password authentication
- [ ] Set `maxmemory` policy to `allkeys-lru`
- [ ] Enable Redis persistence (AOF or RDB)
- [ ] Test Redis connectivity

### Firebase Setup

- [ ] Create Firebase project
- [ ] Enable Firebase Authentication
- [ ] Enable Firebase Storage
- [ ] Download service account JSON
- [ ] Securely store credentials file
- [ ] Configure Firebase Storage CORS rules
- [ ] Set up Firebase Storage security rules

### Cloudinary Setup

- [ ] Create Cloudinary account
- [ ] Get cloud name, API key, and API secret
- [ ] Configure upload presets (optional)
- [ ] Set up folder structure

### Security

- [ ] Review and update CORS origins
- [ ] Ensure all passwords are strong and unique
- [ ] Enable HTTPS/TLS for all connections
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Review security headers configuration
- [ ] Disable debug mode
- [ ] Remove development dependencies

## Deployment

### Docker Deployment

- [ ] Build Docker image:
  ```bash
  docker build -t scholargrid-api:latest .
  ```
- [ ] Test Docker image locally:
  ```bash
  docker run -p 8000:8000 --env-file .env scholargrid-api:latest
  ```
- [ ] Push image to container registry (Docker Hub, ECR, GCR)
- [ ] Deploy with docker-compose:
  ```bash
  docker compose up -d
  ```
- [ ] Verify all containers are running:
  ```bash
  docker compose ps
  ```

### Manual Deployment

- [ ] Install Python 3.12+
- [ ] Create virtual environment
- [ ] Install dependencies:
  ```bash
  pip install -e .
  ```
- [ ] Run migrations
- [ ] Start application with Uvicorn:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
  ```

### Kubernetes Deployment (Optional)

- [ ] Create Kubernetes manifests
- [ ] Configure ConfigMaps for environment variables
- [ ] Configure Secrets for sensitive data
- [ ] Set up persistent volumes for PostgreSQL
- [ ] Configure Ingress for HTTPS
- [ ] Deploy to cluster:
  ```bash
  kubectl apply -f k8s/
  ```

## Post-Deployment

### Verification

- [ ] Check health endpoint:
  ```bash
  python scripts/health_check.py --url https://api.example.com
  ```
- [ ] Verify API documentation:
  - [ ] https://api.example.com/docs
  - [ ] https://api.example.com/redoc
- [ ] Test authentication flow
- [ ] Test file upload/download
- [ ] Test real-time chat
- [ ] Test AI chatbot
- [ ] Verify database connectivity
- [ ] Verify Redis connectivity
- [ ] Check application logs

### Monitoring Setup

- [ ] Configure Sentry error tracking
- [ ] Set up log aggregation (ELK, Splunk, CloudWatch)
- [ ] Configure health check monitoring
- [ ] Set up uptime monitoring (Pingdom, UptimeRobot)
- [ ] Configure performance monitoring (Datadog, New Relic)
- [ ] Set up alerts for:
  - [ ] API downtime
  - [ ] Database connectivity issues
  - [ ] Redis connectivity issues
  - [ ] High error rates
  - [ ] Slow response times
  - [ ] Disk space warnings
  - [ ] Memory usage warnings

### Performance Optimization

- [ ] Verify database indexes are created
- [ ] Test cache hit rates
- [ ] Monitor response times
- [ ] Check connection pool settings
- [ ] Verify Uvicorn worker count
- [ ] Test under load (optional)

### Security Hardening

- [ ] Enable HTTPS enforcement
- [ ] Verify security headers
- [ ] Test rate limiting
- [ ] Review CORS configuration
- [ ] Audit access logs
- [ ] Set up intrusion detection (optional)

### Documentation

- [ ] Document deployment architecture
- [ ] Document environment variables
- [ ] Document backup procedures
- [ ] Document rollback procedures
- [ ] Document scaling procedures
- [ ] Create runbook for common issues

## Ongoing Maintenance

### Daily

- [ ] Monitor error rates in Sentry
- [ ] Check application logs for warnings
- [ ] Verify health check status

### Weekly

- [ ] Review performance metrics
- [ ] Check disk space usage
- [ ] Review security alerts
- [ ] Update dependencies (if needed)

### Monthly

- [ ] Review and rotate secrets
- [ ] Test backup restoration
- [ ] Review and update documentation
- [ ] Conduct security audit
- [ ] Review and optimize database queries

### Quarterly

- [ ] Update Python and dependencies
- [ ] Review and update security policies
- [ ] Conduct load testing
- [ ] Review and optimize infrastructure costs

## Rollback Procedure

If deployment fails or issues are discovered:

1. [ ] Stop the new deployment
2. [ ] Restore previous Docker image/code version
3. [ ] Rollback database migrations (if needed):
   ```bash
   alembic downgrade -1
   ```
4. [ ] Verify health checks pass
5. [ ] Investigate and fix issues
6. [ ] Re-deploy when ready

## Emergency Contacts

- **DevOps Lead**: [Name] - [Email] - [Phone]
- **Backend Lead**: [Name] - [Email] - [Phone]
- **Database Admin**: [Name] - [Email] - [Phone]
- **Security Team**: [Email]

## Support Resources

- **Documentation**: https://github.com/your-org/scholargrid-backend
- **Issue Tracker**: https://github.com/your-org/scholargrid-backend/issues
- **Sentry**: https://sentry.io/organizations/your-org/projects/scholargrid/
- **Monitoring Dashboard**: [URL]

---

**Last Updated**: [Date]
**Deployment Version**: [Version]
**Deployed By**: [Name]
