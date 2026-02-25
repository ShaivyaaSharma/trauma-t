import Navbar from './Navbar';
import Footer from './Footer';
import BackButton from './BackButton';

const Layout = ({ children }) => {
    return (
        <div className="flex flex-col min-h-screen w-full relative">
            <Navbar />
            <BackButton />
            <main className="flex-grow flex flex-col w-full relative">
                {children}
            </main>
            <Footer />
        </div>
    );
};

export default Layout;
