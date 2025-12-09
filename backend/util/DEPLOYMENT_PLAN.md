# MyTeacher AI - Step-by-Step Deployment Plan
## From Zero to Production in 4 Hours

**Target**: AWS Cloud (us-east-1)
**Audience**: DevOps Engineers, SysAdmins
**Prerequisites**: AWS Account, Domain name, Basic AWS CLI knowledge
**Estimated Time**: 3-4 hours
**Cost**: ~$300/month (production with 10k users)

---

## 📋 Pre-Deployment Checklist

- [ ] AWS Account with billing enabled
- [ ] AWS CLI installed (`aws --version`)
- [ ] Docker installed (`docker --version`)
- [ ] Git repository access
- [ ] Domain name registered (e.g., myteacher.ai)
- [ ] Anthropic API key (https://console.anthropic.com)
- [ ] MongoDB Atlas account (https://cloud.mongodb.com)

---

## Phase 1: AWS Account Setup (30 minutes)

### Step 1.1: Create IAM Admin User
```bash
# Login to AWS Console as root
# Go to IAM → Users → Create User

Username: myteacher-admin
Permissions: AdministratorAccess (managed policy)
Access type:
  - Programmatic access (access key)
  - AWS Management Console access

# Save credentials securely
ACCESS_KEY_ID=AKIA...
SECRET_ACCESS_KEY=...
CONSOLE_URL=https://123456789012.signin.aws.amazon.com/console
```

### Step 1.2: Configure AWS CLI
```bash
# Configure AWS CLI
aws configure
AWS Access Key ID: <ACCESS_KEY_ID>
AWS Secret Access Key: <SECRET_ACCESS_KEY>
Default region name: us-east-1
Default output format: json

# Test connection
aws sts get-caller-identity
# Should show your account ID and ARN
```

### Step 1.3: Enable Cost Explorer & Budgets
```bash
# Via AWS Console
# Go to Billing → Cost Explorer → Enable Cost Explorer
# Go to Billing → Budgets → Create Budget
Budget Type: Cost budget
Budget Amount: $500/month
Alert: Email when actual > $400 (80%)
```

---

## Phase 2: Network Infrastructure (30 minutes)

### Step 2.1: Create VPC
```bash
# Create VPC
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=myteacher-vpc}]'

VPC_ID=vpc-xxxxx  # Save this

# Enable DNS
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames
```

### Step 2.2: Create Subnets
```bash
# Public Subnet 1 (us-east-1a)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=myteacher-public-1a}]'
PUBLIC_SUBNET_1=subnet-xxxxx

# Public Subnet 2 (us-east-1b)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=myteacher-public-1b}]'
PUBLIC_SUBNET_2=subnet-xxxxx

# Private Subnet 1 (us-east-1a)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.10.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=myteacher-private-1a}]'
PRIVATE_SUBNET_1=subnet-xxxxx

# Private Subnet 2 (us-east-1b)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.11.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=myteacher-private-1b}]'
PRIVATE_SUBNET_2=subnet-xxxxx
```

### Step 2.3: Internet Gateway & Routing
```bash
# Create Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=myteacher-igw}]'
IGW_ID=igw-xxxxx

# Attach to VPC
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID

# Create Route Table for Public Subnets
aws ec2 create-route-table --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=myteacher-public-rt}]'
PUBLIC_RT=rtb-xxxxx

# Add route to IGW
aws ec2 create-route --route-table-id $PUBLIC_RT --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID

# Associate subnets
aws ec2 associate-route-table --subnet-id $PUBLIC_SUBNET_1 --route-table-id $PUBLIC_RT
aws ec2 associate-route-table --subnet-id $PUBLIC_SUBNET_2 --route-table-id $PUBLIC_RT
```

### Step 2.4: NAT Gateway (for private subnets)
```bash
# Allocate Elastic IP
aws ec2 allocate-address --domain vpc
EIP_ID=eipalloc-xxxxx

# Create NAT Gateway in public subnet
aws ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET_1 \
  --allocation-id $EIP_ID \
  --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=myteacher-nat}]'
NAT_ID=nat-xxxxx

# Create Route Table for Private Subnets
aws ec2 create-route-table --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=myteacher-private-rt}]'
PRIVATE_RT=rtb-xxxxx

# Add route to NAT
aws ec2 create-route --route-table-id $PRIVATE_RT --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $NAT_ID

# Associate private subnets
aws ec2 associate-route-table --subnet-id $PRIVATE_SUBNET_1 --route-table-id $PRIVATE_RT
aws ec2 associate-route-table --subnet-id $PRIVATE_SUBNET_2 --route-table-id $PRIVATE_RT
```

---

## Phase 3: Database Setup (45 minutes)

### Step 3.1: MongoDB Atlas
```bash
# 1. Go to https://cloud.mongodb.com
# 2. Create new project: "MyTeacher Production"
# 3. Build a Cluster:

Configuration:
  Provider: AWS
  Region: us-east-1 (N. Virginia)
  Tier: M10 (Dedicated)
  Cluster Name: myteacher-prod

# 4. Security:
Database Access → Add New Database User:
  Username: myteacher_app
  Password: <generate strong password>
  Role: Atlas admin

Network Access → Add IP Address:
  Type: CIDR
  Address: 10.0.0.0/16 (your VPC CIDR)
  Comment: VPC Private Subnets

# 5. Connect → Get Connection String:
MONGODB_URL=mongodb+srv://myteacher_app:<password>@myteacher-prod.xxxxx.mongodb.net/myteacher?retryWrites=true&w=majority

# Save to Secrets Manager (see Step 4.1)
```

### Step 3.2: ElastiCache Redis
```bash
# Create Subnet Group
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name myteacher-redis-subnet \
  --cache-subnet-group-description "Redis subnet group" \
  --subnet-ids $PRIVATE_SUBNET_1 $PRIVATE_SUBNET_2

# Create Security Group
aws ec2 create-security-group \
  --group-name myteacher-redis-sg \
  --description "Redis security group" \
  --vpc-id $VPC_ID
REDIS_SG=sg-xxxxx

# Allow Redis port from ECS (we'll create ECS SG later)
aws ec2 authorize-security-group-ingress \
  --group-id $REDIS_SG \
  --protocol tcp \
  --port 6379 \
  --source-group <ECS_SG>  # Fill after Step 5.2

# Create Redis Cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id myteacher-redis \
  --cache-node-type cache.t4g.micro \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --cache-subnet-group-name myteacher-redis-subnet \
  --security-group-ids $REDIS_SG \
  --tags Key=Name,Value=myteacher-redis

# Wait 10 minutes for creation
aws elasticache describe-cache-clusters \
  --cache-cluster-id myteacher-redis \
  --show-cache-node-info

# Get endpoint
REDIS_URL=myteacher-redis.xxxxx.0001.use1.cache.amazonaws.com:6379
```

---

## Phase 4: Secrets Management (15 minutes)

### Step 4.1: Store Secrets in AWS Secrets Manager
```bash
# Store MongoDB URL
aws secretsmanager create-secret \
  --name /myteacher/prod/mongodb-url \
  --description "MongoDB Atlas connection string" \
  --secret-string "$MONGODB_URL"

# Store Redis URL
aws secretsmanager create-secret \
  --name /myteacher/prod/redis-url \
  --description "ElastiCache Redis endpoint" \
  --secret-string "redis://$REDIS_URL"

# Store Anthropic API Key
aws secretsmanager create-secret \
  --name /myteacher/prod/anthropic-api-key \
  --description "Anthropic Claude API key" \
  --secret-string "sk-ant-..."

# Generate and store JWT secret
JWT_SECRET=$(openssl rand -base64 32)
aws secretsmanager create-secret \
  --name /myteacher/prod/jwt-secret \
  --description "JWT signing secret" \
  --secret-string "$JWT_SECRET"

# List secrets
aws secretsmanager list-secrets | grep myteacher
```

---

## Phase 5: Container Setup (ECS + ECR) (45 minutes)

### Step 5.1: Create ECR Repository
```bash
# Create repository for backend
aws ecr create-repository \
  --repository-name myteacher-backend \
  --image-scanning-configuration scanOnPush=true \
  --tags Key=Name,Value=myteacher-backend

ECR_REPO=$(aws ecr describe-repositories --repository-names myteacher-backend --query 'repositories[0].repositoryUri' --output text)
echo $ECR_REPO
# Example: 123456789012.dkr.ecr.us-east-1.amazonaws.com/myteacher-backend
```

### Step 5.2: Build and Push Docker Image
```bash
# Navigate to backend directory
cd backend

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO

# Build image
docker build -t myteacher-backend:latest .

# Tag image
docker tag myteacher-backend:latest $ECR_REPO:latest
docker tag myteacher-backend:latest $ECR_REPO:v1.0.0

# Push to ECR
docker push $ECR_REPO:latest
docker push $ECR_REPO:v1.0.0

# Verify
aws ecr list-images --repository-name myteacher-backend
```

### Step 5.3: Create ECS Cluster
```bash
# Create cluster
aws ecs create-cluster \
  --cluster-name myteacher-backend-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 \
  --tags key=Name,value=myteacher-backend-cluster
```

### Step 5.4: Create Security Groups
```bash
# ALB Security Group
aws ec2 create-security-group \
  --group-name myteacher-alb-sg \
  --description "ALB security group" \
  --vpc-id $VPC_ID
ALB_SG=sg-xxxxx

# Allow HTTPS from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Allow HTTP (redirect to HTTPS)
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# ECS Security Group
aws ec2 create-security-group \
  --group-name myteacher-ecs-sg \
  --description "ECS tasks security group" \
  --vpc-id $VPC_ID
ECS_SG=sg-xxxxx

# Allow 8000 from ALB
aws ec2 authorize-security-group-ingress \
  --group-id $ECS_SG \
  --protocol tcp \
  --port 8000 \
  --source-group $ALB_SG

# Allow HTTPS outbound (for Anthropic API)
aws ec2 authorize-security-group-egress \
  --group-id $ECS_SG \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

### Step 5.5: Create IAM Roles
```bash
# Create Task Execution Role (needed by ECS to pull images, write logs)
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name myteacher-ecs-execution-role \
  --assume-role-policy-document file://trust-policy.json

aws iam attach-role-policy \
  --role-name myteacher-ecs-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Create Task Role (used by application code)
aws iam create-role \
  --role-name myteacher-ecs-task-role \
  --assume-role-policy-document file://trust-policy.json

# Attach Secrets Manager read policy
cat > task-role-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ],
    "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:/myteacher/prod/*"
  }]
}
EOF

