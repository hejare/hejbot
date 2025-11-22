# Hejbot AWS Deployment Guide

This guide covers deploying Hejbot to AWS using GitHub Actions for CI/CD.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      GitHub Actions                         │
│  (Builds Docker image and pushes to ECR on push to main)   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─ OIDC Authentication
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                         AWS Cloud                            │
│                                                              │
│  ┌────────────┐      ┌──────────────┐                      │
│  │    ECR     │─────▶│ ECS Fargate  │                      │
│  │ Repository │      │   Service    │                      │
│  └────────────┘      └──────┬───────┘                      │
│                             │                               │
│                             │ Connects to                   │
│                             ▼                               │
│                      ┌──────────────┐                      │
│                      │ PostgreSQL   │                      │
│                      │     RDS      │                      │
│                      └──────────────┘                      │
│                                                              │
│  Secrets stored in SSM Parameter Store                      │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **AWS Account**: Access to the playground account
2. **AWS CLI**: Configured with `hejare-terraform` profile
3. **Node.js & npm**: For CDKTF deployment
4. **Slack App**: Bot Token and Signing Secret from https://api.slack.com/apps

## Step 1: Deploy Infrastructure

Navigate to the infrastructure directory and deploy:

```bash
cd /Users/kritt/dev/aws-infra/hejare/hejbot

# Install dependencies
npm install

# Generate Terraform configuration
npm run synth

# Deploy to AWS (this will take ~15 minutes due to RDS creation)
npm run deploy
```

After deployment completes, note the outputs:
- `ecr_repository_url`: ECR repository URL
- `github_deployment_role_arn`: IAM role ARN for GitHub Actions
- `db_endpoint`: PostgreSQL endpoint
- `ecs_cluster_name`: ECS cluster name

## Step 2: Configure Slack Credentials

Create SSM parameters for Slack credentials:

```bash
# Set your Slack Bot Token (starts with xoxb-)
aws ssm put-parameter \
    --name "/hejbot/slack_bot_token" \
    --value "xoxb-your-actual-token-here" \
    --type "SecureString" \
    --profile hejare-terraform \
    --region eu-west-1

# Set your Slack Signing Secret
aws ssm put-parameter \
    --name "/hejbot/slack_signing_secret" \
    --value "your-signing-secret-here" \
    --type "SecureString" \
    --profile hejare-terraform \
    --region eu-west-1
```

The RDS password is auto-generated and stored at `/hejbot/rds_password`.

## Step 3: Configure GitHub Repository

### Add AWS Role ARN to GitHub Secrets

1. Go to your GitHub repository: https://github.com/hejare/hejbot
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `AWS_ROLE_ARN`
5. Value: The `github_deployment_role_arn` from the infrastructure deployment output

### Update GitHub OIDC Condition (if needed)

The infrastructure assumes your GitHub repository is at `hejare/hejbot`. If it's different, update the role condition in `/Users/kritt/dev/aws-infra/hejare/hejbot/main.ts` line 401:

```typescript
"token.actions.githubusercontent.com:sub": "repo:YOUR_ORG/YOUR_REPO:*",
```

Then redeploy the infrastructure.

## Step 4: Deploy Application

Once the infrastructure is ready and GitHub is configured, simply push to the main branch:

```bash
cd /Users/kritt/dev/hejbot
git add .
git commit -m "Configure AWS deployment"
git push origin main
```

GitHub Actions will automatically:
1. Build the Docker image
2. Push it to ECR
3. Update the ECS service
4. Wait for the deployment to stabilize

Monitor the deployment at: https://github.com/hejare/hejbot/actions

## Step 5: Configure Slack App (HTTP Mode)

Since the bot runs in HTTP mode (not Socket Mode), you need to configure Slack to send events to your endpoint.

**Important Note**: The current configuration uses ECS tasks with public IPs but no load balancer. For production HTTP mode, you would need to:

1. **Option A - Use Socket Mode** (Recommended for now):
   - Update the ECS task environment variable `SOCKET_MODE` to `True`
   - Add `SLACK_APP_TOKEN` to SSM Parameter Store
   - Redeploy

