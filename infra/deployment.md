# Jinder Deployment Guide

## Architecture
- **Frontend**: Angular SPA hosted on AWS S3 + CloudFront.
- **Backend**: FastAPI app hosted on AWS ECS (Fargate) behind an Application Load Balancer (ALB).
- **Database**: PostgreSQL on AWS RDS.
- **Storage**: AWS S3 for Resume files.
- **Workers**: Background tasks run within the FastAPI container (BackgroundTasks) or separate ECS services for heavy lifting.

## Prerequisites
- AWS Account
- Docker
- AWS CLI
- Terraform (optional but recommended)

## Steps

### 1. Database (RDS)
1. Launch a PostgreSQL instance in RDS.
2. Create a database `jinder`.
3. Note the endpoint, username, and password.

### 2. Backend (ECS Fargate)
1. Dockerize the backend:
   ```dockerfile
   FROM python:3.10
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
   ```
2. Push image to ECR.
3. Create an ECS Task Definition with environment variables:
   - `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
   - `SECRET_KEY`
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
4. Create an ECS Service and ALB.

### 3. Frontend (S3 + CloudFront)
1. Build the Angular app: `ng build --configuration production`.
2. Upload `dist/frontend` to an S3 bucket.
3. Configure S3 for static website hosting.
4. Create a CloudFront distribution pointing to the S3 bucket.

### 4. Domain & SSL
1. Use Route53 for DNS.
2. Use ACM for SSL certificates (attach to ALB and CloudFront).

## Scaling
- **Backend**: Configure Auto Scaling based on CPU/Memory.
- **Database**: Use Read Replicas if read heavy.
- **Workers**: Move automation to SQS + Lambda or separate ECS workers if scale increases.
