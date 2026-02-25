import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

const BackButton = () => {
    const navigate = useNavigate();
    const location = useLocation();

    if (location.pathname === '/') return null;

    return (
        <Button
            size="sm"
            onClick={() => navigate(-1)}
            className="fixed top-24 left-6 z-40 bg-white/90 backdrop-blur-sm border border-slate-200 shadow-sm hover:bg-navy-50 hover:text-navy-900 text-navy-600 rounded-full px-4 transition-all duration-200"
        >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
        </Button>
    );
};

export default BackButton;
