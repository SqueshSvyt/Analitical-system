# Deployment Guide

## Table of Contents

1. [Development Deployment](#development-deployment)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Security](#security)
6. [Monitoring](#monitoring)
7. [Backup & Recovery](#backup--recovery)

---

## Development Deployment

### Local Development Setup

1. **Start Neo4j:**
```bash
docker-compose up -d neo4j
```

2. **Start Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

3. **Start Frontend:**
```bash
cd frontend
npm run dev
```

4. **Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

---

## Production Deployment

### Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Docker & Docker Compose
- Domain name (optional)
- SSL certificate (Let's Encrypt recommended)

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone <your-repo-url>
cd Analitical_system
```

### Step 2: Configure Environment

```bash
# Backend configuration
cp backend/.env.example backend/.env
nano backend/.env
```

Update with production values:
```env
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<strong-password>
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 3: Configure Docker Compose

Edit `docker-compose.yml`:

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.16.0
    restart: always
    environment:
      - NEO4J_AUTH=neo4j/<strong-password>
      - NEO4J_dbms_memory_heap_max__size=4G
      - NEO4J_dbms_memory_pagecache_size=2G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    networks:
      - analytical-network

  backend:
    build: ./backend
    restart: always
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=<strong-password>
    depends_on:
      - neo4j
    networks:
      - analytical-network

  frontend:
    build: ./frontend
    restart: always
    environment:
      - VITE_API_URL=https://your-domain.com/api
    networks:
      - analytical-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - analytical-network

volumes:
  neo4j_data:
  neo4j_logs:

networks:
  analytical-network:
```

### Step 4: Setup Nginx

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location /api/ {
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location / {
            proxy_pass http://frontend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### Step 5: SSL Certificate

Using Let's Encrypt:

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
```

### Step 6: Start Services

```bash
docker-compose up -d
```

### Step 7: Verify Deployment

```bash
# Check containers
docker-compose ps

# Check logs
docker-compose logs -f

# Test health
curl https://your-domain.com/health
```

---

## Docker Deployment

### Single-Server Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Scaling Services

```bash
# Scale backend
docker-compose up -d --scale backend=3

# Scale with load balancer
# Update nginx.conf with multiple backend servers
```

---

## Cloud Deployment

### AWS Deployment

#### Using EC2

1. **Launch EC2 Instance:**
   - Ubuntu 20.04 LTS
   - t3.large or larger
   - 50GB+ storage
   - Security groups: 22, 80, 443

2. **Setup:**
```bash
ssh ubuntu@<ec2-ip>
# Follow production deployment steps
```

#### Using ECS (Fargate)

1. Create ECR repositories
2. Push Docker images
3. Create ECS cluster
4. Define task definitions
5. Create services
6. Configure ALB

### Google Cloud Platform

#### Using Compute Engine

Similar to AWS EC2 deployment.

#### Using Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/analytical-backend backend/
gcloud builds submit --tag gcr.io/PROJECT-ID/analytical-frontend frontend/

# Deploy
gcloud run deploy analytical-backend --image gcr.io/PROJECT-ID/analytical-backend
gcloud run deploy analytical-frontend --image gcr.io/PROJECT-ID/analytical-frontend
```

### Azure

#### Using Azure Container Instances

```bash
az container create --resource-group myResourceGroup \
  --name analytical-system \
  --image myregistry.azurecr.io/analytical:latest
```

---

## Security

### Security Checklist

- [ ] Change default Neo4j password
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Implement rate limiting
- [ ] Setup firewall rules
- [ ] Regular security updates
- [ ] Enable authentication/authorization
- [ ] Use secure session management
- [ ] Implement input validation
- [ ] Setup logging and monitoring

### Environment Security

```bash
# Secure .env files
chmod 600 backend/.env

# Use secrets management
# AWS Secrets Manager
# Azure Key Vault
# Google Secret Manager
```

### Network Security

```bash
# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Restrict Neo4j access
# Only allow internal network
```

---

## Monitoring

### Application Monitoring

1. **Health Checks:**
```bash
# Backend health
curl http://localhost:8000/health

# Neo4j health
curl http://localhost:7474
```

2. **Logging:**
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
```

3. **Metrics:**
- Setup Prometheus + Grafana
- Monitor API response times
- Track database queries
- Monitor system resources

### Database Monitoring

```cypher
// Neo4j monitoring queries
CALL dbms.queryJmx('org.neo4j:*')
YIELD name, attributes RETURN *;

// Check database size
CALL apoc.meta.stats();
```

---

## Backup & Recovery

### Neo4j Backup

```bash
# Backup Neo4j data
docker exec analytical-neo4j neo4j-admin database backup neo4j \
  --to-path=/backups

# Copy backup
docker cp analytical-neo4j:/backups ./backups

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
docker exec analytical-neo4j neo4j-admin database backup neo4j \
  --to-path=/backups/backup-$DATE
```

### Restore Neo4j

```bash
# Stop Neo4j
docker-compose stop neo4j

# Restore
docker run --rm -v neo4j_data:/data -v ./backups:/backups \
  neo4j:5.16.0 neo4j-admin database restore neo4j \
  --from-path=/backups/backup-20241220

# Start Neo4j
docker-compose start neo4j
```

### Application Backup

```bash
# Backup configuration
tar -czf config-backup.tar.gz backend/.env docker-compose.yml

# Backup code
git push origin main
```

---

## Maintenance

### Updates

```bash
# Update Docker images
docker-compose pull

# Rebuild with new code
docker-compose build --no-cache

# Rolling update
docker-compose up -d --no-deps --build backend
```

### Database Maintenance

```cypher
// Neo4j maintenance
CALL db.checkpoint();
CALL apoc.trigger.list();
```

---

## Troubleshooting

### Common Issues

1. **Container won't start:**
```bash
docker-compose logs <service-name>
docker-compose down -v
docker-compose up -d
```

2. **Database connection failed:**
```bash
docker-compose restart neo4j
docker exec -it analytical-neo4j cypher-shell -u neo4j -p <password>
```

3. **Out of memory:**
```yaml
# Increase Neo4j memory in docker-compose.yml
NEO4J_dbms_memory_heap_max__size=8G
```

### Performance Tuning

1. **Neo4j Configuration:**
```properties
dbms.memory.heap.initial_size=2G
dbms.memory.heap.max_size=4G
dbms.memory.pagecache.size=2G
```

2. **Backend Optimization:**
- Increase uvicorn workers
- Enable caching
- Optimize database queries

3. **Frontend Optimization:**
- Build production bundle
- Enable compression
- Use CDN for static assets

