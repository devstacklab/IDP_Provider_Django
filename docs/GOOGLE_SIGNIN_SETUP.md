# Google Sign-In Setup Guide

This guide will walk you through setting up Google Sign-In (OAuth 2.0) for your SAML IdP provider.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Enter a project name (e.g., "SAML IdP Provider")
4. Click **Create**

## Step 2: Enable Google+ API

1. In the Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for **"Google+ API"**
3. Click on it and press **Enable**

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** (or **Internal** if you have a Google Workspace account)
3. Fill in the required fields:
   - **App name**: SAML IdP Provider
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Click **Save and Continue**
5. Add scopes (optional, defaults are fine)
6. Click **Save and Continue**
7. Add test users (optional for now)
8. Click **Save and Continue**

## Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Select **Application type**: **Web application**
4. Enter a name (e.g., "SAML IdP Web Client")
5. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8000/accounts/google/login/callback/
   ```
6. Under **Authorized JavaScript origins**, add:
   ```
   http://localhost:8000
   ```
7. Click **Create**

## Step 5: Copy Your Credentials

After creating the OAuth client, Google will display:
- **Client ID**: Something like `123456789-xxxxx.apps.googleusercontent.com`
- **Client Secret**: A long random string

**Important:** Download or copy these credentials immediately. You won't be able to see the client secret again!

## Step 6: Configure Your Django App

1. Open your `.env` file (or create one if it doesn't exist)
2. Add the following lines:

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

Replace `your-client-id` and `your-client-secret` with the actual values from Google.

## Step 7: Run Migrations

```bash
uv run python manage.py migrate
```

## Step 8: Test Google Sign-In

1. Start the development server:
   ```bash
   uv run python manage.py runserver
   ```

2. Go to: http://localhost:8000/accounts/login/

3. You should see a **"Sign in with Google"** button above the email/password form.

4. Click it and authenticate with your Google account.

5. After successful authentication, you'll be redirected back to the IdP.

## Step 9: (Optional) Add More Test Users

If you want to test with multiple Google accounts:

1. Go to **APIs & Services** → **OAuth consent screen**
2. Scroll down to **Test users**
3. Click **+ Add Users**
4. Enter the email addresses you want to test with

## Troubleshooting

### Error: "redirect_uri_mismatch"

This means the redirect URI in your Google Cloud Console doesn't match what Django is using.

**Fix:**
1. Go to Google Cloud Console → Credentials
2. Edit your OAuth client
3. Ensure the **Authorized redirect URI** is exactly:
   ```
   http://localhost:8000/accounts/google/login/callback/
   ```

### Error: "Access blocked: This app's request is invalid"

This usually means the OAuth consent screen is not configured.

**Fix:**
1. Complete the OAuth consent screen setup in Google Cloud Console
2. Make sure you've added test users if the app is in "Testing" mode

### Google Sign-In button not showing

**Check:**
1. `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in `.env`
2. You've run `uv run python manage.py migrate`
3. The `django.contrib.sites` app is in `INSTALLED_APPS`
4. `SITE_ID = 1` is in settings

### User not created after Google login

**Check:**
1. `SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True` is in settings
2. The email from Google is unique (not already used by another provider)

## Production Configuration

For production deployment:

1. **Update redirect URI** in Google Cloud Console:
   ```
   https://yourdomain.com/accounts/google/login/callback/
   ```

2. **Update `.env`** with production domain:
   ```env
   GOOGLE_CLIENT_ID=your-production-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-production-client-secret
   ```

3. **Change OAuth consent screen** from "Testing" to "In Production"

4. **Verify your domain** with Google Search Console if required

## Multiple Social Providers

You can add more social providers (GitHub, Facebook, etc.) alongside Google:

1. Add provider to `SOCIALACCOUNT_PROVIDERS` in settings
2. Create OAuth app in the provider's developer console
3. Add credentials to `.env`
4. Allauth will automatically show buttons for all configured providers

## SAML + Google Sign-In Flow

Here's how it works together:

1. **User accesses SP** (Service Provider)
2. **SP redirects to IdP** (your Django app) with SAML request
3. **User logs in with Google** (or email/password)
4. **IdP authenticates user** and creates session
5. **IdP sends SAML response** back to SP with user attributes
6. **SP grants access** to the user

The Google authentication is transparent to the SAML SP - they only see the SAML assertion!

## API Reference

### Callback URL
```
http://localhost:8000/accounts/google/login/callback/
```

### Manual Google Login URL
```
http://localhost:8000/accounts/google/login/
```

### Logout
```
http://localhost:8000/accounts/logout/
```

## Next Steps

- ✅ Test Google Sign-In locally
- ✅ Add more test users
- ✅ Configure production credentials
- ✅ Set up multiple social providers
- ✅ Customize attribute mapping for SAML assertions
