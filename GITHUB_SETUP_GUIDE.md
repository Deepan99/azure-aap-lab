# GitHub Repository Security Setup Guide

This guide walks you through the manual GitHub configuration steps to complete the security setup for your repository.

## Prerequisites

- Repository owner or admin access
- GitHub account with appropriate permissions

## Step 1: Enable Branch Protection Rules

### Why This Matters
Branch protection rules prevent direct pushes to main branch and ensure all security checks pass before merging.

### How to Configure

1. **Navigate to Repository Settings**
   - Go to your repository on GitHub
   - Click **Settings** tab
   - Click **Branches** in the left sidebar

2. **Add Branch Protection Rule**
   - Click **Add rule**
   - Branch name pattern: `main`
   - Configure the following settings:

   **✅ Require pull request before merging**
   - Require approvals: **1**
   - Dismiss stale PR approvals when new commits are pushed: **Check**
   - Require review from CODEOWNERS: **Optional**

   **✅ Require status checks to pass before merging**
   - Require branches to be up to date before merging: **Check**
   - Select required status checks:
     - `Validate Terraform Configuration`
     - `Validate Ansible Playbooks`
     - `Security Scanning`
     - `CodeQL Analysis`
     - `Dependency Scanning`
     - `Integration Tests`

   **✅ Do not allow bypassing the above settings**
   - Check this box to enforce rules for all users

   **✅ Require signed commits**
   - Optional but recommended for enhanced security

3. **Save Changes**
   - Click **Create** or **Save changes**

### Verification
Try to push directly to main branch - it should be rejected and require a pull request.

## Step 2: Configure Required Status Checks

### Why This Matters
Ensures all security validations pass before code can be merged.

### How to Configure

1. **In Branch Protection Settings**
   - Under "Require status checks to pass before merging"
   - Make sure these are checked:
     - `Validate Terraform Configuration`
     - `Validate Ansible Playbooks`
     - `Security Scanning`
     - `CodeQL Analysis`
     - `Dependency Scanning`
     - `Integration Tests`

2. **Require branches to be up to date**
   - This ensures the branch is based on the latest main

### Verification
Create a test PR and verify all checks must pass before merge button becomes available.

## Step 3: Review Repository Access Control

### Why This Matters
Ensures only authorized users have appropriate access levels.

### How to Configure

1. **Navigate to Collaborators & Teams**
   - Go to repository **Settings**
   - Click **Collaborators & teams** in the left sidebar

2. **Review Current Access**
   - **People** tab: Review individual collaborators
   - **Teams** tab: Review team access (if using GitHub Teams)

3. **Configure Appropriate Permissions**
   - **Admin**: Full control (you and trusted maintainers)
   - **Maintain**: Can manage issues, PRs, but not settings
   - **Write**: Can push to non-protected branches
   - **Read**: Can clone and view, no write access

4. **Best Practices**
   - Limit admin access to minimum number of people
   - Use teams for group-based access management
   - Regularly review and remove inactive collaborators
   - Enable two-factor authentication requirement

### Verification
Ensure only intended users have access and permissions are appropriate.

## Step 4: Optional - Configure Commit Signing

### Why This Matters
Verifies the identity of committers and ensures code integrity.

### How to Configure