aws iam put-role-policy \
  --role-name myteacher-ecs-task-role \
  --policy-name SecretsManagerAccess \
  --policy-document file://task-role-policy.json
```

### Step 5.6: Create Task Definition
```bash
cat > task-definition.json <<EOF
{
  "family": "myteacher-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/myteacher-ecs-execution-role",
  "taskRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/myteacher-ecs-task-role",
  "containerDefinitions": [{
    "name": "myteacher-backend",
    "image": "$ECR_REPO:latest",
    "portMappings": [{
      "containerPort": 8000,
      "protocol": "tcp"
    }],
    "secrets": [
      {"name": "MONGODB_URL", "valueFrom": "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:/myteacher/prod/mongodb-url"},
      {"name": "REDIS_URL", "valueFrom": "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:/myteacher/prod/redis-url"},
      {"name": "ANTHROPIC_API_KEY", "valueFrom": "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:/myteacher/prod/anthropic-api-key"},
      {"name": "JWT_SECRET", "valueFrom": "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:/myteacher/prod/jwt-secret"}
    ],
    "environment": [
      {"name": "ENVIRONMENT", "value": "production"},
      {"name": "LOG_LEVEL", "value": "INFO"}
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/aws/ecs/myteacher-backend",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "backend"
      }
    },
    "healthCheck": {
      "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
      "interval": 30,
      "timeout": 5,
      "retries": 3,
      "startPeriod": 60
    }
  }]
}
EOF

