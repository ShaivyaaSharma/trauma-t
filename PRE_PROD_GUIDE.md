# 🚀 TTI Production Deployment Guide (Vercel Unified)

This guide helps you deploy the entire Trauma Transformation Institute platform (Frontend + Backend) to **Vercel** as a single project.

---

### 1️⃣ Prepare for Production

#### A. MongoDB Atlas (Cloud Database)
1. Go to [MongoDB Atlas](https://cloud.mongodb.com/) and create a **Free (M0)** cluster.
2. Under **Network Access**, add `0.0.0.0/0` (Allow access from anywhere, required for Vercel).
3. Under **Database Access**, create a user and password.
4. Click **Connect** → **Drivers** and copy your `connection string`.
   - Your string looks like: `mongodb+srv://user:pass@cluster.xxxx.mongodb.net/?retryWrites=true&w=majority`

#### B. GitHub
1. Create a new **Private Repository** on GitHub.
2. Push your current project code to this repo:
   ```bash
   git init
   git add .
   git commit -m "Production ready release"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

---

### 2️⃣ Deploy to Vercel

1. Log in to your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** → **Project**.
3. Import your GitHub repository.
4. **Configure Project:**
   - **Framework Preset:** `Other` (Vercel will detect settings from `vercel.json`).
   - **Root Directory:** Keep as `./` (Project Root).

5. **Environment Variables (CRITICAL):**
   Add the following variables in the Vercel dashboard:
   
   | Key | Value |
   |-----|-------|
   | `MONGO_URL` | Your MongoDB Atlas connection string |
   | `DB_NAME` | `tti_db` |
   | `JWT_SECRET_KEY` | Use a long random string (e.g., `openssl rand -hex 32`) |
   | `STRIPE_API_KEY` | `sk_test_...` (Optional, for payments) |
   | `REACT_APP_BACKEND_URL` | `/api` (This tells the frontend to use the relative Vercel path) |

6. Click **Deploy**. Vercel will build the React frontend and deploy the FastAPI backend as serverless functions.

---

### 3️⃣ Seed Your Production Database

Once the app is deployed, your database will be empty. You need to seed the courses and modules.

1. Install requirements locally: `pip install -r backend/requirements.txt`
2. Run the seeding scripts from your terminal, pointing to the **Production MongoDB**:
   ```bash
   # Set the prod URL temporarily in your terminal
   export MONGO_URL="your_mongodb_atlas_connection_string"
   export DB_NAME="tti_db"

   # Run seeding scripts
   python3 backend/sync_courses.py
   python3 backend/seed_utility_courses.py
   python3 backend/seed_clinical_curriculum.py
   ```

---

### 🛠️ Production Verification Checklist
- [ ] Visit your Vercel URL (e.g., `tti-app.vercel.app`).
- [ ] Check if courses are visible on the landing page.
- [ ] Try creating a new account (Sign up).
- [ ] Log in and verify you can see the Course Details page.
- [ ] Verify you can see the "Module Breakdown" section on Clinical courses.
- [ ] Test a "Coming Soon" course (it should show 'Registration Closed').

---

### 📝 Project Structure for Vercel
- `/package.json`: **(New)** Root manifest for project scripts and monorepo management.
- `/api/index.py`: Entry point for FastAPI serverless functions.
- `/backend/`: Core business logic and database models.
- `/frontend/`: React application (automatically built to static files).
- `/vercel.json`: Unified routing configuration.
- `/requirements.txt`: Root requirements for the Python runtime.
