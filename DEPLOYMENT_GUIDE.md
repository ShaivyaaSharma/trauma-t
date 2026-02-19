# TTI App - Vercel Deployment Guide

## 🚀 Deployment Strategy

Since this is a full-stack application with FastAPI backend and React frontend, you'll need to deploy them separately:

### Option 1: Separate Deployments (Recommended)
- **Frontend**: Deploy to Vercel
- **Backend**: Deploy to Vercel (as serverless) or Railway/Render/Heroku
- **Database**: MongoDB Atlas (free tier available)

### Option 2: Backend as Vercel Serverless Functions
- Convert FastAPI routes to Vercel serverless functions
- More complex but single deployment

---

## 📋 Prerequisites

1. **Vercel Account**: https://vercel.com/signup
2. **MongoDB Atlas Account**: https://www.mongodb.com/cloud/atlas/register
3. **Stripe Account**: https://dashboard.stripe.com/register (for payments)
4. **GitHub Repository**: Push your code to GitHub

---

## 🗄️ Step 1: Setup MongoDB Atlas

1. **Create Cluster**:
   - Go to https://cloud.mongodb.com/
   - Create a free M0 cluster
   - Choose a region close to your users

2. **Configure Network Access**:
   - Go to Network Access
   - Click "Add IP Address"
   - Select "Allow Access from Anywhere" (0.0.0.0/0)
   - Or add Vercel's IP ranges

3. **Create Database User**:
   - Go to Database Access
   - Add new database user
   - Choose password authentication
   - Save username and password

4. **Get Connection String**:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/tti_db?retryWrites=true&w=majority
   ```
   - Replace `<username>` and `<password>`
   - Replace `tti_db` with your database name

---

## 🔧 Step 2: Deploy Backend

### Option A: Deploy to Railway (Easiest for FastAPI)

1. **Go to Railway**: https://railway.app/
2. **Create New Project** → Deploy from GitHub
3. **Select Repository** → Choose backend folder
4. **Configure**:
   - Set root directory to `backend`
   - Add start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

5. **Environment Variables**:
   ```
   MONGO_URL=your_mongodb_atlas_connection_string
   DB_NAME=tti_db
   JWT_SECRET_KEY=your_random_secret_key_here
   STRIPE_API_KEY=your_stripe_api_key
   CORS_ORIGINS=*
   PORT=8001
   ```

6. **Deploy** → Copy the public URL (e.g., `https://your-app.up.railway.app`)

### Option B: Deploy to Render

1. **Go to Render**: https://render.com/
2. **New Web Service** → Connect GitHub
3. **Configure**:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables** (same as above)
5. **Deploy** → Copy the URL

### Option C: Deploy Backend to Vercel (Serverless)

**Note**: This requires converting your FastAPI app to work with Vercel's serverless environment.

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Deploy Backend**:
   ```bash
   cd backend
   vercel --prod
   ```

4. **Set Environment Variables** in Vercel Dashboard:
   - Go to Project Settings → Environment Variables
   - Add all backend env vars

---

## 🎨 Step 3: Deploy Frontend to Vercel

### Method 1: Using Vercel Dashboard (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Import to Vercel**:
   - Go to https://vercel.com/new
   - Click "Import Git Repository"
   - Select your GitHub repository
   - Choose the repository

3. **Configure Project**:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn build`
   - **Output Directory**: `build`
   - **Install Command**: `yarn install`

4. **Environment Variables**:
   ```
   REACT_APP_BACKEND_URL=https://your-backend-url.railway.app
   ```
   ⚠️ **Important**: Use your actual backend URL from Step 2

5. **Deploy**: Click "Deploy"
   - Wait for build to complete (~2-3 minutes)
   - Your app will be live at `https://your-project.vercel.app`

### Method 2: Using Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Deploy Frontend**:
   ```bash
   cd frontend
   vercel --prod
   ```

4. **Set Environment Variables**:
   ```bash
   vercel env add REACT_APP_BACKEND_URL production
   ```
   Enter your backend URL when prompted

---

## 📊 Step 4: Seed Database

After deployment, seed your database with initial data:

1. **Seed Courses**:
   ```bash
   curl -X POST https://your-backend-url.railway.app/api/seed
   ```

2. **Seed Modules**:
   ```bash
   curl -X POST https://your-backend-url.railway.app/api/seed-modules
   ```

3. **Verify**:
   ```bash
   curl https://your-backend-url.railway.app/api/courses
   ```

---

## ✅ Step 5: Verify Deployment

### Test Backend:
```bash
# Health check
curl https://your-backend-url.railway.app/api/health

# Get courses
curl https://your-backend-url.railway.app/api/courses
```