# Replace <ACCOUNT_ID> with your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
sed -i "s/<ACCOUNT_ID>/$ACCOUNT_ID/g" task-definition.json

# Create CloudWatch log group
aws logs create-log-group --log-group-name /aws/ecs/myteacher-backend

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

---

## Phase 6: Load Balancer (30 minutes)

### Step 6.1: Create Application Load Balancer
```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name myteacher-alb \
  --subnets $PUBLIC_SUBNET_1 $PUBLIC_SUBNET_2 \
  --security-groups $ALB_SG \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --tags Key=Name,Value=myteacher-alb

ALB_ARN=$(aws elbv2 describe-load-balancers --names myteacher-alb --query 'LoadBalancers[0].LoadBalancerArn' --output text)
ALB_DNS=$(aws elbv2 describe-load-balancers --names myteacher-alb --query 'LoadBalancers[0].DNSName' --output text)
echo "ALB DNS: $ALB_DNS"
```

### Step 6.2: Create Target Group
```bash
aws elbv2 create-target-group \
  --name myteacher-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3

TG_ARN=$(aws elbv2 describe-target-groups --names myteacher-backend-tg --query 'TargetGroups[0].TargetGroupArn' --output text)
```

### Step 6.3: Create Listener (HTTP → HTTPS redirect)
```bash
# HTTP listener (redirect to HTTPS)
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,RedirectConfig={Protocol=HTTPS,Port=443,StatusCode=HTTP_301}

# HTTPS listener (will add after getting SSL certificate)
# See Step 7.2
```

