import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';

const SignupPage = () => {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!name || !email || !password || !confirmPassword) {
      toast.error('Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      await signup(email, password, name);
      toast.success('Account created successfully!');
      navigate('/dashboard', { replace: true });
    } catch (error) {
      console.error('Signup error:', error);
      const message = error.response?.data?.detail || 'Failed to create account';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-navy-50/30 flex items-center justify-center px-6 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Back Link */}
        <Link 
          to="/" 
          className="inline-flex items-center gap-2 text-navy-500 hover:text-navy-900 transition-colors mb-8"
          data-testid="back-home-link"
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="font-dm-sans text-sm">Back to Home</span>
        </Link>

        <Card className="border-slate-200 shadow-card">
          <CardHeader className="text-center pb-2">
            <div className="w-12 h-12 bg-navy-900 rounded-sm flex items-center justify-center mx-auto mb-4">
              <span className="text-white font-playfair font-bold text-xl">T</span>
            </div>
            <CardTitle className="text-2xl font-playfair text-navy-900">
              Create Account
            </CardTitle>
            <CardDescription className="font-dm-sans">
              Join TTI to start your transformation journey
            </CardDescription>
          </CardHeader>
          
          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name" className="font-dm-sans text-navy-700">
                  Full Name
                </Label>
                <Input
                  id="name"
                  type="text"
                  placeholder="Dr. John Smith"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="h-12 font-dm-sans bg-slate-50 border-slate-200 focus:bg-white"
                  data-testid="name-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email" className="font-dm-sans text-navy-700">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="h-12 font-dm-sans bg-slate-50 border-slate-200 focus:bg-white"
                  data-testid="email-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="font-dm-sans text-navy-700">
                  Password
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-12 font-dm-sans bg-slate-50 border-slate-200 focus:bg-white pr-10"
                    data-testid="password-input"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-navy-400 hover:text-navy-600"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="font-dm-sans text-navy-700">
                  Confirm Password
                </Label>
                <Input
                  id="confirmPassword"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="h-12 font-dm-sans bg-slate-50 border-slate-200 focus:bg-white"
                  data-testid="confirm-password-input"
                />
              </div>

              <Button 
                type="submit" 
                className="w-full h-12 bg-navy-900 hover:bg-navy-800 font-dm-sans font-medium mt-6"
                disabled={loading}
                data-testid="signup-submit-btn"
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Creating account...
                  </div>
                ) : (
                  'Create Account'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="font-dm-sans text-sm text-navy-500">
                Already have an account?{' '}
                <Link 
                  to="/login" 
                  className="text-sky hover:text-sky/80 font-medium"
                  data-testid="login-link"
                >
                  Sign in
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default SignupPage;
