import { Link } from 'react-router-dom';

const Footer = () => {
    return (
        <footer className="border-t border-slate-100 py-12 px-6 bg-navy-50/50 mt-auto">
            <div className="max-w-6xl mx-auto flex flex-col gap-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
                    {/* Left: Logo */}
                    <div className="flex items-start gap-3">
                        <img src="/brain-logo.png" alt="Logo" className="w-8 h-8 object-contain" />
                        <span className="font-dm-sans text-base font-medium text-navy-600 mt-1">
                            TraumaTransformationInstitute
                        </span>
                    </div>

                    {/* Center: Links & Contact */}
                    <div className="flex md:justify-center">
                        <div className="flex flex-col items-start gap-4 text-base md:text-md font-dm-sans text-navy-500">
                            <Link to="/about" className="hover:text-navy-900 transition-colors">About Us</Link>
                            <a href="mailto:ssidhu@lightmindsett.com" className="hover:text-navy-900 transition-colors">E: ssidhu@lightmindsett.com</a>
                            <a href="tel:972-336-1591" className="hover:text-navy-900 transition-colors">P: 972-336-1591</a>
                        </div>
                    </div>

                    {/* Right space filler to keep center perfectly centered */}
                    <div className="hidden md:block"></div>
                </div>

                {/* Bottom Right: Copyright */}
                <div className="pt-6 border-t border-slate-200/60 flex flex-col md:flex-row justify-center md:justify-end">
                    <span className="text-sm font-dm-sans text-navy-500">
                        © 2026 TraumaTransformationInstitute
                    </span>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
