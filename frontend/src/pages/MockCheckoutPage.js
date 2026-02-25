import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Box, CheckCircle2, Lock, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const MockCheckoutPage = () => {
    const [searchParams] = useSearchParams();
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
                // Extract course_id and other details if needed, but for Stripe mock we just return
                if (successUrl) {
                    const finalUrl = decodeURIComponent(successUrl).replace('{CHECKOUT_SESSION_ID}', sessionId);
                    window.location.href = finalUrl;
                } else {
                    window.location.href = '/payment-success?session_id=' + sessionId + '&mock=1';
                }
            }, 1000);
        }, 2000);
    };

    if (isProcessing) {
        return (
            <div className="min-h-screen bg-white flex items-center justify-center p-4">
                <motion.div
                    key="processing"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="h-full flex flex-col items-center justify-center text-center space-y-6 py-12"
                >
                    {!isDone ? (
                        <>
                            <div className="relative">
                                <Loader2 className="w-16 h-16 text-[#0070F3] animate-spin stroke-[2px]" />
                                <Lock className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                            </div>
                            <div className="space-y-2">
                                <h3 className="text-xl font-medium text-slate-800">Processing Payment...</h3>
                                <p className="text-sm text-slate-500">Please don't close this window.</p>
                            </div>
                        </>
                    ) : (
                        <>
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center"
                            >
                                <CheckCircle2 className="w-10 h-10 text-emerald-600" />
                            </motion.div>
                            <div className="space-y-2">
                                <h3 className="text-xl font-medium text-slate-800">Payment Successful</h3>
                                <p className="text-sm text-slate-500">Redirecting to your course...</p>
                            </div>
                        </>
                    )}
                </motion.div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-white flex justify-center font-sans">
            <div className="w-full max-w-[1000px] grid md:grid-cols-2 lg:grid-cols-[1fr_450px] gap-8 md:gap-16 pt-12 md:pt-24 px-6 md:px-8">

                {/* Left Side: Summary and Header */}
                <div className="flex flex-col">
                    {/* Header */}
                    <div className="flex items-center gap-3 mb-10 text-sm font-medium text-slate-700">
                        <button className="text-slate-400 hover:text-slate-600 transition-colors" onClick={() => window.history.back()}>
                            <ArrowLeft className="w-5 h-5" />
                        </button>
                        <div className="w-7 h-7 bg-slate-100 rounded flex items-center justify-center">
                            <Box className="w-4 h-4 text-slate-600" />
                        </div>
                        <span>Sandbox 3</span>
                        <div className="flex items-center gap-1.5 bg-[#1C253B] text-white px-2.5 py-1 rounded text-xs tracking-wide">
                            <Box className="w-3 h-3 text-white/80" />
                            Sandbox
                        </div>
                    </div>

                    {/* Price Display */}
                    <div>
                        <p className="text-slate-500 text-base mb-1">Payment</p>
                        <h1 className="text-[40px] font-semibold text-slate-900 tracking-tight leading-none">
                            ₹25,000.00
                        </h1>
                    </div>
                </div>

                {/* Right Side: Payment Form */}
                <div className="flex flex-col space-y-6 pt-1 md:pt-14 pb-12">
                    {/* Contact Information */}
                    <div className="space-y-3">
                        <h3 className="text-lg font-medium text-slate-800">Contact information</h3>
                        <div className="space-y-1.5">
                            <label className="text-sm text-slate-600">Email</label>
                            <Input
                                defaultValue="shaivyaasharma04@gmail.com"
                                className="h-11 rounded-md border-slate-300 shadow-sm focus-visible:ring-1 focus-visible:ring-[#0070F3] bg-[#FEFCE8]"
                            />
                        </div>
                    </div>

                    {/* Payment Method */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-medium text-slate-800">Payment method</h3>

                        {/* Card Info Box */}
                        <div className="space-y-1.5">
                            <label className="text-sm text-slate-600">Card information</label>
                            <div className="rounded-md border border-slate-300 shadow-sm bg-white overflow-hidden focus-within:ring-1 focus-within:ring-[#0070F3] focus-within:border-[#0070F3]">
                                {/* Card Number Row */}
                                <div className="border-b border-slate-200 relative flex items-center">
                                    <input
                                        type="text"
                                        placeholder="1234 5678 1234 5678"
                                        defaultValue="4242 4242 4242 4242"
                                        className="w-full h-11 px-3 text-[15px] outline-none placeholder:text-slate-400"
                                    />
                                    <div className="absolute right-3">
                                        <svg className="h-4" viewBox="0 0 32 21" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="32" height="20.5714" rx="3" fill="#1434CB" /><path d="M12.9855 13.9161L14.7709 3.52042H17.5756L15.7901 13.9161H12.9855ZM23.3676 3.7915C22.8427 3.59714 21.9312 3.40723 20.893 3.40723C18.1566 3.40723 16.2731 4.75704 16.2554 6.83296C16.2372 8.35637 17.6892 9.20816 18.7845 9.70477C19.9126 10.2157 20.2917 10.5372 20.2863 11.0289C20.2804 11.7766 19.3175 12.107 18.3315 12.107C17.0652 12.107 16.2894 11.8016 15.6865 11.5369L15.3188 11.3712L14.9606 13.447C15.6517 13.7441 16.8924 14.0205 18.1979 14.0205C21.1091 14.0205 22.9669 12.6859 22.9897 10.4632C23.0079 9.2452 22.2575 8.32483 18.8687 6.78652C17.8447 6.32684 17.2003 6.00843 17.2144 5.4384C17.2144 4.77013 18.0197 4.14856 19.4674 4.14856C20.536 4.13524 21.3204 4.35414 21.9427 4.6062L22.2519 4.74313L23.3676 3.7915ZM30.413 13.9161C30.413 13.9161 28.5283 8.39763 28.23 7.29145C27.9719 6.37761 27.671 5.91893 27.0505 5.91893H23.5186L23.4419 6.25785C24.4996 6.50549 25.4363 6.94634 26.2625 7.5142L25.9616 6.27063H25.9529L22.9669 13.9161H25.8659L26.4476 12.3831H30.0177L29.982 12.5694L30.413 13.9161ZM27.2797 10.2319H29.1306L28.214 6.8988C28.214 6.8988 28.1691 6.89069 28.1408 6.99407L27.2797 10.2319ZM11.9661 13.9161L9.043 4.10307C8.94857 3.73173 8.87702 3.63931 8.57213 3.52042C7.75624 3.2081 6.38601 2.94672 5.37893 2.76636L5.45268 3.09063C6.39054 3.30873 7.42629 3.68452 8.01026 4.02027C8.28181 4.17835 8.36838 4.38138 8.44169 4.6851L10.963 13.9161H11.9661Z" fill="white" /></svg>
                                    </div>
                                </div>
                                {/* Expiry and CVC Row */}
                                <div className="grid grid-cols-2">
                                    <div className="border-r border-slate-200">
                                        <input
                                            type="text"
                                            placeholder="MM / YY"
                                            className="w-full h-11 px-3 text-[15px] outline-none placeholder:text-slate-400"
                                        />
                                    </div>
                                    <div className="relative flex items-center">
                                        <input
                                            type="text"
                                            placeholder="CVC"
                                            className="w-full h-11 px-3 text-[15px] outline-none placeholder:text-slate-400"
                                        />
                                        <div className="absolute right-3">
                                            <svg className="w-5 h-5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="5" width="20" height="14" rx="2" /><line x1="2" y1="10" x2="22" y2="10" /></svg>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Cardholder Name */}
                        <div className="space-y-1.5">
                            <label className="text-sm text-slate-600">Cardholder name</label>
                            <Input
                                placeholder="Full name on card"
                                className="h-11 rounded-md border-slate-300 shadow-sm focus-visible:ring-1 focus-visible:ring-[#0070F3]"
                            />
                        </div>

                        {/* Country */}
                        <div className="space-y-1.5">
                            <label className="text-sm text-slate-600">Country or region</label>
                            <select className="flex h-11 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#0070F3] placeholder:text-slate-500 disabled:cursor-not-allowed disabled:opacity-50 appearance-none">
                                <option>India</option>
                                <option>United States</option>
                                <option>United Kingdom</option>
                                <option>Australia</option>
                            </select>
                            {/* Custom arrow for select */}
                            <div className="relative">
                                <svg className="absolute right-3 -top-8 w-4 h-4 text-slate-500 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                            </div>
                        </div>

                    </div>

                    {/* Pay Button */}
                    <div className="pt-2">
                        <Button
                            onClick={handlePay}
                            className="w-full h-11 bg-[#0070F3] hover:bg-[#0060d3] text-white font-medium text-[15px] rounded-md transition-colors"
                        >
                            Pay
                        </Button>
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-center gap-2 pt-2 text-[13px] text-slate-500">
                        <span>Powered by <span className="font-bold text-slate-600">stripe</span></span>
                        <span className="text-slate-300">|</span>
                        <button className="hover:text-slate-800 transition-colors">Terms</button>
                        <button className="hover:text-slate-800 transition-colors">Privacy</button>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default MockCheckoutPage;