---

## Phase 7: DNS & SSL (30 minutes)

### Step 7.1: Route 53 Hosted Zone
```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name myteacher.ai \
  --caller-reference $(date +%s)

HOSTED_ZONE_ID=$(aws route53 list-hosted-zones-by-name --dns-name myteacher.ai --query 'HostedZones[0].Id' --output text)

# Get name servers
aws route53 get-hosted-zone --id $HOSTED_ZONE_ID --query 'DelegationSet.NameServers'

# Update your domain registrar with these name servers
# (e.g., GoDaddy, Namecheap, etc.)
```

### Step 7.2: Request SSL Certificate (ACM)
```bash
# Request certificate
aws acm request-certificate \
  --domain-name myteacher.ai \
  --subject-alternative-names www.myteacher.ai api.myteacher.ai \
  --validation-method DNS \
  --region us-east-1

CERT_ARN=$(aws acm list-certificates --query 'CertificateSummaryList[?DomainName==`myteacher.ai`].CertificateArn' --output text)

# Get validation CNAME records
aws acm describe-certificate --certificate-arn $CERT_ARN \
  --query 'Certificate.DomainValidationOptions[*].[ResourceRecord.Name,ResourceRecord.Value]' \
  --output table

# Add these CNAME records to Route 53
# (Or AWS will auto-validate if using Route 53)

# Wait for validation
aws acm wait certificate-validated --certificate-arn $CERT_ARN
```

### Step 7.3: Add HTTPS Listener to ALB
```bash
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=$CERT_ARN \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

---

## Phase 8: Deploy ECS Service (20 minutes)

### Step 8.1: Create ECS Service
```bash
aws ecs create-service \
  --cluster myteacher-backend-cluster \
  --service-name myteacher-backend-service \
  --task-definition myteacher-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --platform-version LATEST \
  --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2],securityGroups=[$ECS_SG],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=$TG_ARN,containerName=myteacher-backend,containerPort=8000" \
  --health-check-grace-period-seconds 60

# Wait for service to stabilize
aws ecs wait services-stable \
  --cluster myteacher-backend-cluster \
  --services myteacher-backend-service
```

### Step 8.2: Configure Auto-Scaling
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/myteacher-backend-cluster/myteacher-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy (CPU-based)
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/myteacher-backend-cluster/myteacher-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json

cat > scaling-policy.json <<EOF
{
  "TargetValue": 70.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
  },
  "ScaleOutCooldown": 60,
  "ScaleInCooldown": 300
}
EOF
```

---

## Phase 9: Frontend Deployment (S3 + CloudFront) (30 minutes)

### Step 9.1: Build Frontend
```bash
cd ../frontend

# Install dependencies
npm ci

# Build static export
npm run build
# Output: ./out directory
```

