# MyTeacher AI - AWS Deployment Architecture
## Cost-Optimized, High-Performance, Production-Ready

**Version:** 1.0
**Date:** December 9, 2025
**Target**: AWS Cloud (Multi-AZ, Auto-scaling)
**Estimated Monthly Cost**: $150-300 (low-medium traffic) | $500-800 (high traffic)

---

## 🏗️ Architecture Overview

### Design Principles
1. **Serverless-First**: Use managed services to minimize operational overhead
2. **Auto-Scaling**: Scale based on demand to control costs
3. **Global CDN**: CloudFront for fast content delivery worldwide
4. **High Availability**: Multi-AZ deployment for 99.99% uptime
5. **Security**: WAF, encryption, VPC isolation, least privilege IAM
6. **Cost-Optimized**: Reserved instances, spot instances, right-sizing

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USERS (Global)                                │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Route 53 (DNS) + CloudFront (CDN)                       │
│  • Global edge locations (400+)                                      │
│  • SSL/TLS termination                                               │
│  • DDoS protection                                                   │
│  • Cache static assets (images, CSS, JS)                             │
└─────────────┬───────────────────────────────────┬────────────────────┘
              │                                   │
              ▼ (Dynamic /api)                    ▼ (Static /*, /_next)
┌─────────────────────────────────────┐  ┌──────────────────────────┐
│     Application Load Balancer        │  │   S3 Bucket (Frontend)   │
│  • HTTPS only (port 443)             │  │  • Static Next.js build  │
│  • Health checks                     │  │  • Versioned             │
│  • Auto-scaling trigger              │  │  • Lifecycle policies    │
│  • WAF (Web Application Firewall)    │  └──────────────────────────┘
└─────────────┬───────────────────────┘
              │
      ┌───────┴────────┐
      │                │
      ▼                ▼
┌─────────────┐  ┌─────────────┐
│  ECS Fargate │  │  ECS Fargate │  (Backend API - FastAPI)
│  Container 1 │  │  Container 2 │
│  • Python    │  │  • Python    │
│  • FastAPI   │  │  • FastAPI   │
│  • Auto-scale│  │  • Auto-scale│
└─────┬────────┘  └─────┬────────┘
      │                 │
      └────────┬────────┘
               │
      ┌────────┴─────────────────────────┐
      │                                  │
      ▼                                  ▼
┌──────────────────┐          ┌──────────────────┐
│  MongoDB Atlas   │          │  ElastiCache     │
│  (M10 cluster)   │          │  (Redis)         │
│  • Multi-AZ      │          │  • t4g.micro     │
│  • Backups       │          │  • 0.5 GB RAM    │
│  • Encryption    │          │  • Multi-AZ      │
└──────────────────┘          └──────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                  Supporting Services                            │
├────────────────────────────────────────────────────────────────┤
│ • Secrets Manager  - API keys, DB passwords                    │
│ • CloudWatch      - Logs, metrics, alarms                      │
│ • ECR             - Docker image registry                      │
│ • CodePipeline    - CI/CD automation                           │
│ • Lambda          - Cron jobs (cleanup, analytics)             │
│ • SES             - Email notifications                        │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Component Details

### 1. **Frontend - Next.js on S3 + CloudFront**

#### Why This Approach?
- **Static Export**: Next.js builds to static HTML/CSS/JS
- **Cost**: $1-5/month for S3 storage + $10-20/month for CloudFront
- **Performance**: 10-50ms response time globally
- **Scalability**: Unlimited (CDN handles all traffic)

#### Configuration
```yaml
# Next.js Static Export
# next.config.js
module.exports = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true  # Or use CloudFront image optimization
  }
}

# S3 Bucket
BucketName: myteacher-frontend-prod
Region: us-east-1
Versioning: Enabled
Lifecycle:
  - Delete old versions after 30 days
  - Transition to Glacier after 90 days (backups)

# CloudFront Distribution
Origins:
  - S3 (frontend)
  - ALB (API at /api/*)
Behaviors:
  - /api/* → ALB (dynamic)
  - /* → S3 (static)
  - /_next/* → S3 (static chunks)
SSL: ACM certificate (free)
Caching:
  - Static assets: 1 year
  - HTML: 5 minutes (revalidate)
Compression: Gzip + Brotli
```

**Cost Estimate**: $15-30/month
- S3 storage: $0.023/GB (~1GB) = $0.023/month
- S3 requests: $0.0004/1000 = ~$2/month
- CloudFront data transfer: $0.085/GB first 10TB = ~$10-25/month
- CloudFront requests: $0.0075/10,000 = ~$3/month

---

### 2. **Backend - ECS Fargate (FastAPI)**

#### Why Fargate over EC2?
- **No server management**: AWS handles infrastructure
- **Pay per second**: Only pay for actual usage
- **Auto-scaling**: Scale to zero possible (but not recommended)
- **Cost-effective**: $25-50/month for 0.25 vCPU + 0.5GB RAM

#### Configuration
```yaml
# ECS Cluster
Name: myteacher-backend-cluster
Launch Type: FARGATE
VPC: Custom VPC with private subnets

# Task Definition
Family: myteacher-backend
CPU: 256 (0.25 vCPU) → Start small, scale up
Memory: 512 MB
Container:
  Image: {account}.dkr.ecr.{region}.amazonaws.com/myteacher-backend:latest
  Port: 8000
  Environment:
    - MONGODB_URL: from Secrets Manager
    - REDIS_URL: ElastiCache endpoint
    - ANTHROPIC_API_KEY: from Secrets Manager
    - ENVIRONMENT: production
  HealthCheck:
    Command: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
    Interval: 30s
    Timeout: 5s
    Retries: 3

# Service
DesiredCount: 2  # Minimum for high availability
MinCapacity: 2
MaxCapacity: 10
AutoScaling:
  CPU > 70% → Scale up (+1 task)
  CPU < 30% → Scale down (-1 task)
  Requests > 1000/min → Scale up
LoadBalancer: ALB target group
```

**Cost Estimate**: $30-60/month
- 2 tasks × 0.25 vCPU × $0.04048/hour = $59/month
- Data transfer: ~$5/month
- **Savings**: Use Fargate Spot for 70% discount on non-critical environments

---

### 3. **Database - MongoDB Atlas (Managed)**

#### Why Atlas over Self-Hosted?
- **No maintenance**: Automatic backups, patches, monitoring
- **Built-in HA**: Multi-AZ replication
- **Performance insights**: Query optimization tools
- **Cost**: $0.08/hour for M10 = $60/month

#### Configuration
```yaml
# MongoDB Atlas Cluster
Tier: M10 (Dedicated, 2 vCPUs, 8GB RAM, 10GB storage)
Region: us-east-1 (same as backend)
Replication: 3-node replica set (Multi-AZ)
Backups: Continuous (7-day retention)
Encryption: At rest + in transit (TLS)
IP Whitelist: VPC CIDR only (10.0.0.0/16)

# Indexes (optimize queries)
collections.users:
  - email: unique
collections.user_progress:
  - {user_id: 1, node_id: 1}: unique
collections.exercise_attempts:
  - {user_id: 1, submitted_at: -1}
collections.chat_sessions:
  - {user_id: 1, is_active: 1}
```

**Cost Estimate**: $60-80/month
- M10 cluster: $0.08/hour × 730 hours = $58/month
- Data transfer: $0.02/GB = ~$5/month
- Backups: Included in M10

**Alternative**: AWS DocumentDB (MongoDB-compatible)
- db.t3.medium: $0.073/hour = $53/month
- Storage: $0.10/GB = ~$10/month
- Total: ~$63/month (similar cost, but vendor lock-in)

---

### 4. **Cache - ElastiCache (Redis)**

#### Why Redis?
- **Session caching**: Reduce DB load
- **API response caching**: 10x faster responses
- **Rate limiting**: Track API usage per user
- **Real-time data**: User online status

#### Configuration
```yaml
# ElastiCache Cluster
Engine: Redis 7.0
Node Type: cache.t4g.micro (2 vCPUs, 0.5 GB)
Nodes: 1 (primary only for dev), 2 (primary + replica for prod)
AZ: Multi-AZ with automatic failover
Encryption: At rest + in transit
Eviction Policy: allkeys-lru (least recently used)

# Cache Keys
- session:{session_id} → TTL 7 days
- user:{user_id}:profile → TTL 1 hour
- content:{content_id} → TTL 24 hours
- rate_limit:{user_id} → TTL 1 minute
```

**Cost Estimate**: $12-25/month
- cache.t4g.micro: $0.017/hour × 730 = $12/month
- Multi-AZ replica (prod): $12 × 2 = $24/month
- Data transfer: Included

---

### 5. **Load Balancer - Application Load Balancer (ALB)**

#### Configuration
```yaml
# ALB
Name: myteacher-alb
Scheme: internet-facing
Subnets: Public subnets in 2 AZs
Security Group:
  - Inbound: 443 from 0.0.0.0/0 (HTTPS)
  - Outbound: 8000 to ECS security group

# Listener Rules
1. HTTPS:443 → Forward to ECS target group
2. HTTP:80 → Redirect to HTTPS:443

# Target Group
Protocol: HTTP
Port: 8000
HealthCheck: /health
HealthyThreshold: 2
UnhealthyThreshold: 3
Interval: 30s
Timeout: 5s

# SSL Certificate
Provider: AWS Certificate Manager (ACM)
Domain: api.myteacher.ai
Validation: DNS (automatic)
Cost: FREE
```

**Cost Estimate**: $20-30/month
- ALB: $0.0225/hour × 730 = $16/month
- LCU (Load Balancer Capacity Units): ~$10/month

---

### 6. **DNS & CDN - Route 53 + CloudFront**

#### Configuration
```yaml
# Route 53 Hosted Zone
Domain: myteacher.ai
Records:
  - myteacher.ai → CloudFront distribution (A + AAAA)
  - www.myteacher.ai → CloudFront (CNAME)
  - api.myteacher.ai → ALB (CNAME)
  - *.myteacher.ai → CloudFront (wildcard)

# CloudFront Distribution
Origins:
  1. S3 (frontend) - origin.myteacher.ai
  2. ALB (API) - api.myteacher.ai
Behaviors:
  - /api/* → ALB origin
  - /* → S3 origin
Edge Locations: All (217 locations globally)
SSL: TLS 1.2+ only
Security:
  - WAF: OWASP Top 10 rules
  - Shield Standard: DDoS protection (free)
  - Geo-restriction: None (or block specific countries)
```

**Cost Estimate**: $15-40/month
- Route 53 hosted zone: $0.50/month
- Route 53 queries: $0.40/million = ~$1/month
- CloudFront: See frontend section (~$15-30/month)
- WAF: $5/month + $1 per rule + $0.60 per million requests = ~$10/month

---

## 💰 Total Cost Breakdown

### Development Environment (Low Traffic)
| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| **S3** | 1 GB storage, 10k requests | $3 |
| **CloudFront** | 10 GB transfer, 100k requests | $10 |
| **ECS Fargate** | 1 task × 0.25 vCPU × 0.5 GB | $30 |
| **MongoDB Atlas** | M0 (Free tier) | $0 |
| **ElastiCache** | cache.t4g.micro single node | $12 |
| **ALB** | 1 ALB + minimal LCU | $20 |
| **Route 53** | 1 hosted zone + minimal queries | $1 |
| **Secrets Manager** | 2 secrets | $1 |
| **CloudWatch** | Logs + metrics (first 10 GB free) | $5 |
| **ECR** | Docker image storage (1 GB) | $0.10 |
| **Total** | | **$82/month** |

### Production Environment (Medium Traffic - 10k users/month)
| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| **S3** | 5 GB storage, 1M requests | $5 |
| **CloudFront** | 500 GB transfer, 10M requests | $60 |
| **ECS Fargate** | 2-4 tasks (avg 3) × 0.25 vCPU × 0.5 GB | $90 |
| **MongoDB Atlas** | M10 (2 vCPU, 8 GB RAM, 10 GB storage) | $60 |
| **ElastiCache** | cache.t4g.micro Multi-AZ (2 nodes) | $24 |
| **ALB** | 1 ALB + moderate LCU | $30 |
| **Route 53** | 1 hosted zone + 1M queries | $2 |
| **WAF** | OWASP rules + 10M requests | $15 |
| **Secrets Manager** | 5 secrets | $2 |
| **CloudWatch** | 50 GB logs + custom metrics | $25 |
| **ECR** | 5 GB images | $0.50 |
| **Lambda** | Cron jobs (analytics, cleanup) | $5 |
| **SES** | 10k emails/month | $1 |
| **Total** | | **$319/month** |

### High Traffic (100k users/month)
| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| **S3** | 20 GB storage, 10M requests | $15 |
| **CloudFront** | 5 TB transfer, 100M requests | $450 |
| **ECS Fargate** | 5-10 tasks (avg 7) × 0.5 vCPU × 1 GB | $410 |
| **MongoDB Atlas** | M30 (4 vCPU, 16 GB RAM, 40 GB storage) | $290 |
| **ElastiCache** | cache.m6g.large Multi-AZ (8 GB) | $150 |
| **ALB** | 1 ALB + high LCU | $80 |
| **Route 53** | 1 hosted zone + 100M queries | $40 |
| **WAF** | OWASP rules + 100M requests | $65 |
| **Secrets Manager** | 10 secrets | $4 |
| **CloudWatch** | 500 GB logs + custom metrics | $250 |
| **ECR** | 50 GB images | $5 |
| **Lambda** | Heavy usage | $50 |
| **SES** | 1M emails/month | $100 |
| **Total** | | **$1,909/month** |

---

## 🚀 Cost Optimization Strategies

### 1. **Fargate Spot Instances** (70% discount)
```yaml
# For non-production environments
CapacityProvider:
  Name: FARGATE_SPOT
  Strategy:
    - Base: 1  # Always 1 on-demand
    - Weight: 4  # 80% spot, 20% on-demand
Savings: $60 → $24/month (60% reduction)
```

### 2. **Reserved Instances** (30-60% discount)
- MongoDB Atlas: 1-year reserved = 20% off
- ElastiCache: 1-year reserved = 37% off
- Total savings: ~$20-30/month

### 3. **S3 Intelligent-Tiering**
```yaml
# Automatically moves objects to cheaper tiers
Lifecycle:
  - Transition to Standard-IA after 30 days
  - Transition to Glacier after 90 days
  - Delete old versions after 365 days
Savings: ~$5/month
```

### 4. **CloudFront Cost Optimization**
- Use CloudFront Functions ($0.10 per 1M invocations)
- Cache aggressively (TTL 1 year for static)
- Enable compression (reduce transfer by 70%)
- Savings: ~$20/month

### 5. **Right-Sizing**
```bash
# Monitor and adjust
# Start small:
ECS: 0.25 vCPU → 0.5 vCPU only if CPU > 80%
MongoDB: M10 → M30 only if connections > 500
ElastiCache: micro → small only if memory > 90%
```

### 6. **Automated Scaling**
```yaml
# Scale to minimum during off-hours
Schedule:
  - 00:00-06:00 UTC: 1 task (night)
  - 06:00-22:00 UTC: 2-10 tasks (day)
  - 22:00-00:00 UTC: 1 task (evening)
Savings: ~$15/month
```

---

## 🔒 Security Best Practices

### 1. **Network Security**
```yaml
# VPC Configuration
CIDR: 10.0.0.0/16
Subnets:
  Public (ALB): 10.0.1.0/24, 10.0.2.0/24
  Private (ECS, Redis): 10.0.10.0/24, 10.0.11.0/24
  Data (MongoDB): 10.0.20.0/24, 10.0.21.0/24

# Security Groups
ALB-SG:
  Inbound: 443 from 0.0.0.0/0
  Outbound: 8000 to ECS-SG
ECS-SG:
  Inbound: 8000 from ALB-SG
  Outbound: 27017 to MongoDB, 6379 to Redis, 443 to internet (Anthropic API)
Redis-SG:
  Inbound: 6379 from ECS-SG
MongoDB-SG:
  Inbound: 27017 from ECS-SG
```

### 2. **IAM Roles & Policies**
```yaml
# ECS Task Role (least privilege)
Policies:
  - SecretsManagerReadWrite (limited to myteacher/* secrets)
  - CloudWatchLogsWrite (limited to /aws/ecs/myteacher/*)
  - S3Read (limited to myteacher-uploads-bucket)

# ECS Task Execution Role
Policies:
  - AmazonECSTaskExecutionRolePolicy
  - ECRReadOnly

# CodePipeline Service Role
Policies:
  - CodePipelineServiceRole
  - S3FullAccess (limited to myteacher-pipeline-bucket)
  - ECRFullAccess (limited to myteacher-backend repo)
```

### 3. **Secrets Management**
```yaml
# AWS Secrets Manager
Secrets:
  - /myteacher/prod/mongodb-url
  - /myteacher/prod/redis-url
  - /myteacher/prod/anthropic-api-key
  - /myteacher/prod/jwt-secret
  - /myteacher/prod/ses-credentials
Encryption: AWS KMS (myteacher-secrets-key)
Rotation: Manual for API keys, automatic for DB passwords (30 days)
```

### 4. **WAF Rules**
```yaml
# AWS WAF - OWASP Top 10
Rules:
  - AWS-AWSManagedRulesCommonRuleSet (core)
  - AWS-AWSManagedRulesKnownBadInputsRuleSet (SQLi, XSS)
  - AWS-AWSManagedRulesLinuxRuleSet (Linux-specific attacks)
  - Custom: Rate limiting (100 requests/5 min per IP)
  - Custom: Geo-blocking (if needed)
Action: Block malicious, count suspicious
```

### 5. **SSL/TLS**
```yaml
# Enforce HTTPS everywhere
CloudFront:
  ViewerProtocolPolicy: redirect-to-https
  MinimumProtocolVersion: TLSv1.2_2021
ALB:
  Listener: HTTPS:443 only
  SSLPolicy: ELBSecurityPolicy-TLS-1-2-Ext-2018-06
MongoDB Atlas:
  requireTLS: true
```

---

## 📈 Performance Optimization

### 1. **CloudFront Caching Strategy**
```yaml
# Cache behaviors
Static Assets (/_next/*, /images/*, /fonts/):
  TTL: 31536000 (1 year)
  QueryString: None
  Cookies: None

HTML Pages (/, /dashboard, etc.):
  TTL: 300 (5 minutes)
  QueryString: None
  Cookies: Forward auth cookies

API (/api/*):
  TTL: 0 (no caching)
  QueryString: All
  Cookies: All
  Headers: Authorization, Content-Type
```

### 2. **ECS Auto-Scaling Policies**
```yaml
# Target Tracking Scaling
Policies:
  - TargetCPUUtilization: 70%
    ScaleOutCooldown: 60s
    ScaleInCooldown: 300s
  - TargetRequestCountPerTarget: 1000
    ScaleOutCooldown: 30s
    ScaleInCooldown: 180s
```

### 3. **Database Optimization**
```yaml
# MongoDB Connection Pooling
mongoClient:
  maxPoolSize: 100
  minPoolSize: 10
  maxIdleTimeMS: 45000
  serverSelectionTimeoutMS: 5000

# Read Preference
Primary: For writes
Secondary: For reads (when eventual consistency OK)

# Indexes (see DATABASE_SCHEMA.md)
```

### 4. **Redis Caching**
```python
# Cache frequently accessed data
@cache(ttl=3600)  # 1 hour
async def get_user_profile(user_id: str):
    # Check Redis first
    cached = await redis.get(f"user:{user_id}:profile")
    if cached:
        return json.loads(cached)

    # Fetch from DB
    profile = await db.user_profiles.find_one({"user_id": user_id})

    # Store in Redis
    await redis.setex(f"user:{user_id}:profile", 3600, json.dumps(profile))

    return profile
```

---

## 🔄 CI/CD Pipeline (AWS CodePipeline)

### Pipeline Stages

```yaml
# CodePipeline Configuration
Name: myteacher-cicd-pipeline

# Stage 1: Source
Source:
  Provider: GitHub
  Repository: your-username/myteacher
  Branch: main
  Webhook: Enabled (auto-trigger on push)

# Stage 2: Build (CodeBuild)
Build:
  Backend:
    Buildspec: backend/buildspec.yml
    Environment:
      ComputeType: BUILD_GENERAL1_SMALL
      Image: aws/codebuild/standard:7.0
    Steps:
      - Install dependencies (pip install -r requirements.txt)
      - Run tests (pytest)
      - Build Docker image
      - Push to ECR (myteacher-backend:latest + :${GIT_SHA})
  Frontend:
    Buildspec: frontend/buildspec.yml
    Environment:
      ComputeType: BUILD_GENERAL1_SMALL
      Image: aws/codebuild/standard:7.0
    Steps:
      - Install dependencies (npm ci)
      - Run tests (npm test)
      - Build static export (npm run build)
      - Sync to S3 (aws s3 sync out/ s3://myteacher-frontend-prod/)
      - Invalidate CloudFront cache

# Stage 3: Deploy (ECS Rolling Update)
Deploy:
  Provider: ECS
  Cluster: myteacher-backend-cluster
  Service: myteacher-backend-service
  DeploymentConfig:
    Type: ECS
    MinimumHealthyPercent: 50
    MaximumPercent: 200
    HealthCheckGracePeriod: 60s
  ImageTag: ${GIT_SHA}  # Blue-green via task definition revision
```

### Build Specs

**Backend buildspec.yml:**
```yaml
version: 0.2
phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
  build:
    commands:
      - echo Build started on `date`
      - cd backend
      - docker build -t myteacher-backend:$CODEBUILD_RESOLVED_SOURCE_VERSION .
      - docker tag myteacher-backend:$CODEBUILD_RESOLVED_SOURCE_VERSION $ECR_REPO:latest
      - docker tag myteacher-backend:$CODEBUILD_RESOLVED_SOURCE_VERSION $ECR_REPO:$CODEBUILD_RESOLVED_SOURCE_VERSION
  post_build:
    commands:
      - echo Pushing images...
      - docker push $ECR_REPO:latest
      - docker push $ECR_REPO:$CODEBUILD_RESOLVED_SOURCE_VERSION
      - echo Writing image definitions file...
      - printf '[{"name":"myteacher-backend","imageUri":"%s"}]' $ECR_REPO:$CODEBUILD_RESOLVED_SOURCE_VERSION > imagedefinitions.json
artifacts:
  files: imagedefinitions.json
```

**Frontend buildspec.yml:**
```yaml
version: 0.2
phases:
  pre_build:
    commands:
      - echo Installing dependencies...
      - cd frontend
      - npm ci
  build:
    commands:
      - echo Building static export...
      - npm run build
      - echo Build completed on `date`
  post_build:
    commands:
      - echo Syncing to S3...
      - aws s3 sync out/ s3://$S3_BUCKET/ --delete --cache-control "public, max-age=31536000, immutable"
      - echo Invalidating CloudFront...
      - aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"
artifacts:
  files:
    - '**/*'
  base-directory: frontend/out
```

---

## 📊 Monitoring & Observability

### 1. **CloudWatch Dashboards**
```yaml
# Custom Dashboard: myteacher-prod-overview
Widgets:
  Row 1:
    - ECS CPU Utilization (all tasks)
    - ECS Memory Utilization (all tasks)
    - ALB Request Count
    - ALB Target Response Time
  Row 2:
    - MongoDB Connections (Atlas API)
    - Redis CPU Utilization
    - CloudFront Requests
    - CloudFront Cache Hit Rate
  Row 3:
    - API Errors (5xx, 4xx)
    - Average API Response Time
    - Active Users (custom metric)
    - AI Tool Success Rate (custom metric)
```

### 2. **CloudWatch Alarms**
```yaml
# Critical Alarms (PagerDuty)
HighErrorRate:
  Metric: ALB 5xx errors
  Threshold: > 10 errors in 5 minutes
  Action: SNS → PagerDuty

DatabaseConnectionFailure:
  Metric: MongoDB connection errors (custom)
  Threshold: > 5 errors in 2 minutes
  Action: SNS → PagerDuty

HighResponseTime:
  Metric: ALB TargetResponseTime
  Threshold: > 2 seconds for 3 consecutive periods
  Action: SNS → Slack

# Warning Alarms (Slack)
HighCPU:
  Metric: ECS CPU Utilization
  Threshold: > 80% for 10 minutes
  Action: SNS → Slack → Consider scaling

LowCacheHitRate:
  Metric: Redis cache hits / total requests
  Threshold: < 70%
  Action: SNS → Slack → Review cache strategy
```

### 3. **Application Performance Monitoring (APM)**
```yaml
# AWS X-Ray (Distributed Tracing)
Enable: true
Services:
  - ALB
  - ECS (FastAPI with aws-xray-sdk)
  - DynamoDB (if used)
  - Lambda
SamplingRule: 5% of requests (cost-effective)

# Custom Metrics (CloudWatch)
Namespace: MyTeacher/Production
Metrics:
  - AIToolSuccessRate (per tool)
  - AIResponseTime (per agent)
  - UserExerciseCompletionRate
  - ActiveLearningSessionsCount
  - WeakPointIdentificationAccuracy
```

### 4. **Logging Strategy**
```yaml
# CloudWatch Logs Groups
Groups:
  - /aws/ecs/myteacher-backend
  - /aws/lambda/myteacher-analytics
  - /aws/codebuild/myteacher-backend-build
  - /aws/codebuild/myteacher-frontend-build
Retention: 30 days (adjustable)
Encryption: KMS

# Log Insights Queries
Query1: API errors by endpoint
Query2: Slow API requests (> 1s)
Query3: AI tool failures
Query4: User authentication failures
```

---

## 🚀 Deployment Steps

See [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md) for detailed step-by-step instructions.

---

## 🔄 Disaster Recovery

### 1. **Backup Strategy**
```yaml
# MongoDB Atlas
Backups:
  Type: Continuous
  Retention: 7 days
  Snapshots: Daily at 03:00 UTC
  PointInTimeRecovery: Enabled

# S3 (Frontend)
Versioning: Enabled
Lifecycle:
  - Keep current version indefinitely
  - Delete non-current versions after 30 days
CrossRegionReplication: Optional (to us-west-2)

# Secrets Manager
Automatic snapshots every 7 days
```

### 2. **RTO/RPO Targets**
- **Recovery Time Objective (RTO)**: < 1 hour
- **Recovery Point Objective (RPO)**: < 15 minutes
- **Data Loss Tolerance**: < 5 minutes (continuous MongoDB backups)

### 3. **DR Runbook**
1. **Database Failure**: Restore from latest Atlas snapshot (10 minutes)
2. **ECS Service Failure**: Re-deploy from latest ECR image (5 minutes)
3. **Region Failure**: Failover to CloudFront secondary origin (manual, 30 minutes)
4. **Complete Outage**: Deploy to new region from backups (1 hour)

---

## 📝 Post-Deployment Checklist

- [ ] All services healthy (ECS, MongoDB, Redis, ALB)
- [ ] CloudFront cache warming (pre-populate common pages)
- [ ] SSL certificates valid and auto-renewing
- [ ] DNS propagated globally (check with `dig`)
- [ ] Monitoring dashboards showing data
- [ ] Alarms configured and tested
- [ ] Backup jobs running successfully
- [ ] Load testing completed (target: 1000 req/s)
- [ ] Security audit passed (Prowler, AWS Inspector)
- [ ] Cost budget alerts configured ($500/month threshold)
- [ ] Documentation updated (README, runbooks)
- [ ] Team trained on incident response procedures

---

## 🎯 Next Steps

1. **Setup AWS Account**: Create IAM users, enable MFA
2. **Reserve Domain**: Register myteacher.ai on Route 53
3. **Create VPC**: Follow network architecture above
4. **Deploy MongoDB Atlas**: M10 cluster in us-east-1
5. **Deploy ElastiCache**: cache.t4g.micro Multi-AZ
6. **Setup ECR**: Create repository for backend images
7. **Deploy ECS Cluster**: Fargate with 2 tasks
8. **Configure ALB**: With health checks and SSL
9. **Deploy Frontend**: S3 + CloudFront
10. **Setup CI/CD**: CodePipeline with GitHub webhook
11. **Configure Monitoring**: CloudWatch dashboards and alarms
12. **Load Testing**: Use Locust or k6 (target 1000 concurrent users)
13. **Go Live**: Update DNS, announce launch

---

**Deployment Owner**: Yohans Bekele
**AWS Architect**: Claude AI Assistant
**Last Review**: December 9, 2025
**Next Review**: March 1, 2026

---

**For detailed deployment instructions, see:** [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md)
