import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, CreditCard, CheckCircle, Loader2, Shield, ChevronLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL || ''}/api`;

const DemoPaymentPage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { token } = useAuth();

    const courseId = searchParams.get('course_id');
    const courseTitle = searchParams.get('course_title') || 'Course';
    const coursePrice = searchParams.get('price') || '0';

    const [step, setStep] = useState('form'); // 'form' | 'processing' | 'success'
    const [cardNumber, setCardNumber] = useState('');
    const [expiry, setExpiry] = useState('');
    const [cvv, setCvv] = useState('');
    const [name, setName] = useState('');

    const formatCardNumber = (val) => {
        const digits = val.replace(/\D/g, '').slice(0, 16);
        return digits.replace(/(.{4})/g, '$1 ').trim();
    };

    const formatExpiry = (val) => {
        const digits = val.replace(/\D/g, '').slice(0, 4);
        if (digits.length >= 3) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
        return digits;
    };

    const handlePay = async (e) => {
        e.preventDefault();
        if (!courseId) {
            toast.error('No course selected');
            return;
        }

        setStep('processing');

        // Simulate a 2-second payment processing delay
        await new Promise((r) => setTimeout(r, 2000));

        try {
            await axios.post(
                `${API}/demo/enroll`,
                { course_id: courseId },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setStep('success');
            // Auto-redirect to dashboard after 2s
            setTimeout(() => navigate('/dashboard'), 2000);
        } catch (error) {
            const msg = error.response?.data?.detail || 'Enrollment failed';
            toast.error(msg);
            if (msg === 'Already enrolled in this course') {
                setTimeout(() => navigate('/dashboard'), 1500);
            } else {
                setStep('form');
            }
        }
    };

    const formatPrice = (price) =>
        new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0,
        }).format(Number(price));

    return (
        <div className="min-h-screen bg-gradient-to-br from-navy-900 via-navy-800 to-sky/30 flex items-center justify-center p-4">

            {/* Back button */}
            <button
                onClick={() => navigate(-1)}
                className="absolute top-6 left-6 flex items-center gap-1 text-white/60 hover:text-white text-sm transition-colors"
            >
                <ChevronLeft className="w-4 h-4" /> Back
            </button>

            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md"
            >
                {/* Card */}
                <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">

                    {/* Header */}
                    <div className="bg-gradient-to-r from-navy-900 to-sky px-8 py-6">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                                <Lock className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <p className="text-white/70 text-xs font-dm-sans">Secure Payment</p>
                                <p className="text-white font-playfair font-bold text-sm">Trauma Transformation Institute</p>
                            </div>
                        </div>
                        <div className="bg-white/10 rounded-2xl p-4">
                            <p className="text-white/70 text-xs font-dm-sans mb-1">Enrolling in</p>
                            <p className="text-white font-playfair font-semibold text-base leading-snug">{courseTitle}</p>
                            <p className="text-sky text-2xl font-bold font-playfair mt-2">{formatPrice(coursePrice)}</p>
                        </div>
                    </div>

                    {/* Body */}
                    <div className="px-8 py-6">

                        {/* Success State */}
                        {step === 'success' && (
                            <motion.div
                                initial={{ scale: 0.8, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                className="text-center py-8"
                            >
                                <div className="w-20 h-20 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
                                    <CheckCircle className="w-10 h-10 text-emerald-600" />
                                </div>
                                <h2 className="text-2xl font-playfair font-bold text-navy-900 mb-2">Payment Successful!</h2>
                                <p className="text-navy-500 font-dm-sans text-sm">Redirecting to your dashboard…</p>
                            </motion.div>
                        )}

                        {/* Processing State */}
                        {step === 'processing' && (
                            <div className="text-center py-8">
                                <Loader2 className="w-12 h-12 text-sky animate-spin mx-auto mb-4" />
                                <h2 className="text-xl font-playfair font-bold text-navy-900 mb-2">Processing Payment</h2>
                                <p className="text-navy-500 font-dm-sans text-sm">Please don't close this window…</p>
                            </div>
                        )}

                        {/* Form State */}
                        {step === 'form' && (
                            <form onSubmit={handlePay} className="space-y-4">
                                <div>
                                    <label className="block text-xs font-dm-sans text-navy-500 mb-1">Cardholder Name</label>
                                    <input
                                        type="text"
                                        required
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        placeholder="John Doe"
                                        className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-sky focus:ring-2 focus:ring-sky/20 outline-none text-navy-900 font-dm-sans text-sm transition-all"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-dm-sans text-navy-500 mb-1">Card Number</label>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            required
                                            value={cardNumber}
                                            onChange={(e) => setCardNumber(formatCardNumber(e.target.value))}
                                            placeholder="4242 4242 4242 4242"
                                            maxLength={19}
                                            className="w-full px-4 py-3 pr-12 rounded-xl border border-slate-200 focus:border-sky focus:ring-2 focus:ring-sky/20 outline-none text-navy-900 font-dm-sans text-sm transition-all"
                                        />
                                        <CreditCard className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-3">
                                    <div>
                                        <label className="block text-xs font-dm-sans text-navy-500 mb-1">Expiry</label>
                                        <input
                                            type="text"
                                            required
                                            value={expiry}
                                            onChange={(e) => setExpiry(formatExpiry(e.target.value))}
                                            placeholder="MM/YY"
                                            maxLength={5}
                                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-sky focus:ring-2 focus:ring-sky/20 outline-none text-navy-900 font-dm-sans text-sm transition-all"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-dm-sans text-navy-500 mb-1">CVV</label>
                                        <input
                                            type="password"
                                            required
                                            value={cvv}
                                            onChange={(e) => setCvv(e.target.value.replace(/\D/g, '').slice(0, 3))}
                                            placeholder="•••"
                                            maxLength={3}
                                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-sky focus:ring-2 focus:ring-sky/20 outline-none text-navy-900 font-dm-sans text-sm transition-all"
                                        />
                                    </div>
                                </div>

                                {/* Demo notice */}
                                <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 flex items-start gap-2">
                                    <span className="text-amber-600 text-xs mt-0.5">ℹ️</span>
                                    <p className="text-amber-700 text-xs font-dm-sans">
                                        <strong>Demo Mode.</strong> No real payment is processed. Enter any card details to enroll.
                                    </p>
                                </div>

                                <Button
                                    type="submit"
                                    className="w-full bg-gradient-to-r from-navy-900 to-sky hover:opacity-90 text-white rounded-xl py-4 font-dm-sans font-semibold text-sm transition-all shadow-lg"
                                >
                                    <Lock className="w-4 h-4 mr-2" />
                                    Pay {formatPrice(coursePrice)} & Enroll
                                </Button>

                                <div className="flex items-center justify-center gap-2 text-slate-400 text-xs font-dm-sans">
                                    <Shield className="w-3 h-3" />
                                    <span>256-bit SSL encrypted transaction</span>
                                </div>
                            </form>
                        )}

                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default DemoPaymentPage;
