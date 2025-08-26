# Oracle Cloud Deployment Guide

This guide provides instructions for deploying the AI Note System to Oracle Cloud Infrastructure (OCI).

## Prerequisites

Before you begin, ensure you have the following:

1. An Oracle Cloud account with access to the following services:
   - Oracle Compute Instance
   - Oracle Autonomous Database (ATP or MySQL HeatWave)
   - Oracle Object Storage
   - Oracle Email Delivery

2. The following tools installed on your local machine:
   - Git
   - Docker and Docker Compose
   - Oracle Cloud Infrastructure CLI (OCI CLI)

3. GitHub repository access with GitHub Actions enabled

## Setup Steps

### 1. Oracle Autonomous Database Setup

1. Create an Autonomous Database instance (ATP or MySQL HeatWave)
   - Log in to the Oracle Cloud Console
   - Navigate to Oracle Database > Autonomous Database
   - Click "Create Autonomous Database"
   - Fill in the required details:
     - Display name: `ai-note-system-db`
     - Database name: `ainotesystemdb`
     - Workload type: "Transaction Processing"
     - Deployment type: "Shared Infrastructure"
     - Choose CPU and storage configuration
     - Set admin password
   - Click "Create Autonomous Database"

2. Download the database wallet
   - From the Autonomous Database details page, click "DB Connection"
   - Click "Download Wallet"
   - Set a wallet password and download the wallet ZIP file

3. Create database schema
   - Connect to the database using SQL Developer or another SQL client
   - Run the schema creation script from `database/oracle_schema.sql`

### 2. Oracle Object Storage Setup

1. Create a bucket for file storage
   - Navigate to Storage > Buckets
   - Click "Create Bucket"
   - Name the bucket `ai-note-system-files`
   - Set visibility to "Private"
   - Click "Create"

2. Note your Object Storage namespace and region
   - The namespace is displayed at the top of the Buckets page
   - The region is displayed in the top-right corner of the console

### 3. Oracle Email Delivery Setup

1. Configure Email Delivery
   - Navigate to Email Delivery
   - Click "Create Email Domain"
   - Follow the steps to verify domain ownership
   - Create and verify a sender address

2. Note your Email Delivery endpoint and sender address

### 4. Oracle Compute Instance Setup

1. Create a Compute Instance
   - Navigate to Compute > Instances
   - Click "Create Instance"
   - Name the instance `ai-note-system-server`
   - Choose an Ubuntu image
   - Select shape (recommended: VM.Standard.E4.Flex with 2 OCPUs and 16 GB memory)
   - Configure networking (ensure ports 80, 443, and 22 are open)
   - Add SSH keys for access
   - Click "Create"

2. Connect to the instance via SSH
   ```bash
   ssh -i /path/to/private_key ubuntu@<instance_public_ip>
   ```

3. Install Docker and Docker Compose
   ```bash
   # Update package lists
   sudo apt update
   
   # Install prerequisites
   sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
   
   # Add Docker's official GPG key
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   
   # Add Docker repository
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   
   # Install Docker
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io
   
   # Add current user to docker group
   sudo usermod -aG docker ${USER}
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   
   # Verify installation
   docker --version
   docker-compose --version
   ```

4. Create a directory for the wallet files
   ```bash
   mkdir -p ~/wallet
   ```

5. Upload the wallet files to the instance
   ```bash
   # From your local machine
   scp -i /path/to/private_key /path/to/wallet.zip ubuntu@<instance_public_ip>:~/wallet/
   
   # On the instance
   cd ~/wallet
   unzip wallet.zip
   rm wallet.zip
   ```

### 5. GitHub Repository Setup