### Test Frontend:
1. Visit your Vercel URL: `https://your-project.vercel.app`
2. Try to signup/login
3. Enroll in a course
4. Access learning modules

---

## 🔐 Step 6: Create Demo Account (Optional)

Create a demo account for testing:

```bash
curl -X POST https://your-backend-url.railway.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@tti.com","password":"demo123","name":"Demo User"}'
```

Then enroll them in the course (use MongoDB Atlas UI or connect via CLI).

---

## 🔄 Continuous Deployment

Both Vercel and Railway support automatic deployments:

- **Push to GitHub** → Automatically deploys
- **Preview Deployments** for pull requests
- **Production** deploys from main branch

---

## 🌐 Custom Domain (Optional)

### For Frontend (Vercel):
1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

### For Backend (Railway/Render):
1. Go to Settings → Custom Domain
2. Add your domain
3. Update DNS records

---

## 🔧 Environment Variables Summary

### Backend (.env or Platform Settings):
```bash
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/tti_db
DB_NAME=tti_db
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
STRIPE_API_KEY=sk_live_your_stripe_key  # or sk_test_ for testing
CORS_ORIGINS=*
PORT=8001  # Railway/Render will set this automatically
```

### Frontend (Vercel):
```bash
REACT_APP_BACKEND_URL=https://your-backend.railway.app
```

---

## 📝 Deployment Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created with password
- [ ] Network access configured (0.0.0.0/0)
- [ ] Backend deployed (Railway/Render/Vercel)
- [ ] Backend environment variables set
- [ ] Backend health check passes
- [ ] Database seeded (courses + modules)
- [ ] Frontend deployed to Vercel
- [ ] Frontend environment variable set (REACT_APP_BACKEND_URL)
- [ ] Frontend can access backend API
- [ ] CORS working correctly
- [ ] Signup/Login works
- [ ] Course enrollment works (Stripe test mode)
- [ ] Learning modules accessible
- [ ] Quiz system working

---

## 🐛 Troubleshooting

### Issue: CORS Errors
**Solution**: 
- Check backend CORS settings allow your Vercel domain
- Verify `CORS_ORIGINS=*` in backend env vars
- Check browser console for specific CORS error

### Issue: API Calls Failing
**Solution**:
- Verify `REACT_APP_BACKEND_URL` is set correctly in Vercel
- Check backend logs for errors
- Ensure backend is running (health check)

### Issue: Database Connection Failed
**Solution**:
- Verify MongoDB connection string is correct
- Check username and password
- Ensure network access is configured (0.0.0.0/0)
- Check if cluster is running in Atlas

### Issue: Modules Not Loading
**Solution**:
- Run seed-modules endpoint: `curl -X POST https://your-backend/api/seed-modules`
- Check backend logs
- Verify database has `modules` collection

### Issue: Build Failed on Vercel
**Solution**:
- Check build logs in Vercel dashboard
- Ensure all dependencies in package.json
- Try building locally: `cd frontend && yarn build`

---

## 📊 Monitoring

### Vercel:
- View deployment logs in dashboard
- Monitor function invocations
- Check analytics

### Railway/Render:
- View application logs in real-time
- Monitor resource usage
- Set up health checks

### MongoDB Atlas:
- Monitor database metrics
- Set up alerts
- View slow queries

---

## 💰 Costs

### Free Tiers:
- **Vercel**: Free for personal projects (100GB bandwidth)
- **Railway**: $5 credit/month (no credit card required)
- **Render**: Free tier available (with limitations)
- **MongoDB Atlas**: Free M0 cluster (512MB storage)

### Paid Plans:
- **Vercel Pro**: $20/month (more bandwidth)
- **Railway**: Pay as you go (~$5-20/month)
- **MongoDB Atlas**: ~$9/month for M2 cluster

---

## 🚀 Next Steps After Deployment

1. **Configure Stripe** with live keys (not test keys)
2. **Set up email notifications** for enrollments
3. **Add analytics** (Google Analytics, Mixpanel)
4. **Set up monitoring** (Sentry for error tracking)
5. **Configure backups** for MongoDB
6. **Add SSL certificate** (automatic on Vercel/Railway)
7. **Set up custom domain**
8. **Create documentation** for users
9. **Test thoroughly** in production
10. **Launch!** 🎉

---

## 📚 Additional Resources

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app/
- **Render Docs**: https://render.com/docs
- **MongoDB Atlas Docs**: https://www.mongodb.com/docs/atlas/
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **React Deployment**: https://create-react-app.dev/docs/deployment/

---

## 🆘 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review deployment logs
3. Test APIs with curl/Postman
4. Check browser console for frontend errors
5. Verify all environment variables are set

**Happy Deploying! 🚀**