2. **Option B - Add Application Load Balancer**:
   - Modify infrastructure to add ALB
   - Configure Slack Event Subscriptions with ALB URL
   - More complex but production-ready

**For now, I recommend Socket Mode**:

```bash
# Add App Token to SSM
aws ssm put-parameter \
    --name "/hejbot/slack_app_token" \
    --value "xapp-your-app-token-here" \
    --type "SecureString" \
    --profile hejare-terraform \
    --region eu-west-1

# Update the task definition to use Socket Mode
# Edit main.ts line 333-335, change SOCKET_MODE to "True"
# Add SLACK_APP_TOKEN to the secrets section (lines 341-354)
```

## Monitoring

### View Logs

```bash
# Stream logs from CloudWatch
aws logs tail /aws/ecs/hejbot --follow \
    --profile hejare-terraform \
    --region eu-west-1
```

### Check ECS Service Status

```bash
aws ecs describe-services \
    --cluster hejbot-cluster \
    --services hejbot-service \
    --profile hejare-terraform \
    --region eu-west-1
```

### Check Running Tasks

```bash
aws ecs list-tasks \
    --cluster hejbot-cluster \
    --service-name hejbot-service \
    --profile hejare-terraform \
    --region eu-west-1
```

## Database Access

The PostgreSQL database is in a private subnet and not publicly accessible. To access it:

### Option 1: Use AWS Systems Manager Session Manager

```bash
# Create a session to an ECS task
aws ecs execute-command \
    --cluster hejbot-cluster \
    --task <task-id> \
    --container hejbot \
    --interactive \
    --command "/bin/bash" \
    --profile hejare-terraform \
    --region eu-west-1
```

### Option 2: Port Forwarding via Bastion

(Would require creating a bastion host in public subnet)

## Cost Estimate

Monthly costs (approximate):

- **RDS db.t4g.micro**: ~$15/month (free tier: $0 for 12 months)
- **ECS Fargate** (256 CPU / 512 MB): ~$7/month
- **ECR Storage**: ~$0.10/month (for a few images)
- **Data Transfer**: Varies based on Slack API usage
- **Total**: ~$22/month (or ~$7 on free tier)

## Updating the Application

Simply push to the main branch:

```bash
git push origin main
```

GitHub Actions will automatically rebuild and deploy.

## Troubleshooting

### Task fails to start

Check CloudWatch logs:
```bash
aws logs tail /aws/ecs/hejbot --since 1h \
    --profile hejare-terraform \
    --region eu-west-1
```

Common issues:
- Missing SSM parameters (check all secrets are created)
- Database connection issues (check security groups)
- Invalid Slack credentials

### Database connection errors

Ensure:
1. RDS is in running state
2. Security group allows ECS → RDS on port 5432
3. Database credentials are correct in SSM

### GitHub Actions deployment fails

Check:
1. `AWS_ROLE_ARN` secret is set correctly
2. OIDC provider exists in AWS
3. IAM role trust relationship includes your repo

## Cleanup

To destroy all resources:

```bash
cd /Users/kritt/dev/aws-infra/hejare/hejbot
npm run destroy
```

Manually delete SSM parameters:

```bash
aws ssm delete-parameter --name "/hejbot/slack_bot_token" --profile hejare-terraform --region eu-west-1
aws ssm delete-parameter --name "/hejbot/slack_signing_secret" --profile hejare-terraform --region eu-west-1
aws ssm delete-parameter --name "/hejbot/slack_app_token" --profile hejare-terraform --region eu-west-1
aws ssm delete-parameter --name "/hejbot/rds_password" --profile hejare-terraform --region eu-west-1
```

## Next Steps

- [ ] Configure Socket Mode or add ALB for HTTP mode
- [ ] Set up CloudWatch alarms for task failures
- [ ] Configure RDS automated backups
- [ ] Add custom domain (if needed)
- [ ] Set up proper CI/CD environments (staging, production)