1. Configure GitHub Secrets
   - Navigate to your GitHub repository
   - Go to Settings > Secrets and variables > Actions
   - Add the following secrets:
     - `OCI_CONFIG`: Contents of your OCI CLI config file
     - `OCI_KEY`: Contents of your OCI API private key
     - `PRODUCTION_COMPUTE_INSTANCE_OCID`: OCID of your production compute instance
     - `STAGING_COMPUTE_INSTANCE_OCID`: OCID of your staging compute instance
     - `ORACLE_CONNECTION_STRING`: Connection string for your Autonomous Database
     - `ORACLE_USERNAME`: Database username
     - `ORACLE_PASSWORD`: Database password
     - `ORACLE_WALLET_PASSWORD`: Password for the wallet
     - `OBJECT_STORAGE_NAMESPACE`: Your Object Storage namespace
     - `OBJECT_STORAGE_BUCKET`: Name of your Object Storage bucket
     - `OBJECT_STORAGE_REGION`: Your Oracle Cloud region
     - `EMAIL_SENDER`: Your verified sender email address
     - `EMAIL_DELIVERY_ENDPOINT`: Your Email Delivery endpoint
     - `OCI_COMPARTMENT_ID`: OCID of your compartment
     - `FRONTEND_URL`: URL of your frontend application

2. Enable GitHub Actions
   - Navigate to your GitHub repository
   - Go to Actions tab
   - Click "I understand my workflows, go ahead and enable them"

## Deployment

### Manual Deployment

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/ai-note-system.git
   cd ai-note-system
   ```

2. Create a `.env` file with your environment variables
   ```bash
   cat > .env << EOF
   ORACLE_CONNECTION_STRING=your_connection_string
   ORACLE_USERNAME=your_username
   ORACLE_PASSWORD=your_password
   ORACLE_WALLET_PASSWORD=your_wallet_password
   OBJECT_STORAGE_NAMESPACE=your_namespace
   OBJECT_STORAGE_BUCKET=your_bucket
   OBJECT_STORAGE_REGION=your_region
   EMAIL_SENDER=your_sender_email
   EMAIL_DELIVERY_ENDPOINT=your_email_endpoint
   OCI_COMPARTMENT_ID=your_compartment_id
   FRONTEND_URL=your_frontend_url
   EOF
   ```

3. Build and start the containers
   ```bash
   docker-compose up -d
   ```

4. Verify the deployment
   ```bash
   curl http://localhost/health
   ```

### Automated Deployment

The repository is configured with GitHub Actions for CI/CD. When you push to the `main` or `staging` branches, the workflow will:

1. Run tests
2. Build Docker images
3. Push images to GitHub Container Registry
4. Deploy to the appropriate environment (production for `main`, staging for `staging`)

To trigger a deployment, simply push to the appropriate branch:

```bash
# For staging
git checkout staging
git push origin staging

# For production
git checkout main
git push origin main
```

## Monitoring and Maintenance

### Viewing Logs

```bash
# View logs for all containers
docker-compose logs

# View logs for a specific service
docker-compose logs backend
docker-compose logs frontend
```

### Updating the Application

1. Pull the latest changes
   ```bash
   git pull
   ```

2. Rebuild and restart the containers
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### Backing Up the Database

1. Navigate to the Autonomous Database details page
2. Click "Database Actions"
3. Go to "Data Tools" > "Data Export"
4. Follow the steps to export your data

## Troubleshooting

### Common Issues

1. **Connection issues with Oracle Autonomous Database**
   - Verify that the wallet files are correctly placed in the `wallet` directory
   - Check that the connection string, username, and password are correct
   - Ensure the database is up and running

2. **Docker container fails to start**
   - Check the container logs: `docker-compose logs`
   - Verify that all environment variables are correctly set
   - Ensure that the required ports are not in use by other applications

3. **GitHub Actions workflow fails**
   - Check the workflow logs in the GitHub Actions tab
   - Verify that all secrets are correctly set
   - Ensure that the compute instance is accessible

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the project's GitHub Issues page
2. Contact the development team
3. Refer to the Oracle Cloud documentation for service-specific issues