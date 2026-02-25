import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';
import { LogOut } from 'lucide-react';
import { toast } from 'sonner';

const Navbar = () => {
    const { user, logout } = useAuth();

    const handleLogout = () => {
        logout();
        toast.success('Signed out successfully');
    };

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 glass-nav border-b border-slate-100 bg-white/80 backdrop-blur-md">
            <div className="max-w-7xl mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-6">
                        <Link to="/" className="flex items-center gap-3">
                            <img src="/brain-logo.png" alt="Logo" className="w-8 h-8 object-contain" />
                            <span className="font-playfair font-semibold text-navy-900 hidden sm:inline text-lg tracking-tight">
                                TraumaTransformationInstitute
                            </span>
                        </Link>
                    </div>

                    <div className="flex items-center gap-4">
                        <Link
                            to="/about"
                            className="text-sm font-dm-sans font-medium px-4 py-2 text-navy-700 hover:text-navy-900 transition-colors"
                        >
                            About Us
                        </Link>

                        {user ? (
                            <div className="flex items-center gap-4">
                                <Link to="/dashboard">
                                    <Button variant="outline" className="font-dm-sans border-navy-900 text-navy-900 hover:bg-navy-900 hover:text-white" data-testid="dashboard-btn">
                                        Dashboard
                                    </Button>
                                </Link>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={handleLogout}
                                    className="font-dm-sans text-navy-600 hover:text-navy-900"
                                >
                                    <LogOut className="w-4 h-4 mr-2" />
                                    Sign Out
                                </Button>
                            </div>
                        ) : (
                            <Link to="/login">
                                <Button variant="outline" className="font-dm-sans border-navy-900 text-navy-900 hover:bg-navy-900 hover:text-white" data-testid="login-btn">
                                    Sign In
                                </Button>
                            </Link>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
