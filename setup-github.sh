#!/bin/bash

# GitHub Repository Setup Script for Prompt Tune
# Run this script to create and push to your GitHub repository

echo "🚀 Setting up Prompt Tune GitHub Repository..."

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "📥 Install it with: brew install gh"
    echo "🔗 Or visit: https://cli.github.com/"
    exit 1
fi

# Check if user is logged in to GitHub CLI
if ! gh auth status &> /dev/null; then
    echo "🔐 Please login to GitHub CLI first:"
    echo "   gh auth login"
    exit 1
fi

# Create the repository on GitHub
echo "📝 Creating repository on GitHub..."
gh repo create prompt-tune \
    --public \
    --description "Enterprise-grade AI prompt optimization platform with real-time analytics, team collaboration, and production infrastructure. Built in 2 days!" \
    --homepage "https://github.com/justwant2code/prompt-tune" \
    --add-readme=false

# Add GitHub remote
echo "🔗 Adding GitHub remote..."
git remote add origin https://github.com/justwant2code/prompt-tune.git

# Push to GitHub
echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "🎉 SUCCESS! Your repository is now live at:"
echo "🔗 https://github.com/justwant2code/prompt-tune"
echo ""
echo "📋 Next steps:"
echo "1. Visit your repository on GitHub"
echo "2. Add repository topics/tags for discoverability"
echo "3. Set up GitHub Actions for CI/CD (optional)"
echo "4. Configure branch protection rules (optional)"
echo ""
echo "🚀 Ready to deploy to production!"