1. **Generate GPG Key** (if you don't have one)
   ```bash
   gpg --full-generate-key
   ```

2. **Add GPG Key to GitHub**
   - Go to **Settings** → **SSH and GPG keys**
   - Click **New GPG key**
   - Paste your public key
   - Click **Add GPG key**

3. **Configure Git to Use GPG**
   ```bash
   git config --global user.signingkey YOUR_GPG_KEY_ID
   git config --global commit.gpgsign true
   ```

4. **Test Commit Signing**
   ```bash
   git commit -S -m "Test signed commit"
   ```

### Verification
Check your commits on GitHub - they should show a "Verified" badge.

## Step 5: Optional - Enable GitHub Advanced Security

### Why This Matters
Provides advanced security features like secret scanning and enhanced dependency analysis.

### How to Configure

1. **Check Eligibility**
   - Advanced Security requires GitHub Enterprise or specific repository types
   - Check your GitHub plan for availability

2. **Enable Advanced Security**
   - Go to repository **Settings**
   - Click **Security & analysis** in the left sidebar
   - Enable features:
     - **Secret scanning**
     - **Dependency graph**
     - **Code scanning alerts**

### Verification
Check Security tab for new security alerts and scanning results.

## Step 6: Configure Security Policies

### Why This Matters
Automates security enforcement and provides clear guidelines.

### How to Configure

1. **Security Policies**
   - Go to repository **Settings**
   - Click **Policies** in the left sidebar
   - Configure:
     - **Branch policies** (already covered in Step 1)
     - **Tag policies** (if using Git tags)
     - **Interaction limits** (for temporary restrictions)

2. **Security Advisories**
   - Go to repository **Security** tab
   - Click **Security advisories**
   - Set up advisory notifications

### Verification
Test policy enforcement by attempting restricted actions.

## Step 7: Configure Notifications

### Why This Matters
Ensures you're notified of security events and issues.

### How to Configure

1. **Notification Settings**
   - Go to **Settings** → **Notifications**
   - Configure:
     - **Watch** repositories you want notifications for
     - **Customize** notification types (security alerts, vulnerability alerts)

2. **Repository-Specific Notifications**
   - Go to repository **Settings** → **Notifications**
   - Configure:
     - **Security alerts**: Enabled
     - **Vulnerability alerts**: Enabled
     - **Dependabot alerts**: Enabled

### Verification
Trigger a security event and verify notification delivery.

## Verification Checklist

After completing all steps, verify:

- [ ] Branch protection rules are active for main branch
- [ ] Required status checks are enforced
- [ ] Cannot push directly to main branch
- [ ] PRs require approval before merging
- [ ] All security checks must pass before merge
- [ ] Repository access is appropriately restricted
- [ ] Security notifications are configured
- [ ] (Optional) Commit signing is working
- [ ] (Optional) Advanced Security features are enabled

## Troubleshooting

### Branch Protection Not Working
- Check that the rule is enabled for the correct branch
- Verify you're not bypassing rules (admin bypass)
- Check if rules are being overridden by organization settings

### Status Checks Not Required
- Ensure the status check names match exactly
- Check that the workflow is running successfully
- Verify the check names in the Actions tab

### Access Control Issues
- Verify user permissions in Collaborators section
- Check if organization policies override repository settings
- Ensure two-factor authentication is enabled if required

### Commit Signing Issues
- Verify GPG key is properly added to GitHub
- Check Git configuration for GPG signing
- Ensure email addresses match between Git and GitHub

## Security Best Practices

1. **Regular Reviews**
   - Review branch protection rules quarterly
   - Audit repository access monthly
   - Review security policies regularly

2. **Monitoring**
   - Monitor security alerts in Security tab
   - Review Dependabot PRs promptly
   - Check Actions workflow failures

3. **Documentation**
   - Document security decisions
   - Keep SECURITY.md updated
   - Maintain security runbooks

4. **Training**
   - Train contributors on security practices
   - Provide security guidelines
- Conduct regular security awareness sessions

## Additional Resources

- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/managing-branch-protection-rules)
- [GitHub Security Settings](https://docs.github.com/en/code-security/getting-started/securing-your-repository)
- [GPG Commit Signing](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)
- [GitHub Advanced Security](https://docs.github.com/en/code-security)

## Support

If you encounter issues:
1. Check GitHub documentation
2. Review GitHub Status page
3. Contact GitHub Support (if Enterprise)
4. Review SECURITY.md in this repository

---

**Last Updated**: 2026-08-14  
**Repository**: https://github.com/Deepan99/azure-aap-lab