### Step 9.2: Create S3 Bucket
```bash
aws s3 mb s3://myteacher-frontend-prod --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket myteacher-frontend-prod \
  --versioning-configuration Status=Enabled

# Block public access (CloudFront will access via OAI)
aws s3api put-public-access-block \
  --bucket myteacher-frontend-prod \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### Step 9.3: Upload to S3
```bash
# Sync files
aws s3 sync out/ s3://myteacher-frontend-prod/ \
  --exclude "*.map" \
  --cache-control "public, max-age=31536000, immutable"

# Set index.html to shorter cache
aws s3 cp out/index.html s3://myteacher-frontend-prod/index.html \
  --cache-control "public, max-age=300"
```

### Step 9.4: Create CloudFront Distribution
```bash
# Create Origin Access Identity
aws cloudfront create-cloud-front-origin-access-identity \
  --cloud-front-origin-access-identity-config \
    "CallerReference=$(date +%s),Comment=myteacher-oai"

OAI_ID=$(aws cloudfront list-cloud-front-origin-access-identities --query 'CloudFrontOriginAccessIdentityList.Items[?Comment==`myteacher-oai`].Id' --output text)

# Update S3 bucket policy
cat > bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity $OAI_ID"
    },
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::myteacher-frontend-prod/*"
  }]
}
EOF

aws s3api put-bucket-policy \
  --bucket myteacher-frontend-prod \
  --policy file://bucket-policy.json

# Create CloudFront distribution
# (This is complex, use AWS Console or CloudFormation template)
# See: AWS Console → CloudFront → Create Distribution
```

**CloudFront Configuration (via Console)**:
```yaml
Origins:
  - S3: myteacher-frontend-prod
    OAI: $OAI_ID
  - Custom (ALB): $ALB_DNS
    Protocol: HTTPS only

Behaviors:
  - /api/* → ALB origin
  - /* → S3 origin (default)

Cache:
  - /api/*: No caching
  - /_next/static/*: 1 year
  - /*: 5 minutes

SSL: Use $CERT_ARN
Custom Domain: myteacher.ai, www.myteacher.ai
```

---

## Phase 10: Final Configuration (20 minutes)

### Step 10.1: Update Route 53 Records
```bash
# Get CloudFront distribution domain
CF_DOMAIN=d123456abcdef.cloudfront.net  # From Step 9.4

# Create A record for apex domain
cat > apex-record.json <<EOF
{
  "Comment": "Apex domain to CloudFront",
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "myteacher.ai",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "Z2FDTNDATAQYW2",
        "DNSName": "$CF_DOMAIN",
        "EvaluateTargetHealth": false
      }
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://apex-record.json

# Create CNAME for www
cat > www-record.json <<EOF
{
  "Comment": "www to CloudFront",
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "www.myteacher.ai",
      "Type": "CNAME",
      "TTL": 300,
      "ResourceRecords": [{"Value": "$CF_DOMAIN"}]
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://www-record.json
```

### Step 10.2: Seed Database
```bash
# Run seed script on one ECS task
cd ../backend

# Option 1: Local execution (if you have MongoDB connection)
python -m app.scripts.seed_data

# Option 2: Run in ECS task
aws ecs run-task \
  --cluster myteacher-backend-cluster \
  --task-definition myteacher-backend \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNET_1],securityGroups=[$ECS_SG],assignPublicIp=DISABLED}" \
  --overrides '{"containerOverrides":[{"name":"myteacher-backend","command":["python","-m","app.scripts.seed_data"]}]}'
```

### Step 10.3: Configure Monitoring
```bash
# Enable CloudWatch Container Insights
aws ecs put-account-setting-default \
  --name containerInsights \
  --value enabled

# Create CloudWatch Dashboard
aws cloudwatch put-dashboard \
  --dashboard-name myteacher-prod \
  --dashboard-body file://dashboard.json

# See dashboard.json in repository
```

---

## Phase 11: CI/CD Setup (Optional but Recommended) (30 minutes)

### Step 11.1: Create CodePipeline
```bash
# Create S3 bucket for artifacts
aws s3 mb s3://myteacher-pipeline-artifacts

# Create CodePipeline (via Console or CLI)
# Source: GitHub (connect via OAuth)
# Build: CodeBuild (see buildspec.yml)
# Deploy: ECS Rolling Update
```

### Step 11.2: CodeBuild Project
```yaml
# buildspec.yml (in repository)
version: 0.2
phases:
  pre_build:
    commands:
      - echo Logging in to ECR...
      - aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REPO
  build:
    commands:
      - cd backend
      - docker build -t myteacher-backend:$CODEBUILD_RESOLVED_SOURCE_VERSION .
      - docker tag myteacher-backend:$CODEBUILD_RESOLVED_SOURCE_VERSION $ECR_REPO:latest
  post_build:
    commands:
      - docker push $ECR_REPO:latest
      - printf '[{"name":"myteacher-backend","imageUri":"%s"}]' $ECR_REPO:latest > imagedefinitions.json
artifacts:
  files: imagedefinitions.json
```

---

## Phase 12: Post-Deployment Validation (15 minutes)

### Step 12.1: Health Checks
```bash
# Test ALB health
curl https://api.myteacher.ai/health
# Expected: {"status": "healthy"}

# Test frontend
curl https://myteacher.ai
# Should return HTML

# Test API endpoints
curl -X POST https://api.myteacher.ai/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'
```

### Step 12.2: Monitoring
```bash
# Check ECS service status
aws ecs describe-services \
  --cluster myteacher-backend-cluster \
  --services myteacher-backend-service

# Check ALB targets
aws elbv2 describe-target-health --target-group-arn $TG_ARN

# View logs
aws logs tail /aws/ecs/myteacher-backend --follow
```

### Step 12.3: Load Testing
```bash
# Install k6 (https://k6.io)
brew install k6  # macOS

# Run load test
k6 run load-test.js

# load-test.js
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 100 },   // Ramp up
    { duration: '5m', target: 100 },   // Sustain
    { duration: '1m', target: 0 },     // Ramp down
  ],
};

export default function() {
  let res = http.get('https://myteacher.ai');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
```

---

## 🎉 Deployment Complete!

Your application is now live at:
- **Frontend**: https://myteacher.ai
- **API**: https://api.myteacher.ai

### Next Steps:
1. [ ] Setup monitoring alerts (CloudWatch Alarms → SNS → Email/Slack)
2. [ ] Configure backup schedules (MongoDB Atlas automated)
3. [ ] Setup WAF rules (SQL injection, XSS protection)
4. [ ] Enable CloudTrail for audit logging
5. [ ] Create runbook for incident response
6. [ ] Schedule cost review meeting (weekly)
7. [ ] Plan capacity for growth (monthly)

---

## 🆘 Troubleshooting

### Issue: ECS tasks failing health checks
```bash
# Check logs
aws logs tail /aws/ecs/myteacher-backend --follow

# Common causes:
# - Wrong secret ARNs in task definition
# - Security group blocking 8000
# - MongoDB connection refused (check IP whitelist)
# - Anthropic API key invalid
```

### Issue: ALB returning 503
```bash
# Check target health
aws elbv2 describe-target-health --target-group-arn $TG_ARN

# If unhealthy:
# - Check ECS task status
# - Check security groups (ALB → ECS on port 8000)
# - Check health check path (/health)
```

### Issue: CloudFront not caching
```bash
# Invalidate cache
aws cloudfront create-invalidation \
  --distribution-id $CF_DISTRIBUTION_ID \
  --paths "/*"

# Check cache behavior settings
aws cloudfront get-distribution-config --id $CF_DISTRIBUTION_ID
```

---

## 💰 Cost Monitoring

```bash
# View current month costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d "1 day ago" '+%Y-%m-01'),End=$(date -u '+%Y-%m-%d') \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE

# Set up billing alerts
aws cloudwatch put-metric-alarm \
  --alarm-name myteacher-high-cost \
  --alarm-description "Alert when monthly cost > $500" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 500 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=Currency,Value=USD
```

---

## 📞 Support

- **AWS Support**: https://console.aws.amazon.com/support
- **MongoDB Atlas Support**: https://support.mongodb.com
- **Anthropic Support**: support@anthropic.com

---

**Deployment Guide Version:** 1.0
**Last Updated:** December 9, 2025
**Maintainer:** Yohans Bekele
**Review Date:** March 1, 2026

🚀 **Happy Deploying!**
