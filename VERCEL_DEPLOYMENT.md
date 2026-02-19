# 🚀 TTI App - Vercel Deployment Quick Start

## ✅ Pre-Deployment Verification

Your app is **ready for Vercel deployment**! 

### What's Already Done:
- ✅ No hardcoded URLs in codebase
- ✅ All URLs use environment variables
- ✅ CORS configured to allow all origins
- ✅ Vercel configuration files created
- ✅ Production environment templates ready
- ✅ .gitignore configured properly

---

## 📋 Quick Deployment Steps

### 1️⃣ Deploy Backend First (Railway - Recommended)

**Why Railway?** 
- Easiest for FastAPI
- Free $5/month credit
- Automatic HTTPS
- One-click deployment

**Steps:**
```bash
# 1. Go to https://railway.app/
# 2. Sign up with GitHub
# 3. Click "New Project" → "Deploy from GitHub repo"
# 4. Select your repository
# 5. Select "backend" folder
# 6. Add environment variables:

MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/tti_db
DB_NAME=tti_db
JWT_SECRET_KEY=your-super-secret-key-here-min-32-chars
STRIPE_API_KEY=sk_test_your_stripe_key
CORS_ORIGINS=*
PORT=8001

# 7. Deploy!
# 8. Copy your backend URL (e.g., https://tti-backend.up.railway.app)
```

### 2️⃣ Deploy Frontend to Vercel

**Option A: Using Vercel Dashboard (Easiest)**

1. **Push to GitHub:**
   ```bash
   cd /app
   git add .
   git commit -m "Ready for Vercel deployment"
   git push origin main
   ```

2. **Import to Vercel:**
   - Go to https://vercel.com/new
   - Click "Import Git Repository"
   - Select your repository
   - Configure:
     - **Framework**: Create React App
     - **Root Directory**: `frontend`
     - **Build Command**: `yarn build`
     - **Output Directory**: `build`
     - **Install Command**: `yarn install`

3. **Add Environment Variable:**
   ```
   REACT_APP_BACKEND_URL=https://your-backend.railway.app
   ```
   (Use your actual Railway backend URL)

4. **Deploy!** 🚀

**Option B: Using Vercel CLI**

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod

# Set environment variable
vercel env add REACT_APP_BACKEND_URL production
# Enter your backend URL when prompted
```

### 3️⃣ Setup MongoDB Atlas (Free)

```bash
# 1. Go to https://cloud.mongodb.com/
# 2. Create free M0 cluster
# 3. Create database user
# 4. Add network access: 0.0.0.0/0 (Allow from anywhere)
# 5. Get connection string:
#    mongodb+srv://username:password@cluster.mongodb.net/tti_db
# 6. Add to Railway backend environment variables
```

### 4️⃣ Seed Database

```bash
# Replace with your actual backend URL

# Seed courses
curl -X POST https://your-backend.railway.app/api/seed

# Seed modules
curl -X POST https://your-backend.railway.app/api/seed-modules

# Verify
curl https://your-backend.railway.app/api/courses
```

---

## 🛠️ Automated Deployment Scripts

### Check Deployment Readiness:
```bash
cd /app
./check-deployment-readiness.sh
```

### Quick Deploy:
```bash
cd /app
./deploy-to-vercel.sh
```

---

## 📝 Environment Variables Reference

### Backend (Railway/Render):
```bash
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/tti_db
DB_NAME=tti_db
JWT_SECRET_KEY=your-random-secret-key-minimum-32-characters
STRIPE_API_KEY=sk_test_51xxxxx  # Get from stripe.com
CORS_ORIGINS=*
PORT=8001  # Railway sets this automatically
```

### Frontend (Vercel):
```bash
REACT_APP_BACKEND_URL=https://your-backend.railway.app
```

---

## ✅ Deployment Checklist

Before deploying, ensure:

- [ ] Code pushed to GitHub
- [ ] MongoDB Atlas cluster created
- [ ] Database user created with password
- [ ] Network access configured (0.0.0.0/0)
- [ ] Backend deployed (Railway/Render)
- [ ] Backend environment variables set
- [ ] Backend health check passes: `curl https://your-backend/api/health`
- [ ] Database seeded (courses + modules)
- [ ] Frontend deployed to Vercel
- [ ] Frontend environment variable set (REACT_APP_BACKEND_URL)
- [ ] Test signup/login on production
- [ ] Test course enrollment
- [ ] Test learning modules

---

## 🧪 Testing Your Deployment

### Test Backend:
```bash
# Health check
curl https://your-backend.railway.app/api/health

# Get courses
curl https://your-backend.railway.app/api/courses

# Test signup
curl -X POST https://your-backend.railway.app/api/auth/signup \\
  -H "Content-Type: application/json" \\
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'
```

### Test Frontend:
1. Visit your Vercel URL
2. Try signup/login
3. View courses
4. Test enrollment flow
5. Access learning modules
6. Take a quiz

---

## 🐛 Troubleshooting

### Issue: CORS Error
**Solution:**
- Verify `CORS_ORIGINS=*` in backend env vars
- Check backend logs
- Ensure backend is running

### Issue: API Calls Failing
**Solution:**
- Check `REACT_APP_BACKEND_URL` in Vercel dashboard
- Verify backend URL is accessible
- Check browser console for errors

### Issue: Database Connection Failed
**Solution:**
- Verify MongoDB connection string
- Check username and password
- Ensure network access is 0.0.0.0/0
- Test connection from backend logs

### Issue: Build Failed
**Solution:**
- Run `cd frontend && yarn build` locally
- Check build logs in Vercel
- Ensure all dependencies are in package.json

---

## 📚 Documentation Files

- **DEPLOYMENT_GUIDE.md** - Complete step-by-step deployment guide
- **.env.example** - Environment variables template
- **frontend/vercel.json** - Vercel frontend configuration
- **vercel.json** - Vercel root configuration
- **.vercelignore** - Files to exclude from deployment

---

## 💰 Estimated Costs

### Free Tier (Perfect for Testing):
- **Vercel**: Free (100GB bandwidth/month)
- **Railway**: $5 credit/month (no credit card)
- **MongoDB Atlas**: Free M0 cluster (512MB)
- **Total**: $0/month for testing

### Production (For scale):
- **Vercel Pro**: $20/month
- **Railway**: ~$5-20/month (pay-as-you-go)
- **MongoDB**: ~$9/month (M2 cluster)
- **Total**: ~$34-49/month

---

## 🎯 Success Criteria

Your deployment is successful when:

1. ✅ Backend health check returns 200 OK
2. ✅ Frontend loads without errors
3. ✅ Signup/login works
4. ✅ Courses are visible
5. ✅ Payment flow works (test mode)
6. ✅ Learning modules accessible
7. ✅ Quiz system works
8. ✅ Module progression works (unlock after passing)

---

## 📞 Need Help?

If you encounter issues:

1. Check this README first
2. Review DEPLOYMENT_GUIDE.md
3. Check deployment logs in dashboard
4. Run `./check-deployment-readiness.sh`
5. Test APIs with curl
6. Check browser console

---

## 🎉 After Successful Deployment

1. **Share your app** - Send the Vercel URL to users
2. **Monitor usage** - Check Vercel and Railway dashboards
3. **Set up alerts** - MongoDB Atlas and error tracking
4. **Add custom domain** - Optional but professional
5. **Configure Stripe live keys** - When ready for production
6. **Celebrate!** 🎊

---

**Ready to Deploy? Start with Step 1! 🚀**

For detailed instructions, see **DEPLOYMENT_GUIDE.md**
