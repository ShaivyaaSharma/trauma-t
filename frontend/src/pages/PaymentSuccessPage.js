import { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Loader2, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const PaymentSuccessPage = () => {
  const [searchParams] = useSearchParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [status, setStatus] = useState('loading'); // loading, success, error
  const [attempts, setAttempts] = useState(0);

  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    if (!sessionId) {
      setStatus('error');
      return;
    }

    const pollPaymentStatus = async () => {
      const maxAttempts = 10;
      const pollInterval = 2000;

      if (attempts >= maxAttempts) {
        setStatus('error');
        return;
      }

      try {
        const response = await axios.get(`${API}/payments/status/${sessionId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data.payment_status === 'paid') {
          setStatus('success');
          return;
        } else if (response.data.status === 'expired') {
          setStatus('error');
          return;
        }

        // Continue polling
        setTimeout(() => {
          setAttempts(prev => prev + 1);
        }, pollInterval);
      } catch (error) {
        console.error('Error checking payment:', error);
        setTimeout(() => {
          setAttempts(prev => prev + 1);
        }, pollInterval);
      }
    };

    pollPaymentStatus();
  }, [sessionId, token, attempts]);

  return (
    <div className="min-h-screen bg-navy-50/30 flex items-center justify-center px-6 py-12">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card className="border-slate-200 shadow-card-hover">
          <CardContent className="p-8 text-center">
            {status === 'loading' && (
              <>
                <div className="w-16 h-16 rounded-full bg-sky/10 flex items-center justify-center mx-auto mb-6">
                  <Loader2 className="w-8 h-8 text-sky animate-spin" />
                </div>
                <h1 className="text-2xl font-playfair font-bold text-navy-900 mb-2">
                  Processing Payment
                </h1>
                <p className="font-dm-sans text-navy-500 mb-6">
                  Please wait while we confirm your payment...
                </p>
                <div className="flex justify-center gap-1">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className="w-2 h-2 rounded-full bg-sky animate-bounce"
                      style={{ animationDelay: `${i * 0.1}s` }}
                    />
                  ))}
                </div>
              </>
            )}

            {status === 'success' && (
              <>
                <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-6">
                  <CheckCircle className="w-8 h-8 text-emerald-600" />
                </div>
                <h1 className="text-2xl font-playfair font-bold text-navy-900 mb-2" data-testid="success-title">
                  Enrollment Successful!
                </h1>
                <p className="font-dm-sans text-navy-500 mb-8">
                  Thank you for enrolling. You will receive a confirmation email with course details shortly.
                </p>
                <div className="space-y-3">
                  <Button 
                    className="w-full bg-navy-900 hover:bg-navy-800 font-dm-sans"
                    onClick={() => navigate('/dashboard')}
                    data-testid="go-dashboard-btn"
                  >
                    Go to Dashboard
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                  <Link to="/">
                    <Button variant="outline" className="w-full font-dm-sans">
                      Back to Home
                    </Button>
                  </Link>
                </div>
              </>
            )}

            {status === 'error' && (
              <>
                <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-6">
                  <XCircle className="w-8 h-8 text-red-600" />
                </div>
                <h1 className="text-2xl font-playfair font-bold text-navy-900 mb-2">
                  Payment Issue
                </h1>
                <p className="font-dm-sans text-navy-500 mb-8">
                  We couldn't confirm your payment. Please contact support or try again.
                </p>
                <div className="space-y-3">
                  <Link to="/dashboard">
                    <Button className="w-full bg-navy-900 hover:bg-navy-800 font-dm-sans">
                      Check Dashboard
                    </Button>
                  </Link>
                  <Link to="/">
                    <Button variant="outline" className="w-full font-dm-sans">
                      Back to Home
                    </Button>
                  </Link>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default PaymentSuccessPage;
