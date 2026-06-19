# 👥 User Management Guide

Complete guide for creating and managing users in RestoCost.

---

## 📋 Table of Contents

- [User Roles](#user-roles)
- [Creating the Super Admin](#creating-the-super-admin)
- [Creating Additional Users](#creating-additional-users)
- [User Workflows](#user-workflows)
- [API Endpoints](#api-endpoints)
- [Security Best Practices](#security-best-practices)

---

## 🎭 User Roles

RestoCost has three distinct user roles:

| Role | Description | Permissions |
|------|-------------|-------------|
| **admin** | Super administrator | Full system access. Can create owners and other admins. |
| **owner** | Restaurant owner | Can create staff for their restaurant. Manage restaurant data. |
| **staff** | Restaurant employee | Use the application. No admin permissions. |

### Role Hierarchy

```
admin (Super Admin)
  └─→ Can create: admin, owner, staff

owner (Restaurant Owner)
  └─→ Can create: staff

staff (Employee)
  └─→ Can create: nothing
```

---

## 🔐 Creating the Super Admin

The **first step** when setting up RestoCost is to create a super administrator.

### Prerequisites

- Server access (SSH or local terminal)
- Python virtual environment activated
- Database configured

### Method 1: Interactive (Recommended)

```bash
cd backend
python create_admin.py
```

You will be prompted:

```
Admin email: admin@restocost.com
Admin password: ********
Confirm password: ********

Creating super admin user...
✅ Super admin user created successfully!
   Email: admin@restocost.com
   Role: admin
   ID: 1
```

### Method 2: Command Line Arguments

```bash
python create_admin.py --email admin@restocost.com --password YourSecurePassword123
```

⚠️ **Warning:** This method shows the password in shell history. Only use in secure environments.

### Method 3: Docker

If running in Docker:

```bash
docker exec -it restocost-backend python create_admin.py
```

---

## 👤 Creating Additional Users

Once the super admin is created, all other users are created via the API.

### Creating an Owner (Admin Only)

**Endpoint:** `POST /api/admin/users`

**Request:**
```bash
curl -X POST 'http://localhost:8000/api/admin/users' \
  -H 'Authorization: Bearer YOUR_ADMIN_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "owner@restaurant.com",
    "role": "owner"
  }'
```

**Response:**
```json
{
  "id": 2,
  "email": "owner@restaurant.com",
  "role": "owner",
  "temporary_password": "Abc123XyZ456",
  "must_change_password": true
}
```

**Important:**
- Save the `temporary_password` - it's only returned once!
- Share it securely with the new user (in person, encrypted message, etc.)

---

### Creating Staff (Owner or Admin)

**Endpoint:** `POST /api/admin/users`

**Request:**
```bash
curl -X POST 'http://localhost:8000/api/admin/users' \
  -H 'Authorization: Bearer YOUR_OWNER_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "chef@restaurant.com",
    "role": "staff"
  }'
```

**Response:**
```json
{
  "id": 3,
  "email": "chef@restaurant.com",
  "role": "staff",
  "temporary_password": "Def789UvW012",
  "must_change_password": true
}
```

---

## 🔄 User Workflows

### Complete User Onboarding Flow

```mermaid
graph TD
    A[Admin creates user] --> B[User receives email + temporary password]
    B --> C[User logs in with temporary password]
    C --> D[User changes password]
    D --> E[User can access application]
```

### 1️⃣ Admin Creates User

Admin uses the API or future frontend interface:

```bash
POST /api/admin/users
{
  "email": "newuser@example.com",
  "role": "staff"
}

# Returns temporary_password
```

---

### 2️⃣ User Receives Credentials

Admin shares credentials with the new user **securely**:

✅ **Good methods:**
- In person
- Encrypted messaging (Signal, WhatsApp)
- Password manager shared vault
- Secure company communication tool

❌ **Bad methods:**
- Unencrypted email
- SMS (can be intercepted)
- Slack/Teams public channels
- Written on paper left on desk

---

### 3️⃣ User First Login

**Endpoint:** `POST /api/auth/login`

```bash
curl -X POST 'http://localhost:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "newuser@example.com",
    "password": "Abc123XyZ456"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Important:** User should immediately change their password.

---

### 4️⃣ User Changes Password

**Endpoint:** `POST /api/auth/change-password`

```bash
curl -X POST 'http://localhost:8000/api/auth/change-password' \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "current_password": "Abc123XyZ456",
    "new_password": "MySecurePassword789!"
  }'
```

**Response:**
```json
{
  "id": 3,
  "email": "newuser@example.com",
  "role": "staff",
  "must_change_password": false
}
```

After this, the user can use their own password for all future logins.

---

## 🔌 API Endpoints

### Authentication Endpoints

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** JWT tokens (access + refresh)

---

#### Get Current User Info
```http
GET /api/auth/me
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response:** User information (id, email, role, must_change_password)

---

#### Change Password
```http
POST /api/auth/change-password
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "current_password": "old_password",
  "new_password": "new_password"
}
```

---

### Admin Endpoints

#### Create User (Admin/Owner Only)
```http
POST /api/admin/users
Authorization: Bearer ADMIN_OR_OWNER_TOKEN
Content-Type: application/json

{
  "email": "newuser@example.com",
  "role": "staff"
}
```

**Possible roles:**
- `admin` (only admins can create)
- `owner` (admins and owners can create)
- `staff` (admins and owners can create)

---

## 🔒 Security Best Practices

### Password Requirements

**Current requirements:**
- Minimum 8 characters (enforced in CLI)
- No maximum length

**Recommended for production:**
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

To add this validation, update `app/schemas/user.py`:

```python
from pydantic import field_validator

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain a number')
        return v
```

---

### Temporary Password Security

**Current implementation:**
- Generated with `secrets.choice()` (cryptographically secure)
- 12 characters long
- Contains uppercase, lowercase, and digits
- Only returned once when user is created
- User must change it on first login

**Good practices:**
- ✅ Never log temporary passwords
- ✅ Transmit via secure channels only
- ✅ Expire temporary passwords after 24-48 hours (future feature)
- ✅ Track password change attempts

---

### JWT Token Security

**Current settings:**
- Access token: 30 minutes
- Refresh token: 7 days
- Algorithm: HS256

**Production recommendations:**
- Store `SECRET_KEY` in environment variables (never in code)
- Rotate `SECRET_KEY` periodically
- Consider shorter token lifetimes for high-security applications
- Implement token blacklist for logout (future feature)

---

## 🚀 Quick Reference

### Create Super Admin
```bash
python create_admin.py
```

### Create Owner (as Admin)
```bash
curl -X POST http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@example.com","role":"owner"}'
```

### Create Staff (as Owner)
```bash
curl -X POST http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer $OWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"staff@example.com","role":"staff"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### Change Password
```bash
curl -X POST http://localhost:8000/api/auth/change-password \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"current_password":"old","new_password":"new"}'
```

---

## 🆘 Troubleshooting

### "Admin already exists"
```
❌ Error: User with email 'admin@restocost.com' already exists.
   This user is already an admin.
```

**Solution:** The admin user already exists. Use the existing credentials or create a new admin with a different email.

---

### "Email already registered"
```json
{
  "detail": "Email already registered"
}
```

**Solution:** Choose a different email address. Each user must have a unique email.

---

### "Only administrators can perform this action"
```json
{
  "detail": "Only administrators can perform this action"
}
```

**Solution:** You're trying to create a user without proper permissions. Only `admin` and `owner` roles can create users.

---

### "Current password is incorrect"
```json
{
  "detail": "Current password is incorrect"
}
```

**Solution:** When changing password, make sure you provide the correct current password.

---

## 📖 Additional Resources

- [Main README](../README.md) - Project overview
- [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI
- [CLAUDE.md](../CLAUDE.md) - Development conventions

---

**Last Updated:** 2026-06-19
**Version:** 0.1.0
