import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, CreditCard, Lock, ArrowRight, Loader2, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

const MockCheckoutPage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [isProcessing, setIsProcessing] = useState(false);
    const [isDone, setIsDone] = useState(false);

    const sessionId = searchParams.get('session_id');
    const successUrl = searchParams.get('success_url');

    const handlePay = () => {
        setIsProcessing(true);
        // Simulate gateway delay
        setTimeout(() => {
            setIsDone(true);
            setTimeout(() => {
                // Redirect back to the success URL provided by backend
                const finalUrl = successUrl.replace('{CHECKOUT_SESSION_ID}', sessionId);
                window.location.href = finalUrl;
            }, 1500);
        }, 2500);
    };

    return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
            <div className="w-full max-w-[900px] grid md:grid-cols-2 gap-8 bg-white rounded-2xl shadow-2xl overflow-hidden border border-slate-100">

                {/* Left Side: Order Summary */}
                <div className="bg-navy-900 p-8 text-white flex flex-col justify-between">
                    <div>
                        <div className="flex items-center gap-2 mb-8">
                            <div className="w-8 h-8 bg-sky rounded-lg flex items-center justify-center">
                                <ShieldCheck className="w-5 h-5 text-navy-900" />
                            </div>
                            <span className="font-playfair font-bold text-xl tracking-tight">TraumaTransformation</span>
                        </div>

                        <div className="space-y-6">
                            <div>
                                <p className="text-navy-300 text-sm font-dm-sans mb-1 uppercase tracking-wider">Payment to</p>
                                <h2 className="text-2xl font-playfair font-semibold italic text-sky">TTI Global Academy</h2>
                            </div>

                            <div className="space-y-4">
                                <div className="flex justify-between items-center text-navy-200">
                                    <span className="font-dm-sans">Professional Certification</span>
                                    <span className="font-dm-sans">₹29,000.00</span>
                                </div>
                                <div className="flex justify-between items-center text-navy-200 text-sm">
                                    <span className="font-dm-sans">Learning Platform Fee</span>
                                    <Badge variant="outline" className="text-sky border-sky/30 text-[10px]">WAIVED</Badge>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="pt-8 border-t border-white/10">
                        <div className="flex justify-between items-end">
                            <div>
                                <p className="text-navy-300 text-sm font-dm-sans">Total Amount</p>
                                <p className="text-4xl font-playfair font-bold text-white">₹29,000.00</p>
                            </div>
                            <div className="text-right">
                                <p className="text-[10px] text-navy-400 font-dm-sans uppercase tracking-[2px] mb-1">Secure Transaction</p>
                                <div className="flex gap-1 justify-end">
                                    <div className="w-6 h-4 bg-white/10 rounded-sm" />
                                    <div className="w-6 h-4 bg-white/10 rounded-sm" />
                                    <div className="w-6 h-4 bg-white/10 rounded-sm" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Side: Payment Form */}
                <div className="p-8 relative">
                    <AnimatePresence mode="wait">
                        {!isProcessing ? (
                            <motion.div
                                key="form"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="space-y-6"
                            >
                                <div className="flex justify-between items-center">
                                    <h3 className="text-xl font-dm-sans font-bold text-navy-900">Payment Details</h3>
                                    <div className="flex items-center gap-1 text-emerald-600 text-[10px] font-bold tracking-tighter uppercase px-2 py-1 bg-emerald-50 rounded-full">
                                        <Lock className="w-3 h-3" />
                                        Encrypted
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="text-xs font-dm-sans font-semibold text-navy-500 uppercase tracking-wider">Email Address</label>
                                        <Input disabled placeholder="student@university.edu" className="bg-slate-50 border-slate-200 h-12" />
                                    </div>

                                    <div className="space-y-2">
                                        <label className="text-xs font-dm-sans font-semibold text-navy-500 uppercase tracking-wider">Card Information</label>
                                        <div className="relative">
                                            <Input placeholder="4242 4242 4242 4242" className="pl-12 h-12 border-slate-200 focus:ring-sky" />
                                            <CreditCard className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <label className="text-xs font-dm-sans font-semibold text-navy-500 uppercase tracking-wider">Expiry</label>
                                            <Input placeholder="MM / YY" className="h-12 border-slate-200" />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-xs font-dm-sans font-semibold text-navy-500 uppercase tracking-wider">CVC</label>
                                            <Input placeholder="123" className="h-12 border-slate-200" />
                                        </div>
                                    </div>
                                </div>

                                <div className="pt-4">
                                    <Button
                                        onClick={handlePay}
                                        className="w-full h-14 bg-sky hover:bg-sky/90 text-navy-900 font-bold text-lg shadow-lg shadow-sky/20 transition-all hover:scale-[1.01]"
                                    >
                                        Pay ₹29,000.00
                                        <ArrowRight className="w-5 h-5 ml-2" />
                                    </Button>
                                </div>

                                <p className="text-[10px] text-center text-slate-400 font-dm-sans leading-relaxed">
                                    By confirming your payment, you agree to the Trauma Transformation Institute Terms of Service
                                    and Privacy Policy. Secure processing by TTI Gateway.
                                </p>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="processing"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="h-full flex flex-col items-center justify-center text-center space-y-6 py-12"
                            >
                                {!isDone ? (
                                    <>
                                        <div className="relative">
                                            <Loader2 className="w-20 h-20 text-sky animate-spin stroke-[1px]" />
                                            <Lock className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-navy-200" />
                                        </div>
                                        <div className="space-y-2">
                                            <h3 className="text-2xl font-playfair font-bold text-navy-900 italic">Authenticating...</h3>
                                            <p className="text-sm font-dm-sans text-slate-500">Connecting to your financial institution</p>
                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <motion.div
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center"
                                        >
                                            <CheckCircle2 className="w-12 h-12 text-emerald-600" />
                                        </motion.div>
                                        <div className="space-y-2">
                                            <h3 className="text-2xl font-playfair font-bold text-navy-900 italic">Payment Authorized</h3>
                                            <p className="text-sm font-dm-sans text-slate-500">Secure record created. Redirecting...</p>
                                        </div>
                                    </>
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
};

export default MockCheckoutPage;
