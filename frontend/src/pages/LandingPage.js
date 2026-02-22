import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Leaf, Brain, Heart, Stethoscope, Award, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';

const LandingPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-nav border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-3" data-testid="logo-link">
              <img src="/home-logo.svg" alt="TTI Logo" className="h-12 w-auto" />
              <div>
                <span className="font-playfair font-semibold text-mindful-800 text-lg tracking-tight">
                  Trauma Transformation Institute
                </span>
                <span className="block text-xs text-sage-600 font-dm-sans">ETT India</span>
              </div>
            </Link>
            
            <div className="flex items-center gap-6">
              <Link 
                to="/about" 
                className="text-sm font-dm-sans text-navy-600 hover:text-navy-900 transition-colors"
                data-testid="about-link"
              >
                About
              </Link>
              {user ? (
                <Link to="/dashboard">
                  <Button 
                    variant="outline" 
                    className="font-dm-sans border-navy-900 text-navy-900 hover:bg-navy-900 hover:text-white"
                    data-testid="dashboard-btn"
                  >
                    Dashboard
                  </Button>
                </Link>
              ) : (
                <Link to="/login">
                  <Button 
                    variant="outline" 
                    className="font-dm-sans border-navy-900 text-navy-900 hover:bg-navy-900 hover:text-white"
                    data-testid="login-btn"
                  >
                    Sign In
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-16 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-navy-50 border border-navy-100 mb-8">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm font-dm-sans text-navy-600">Programs Open - Applications Welcome</span>
            </div>
            
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-playfair font-bold text-navy-900 tracking-tight leading-tight mb-6">
              Choose Your Path
            </h1>
            
            <p className="text-lg md:text-xl font-dm-sans text-navy-500 max-w-2xl mx-auto leading-relaxed">
              Transform lives through Emotional Transformation Therapy. Select your journey—Wellness for personal growth or Clinical for professional mastery.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Path Selection Cards */}
      <section className="px-6 pb-24">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Wellness Track Card */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              whileHover={{ y: -4 }}
              className="group"
            >
              <div 
                className="bg-white rounded-lg border border-slate-200 p-8 md:p-10 shadow-card hover:shadow-card-hover transition-all duration-500 cursor-pointer h-full flex flex-col"
                onClick={() => navigate('/wellness')}
                data-testid="wellness-track-card"
              >
                <div className="mb-6">
                  <span className="inline-block px-3 py-1 text-xs font-dm-sans font-semibold tracking-wider uppercase bg-sky/10 text-sky rounded-full">
                    Wellness Track
                  </span>
                </div>
                
                <h2 className="text-3xl font-playfair font-semibold text-navy-900 mb-4">
                  ETT Wellness Model
                </h2>
                
                <p className="text-navy-500 font-dm-sans mb-8 leading-relaxed">
                  Foundations of ETT for wellness professionals and personal seekers
                </p>
                
                <div className="space-y-4 flex-grow">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                      <Leaf className="w-4 h-4 text-emerald-600" />
                    </div>
                    <span className="text-navy-600 font-dm-sans text-sm leading-relaxed">
                      Level 1: Emotional regulation & stress reduction
                    </span>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                      <Heart className="w-4 h-4 text-purple-600" />
                    </div>
                    <span className="text-navy-600 font-dm-sans text-sm leading-relaxed">
                      Somatic healing & spiritual wellness pathways
                    </span>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
                      <Brain className="w-4 h-4 text-amber-600" />
                    </div>
                    <span className="text-navy-600 font-dm-sans text-sm leading-relaxed">
                      Self-paced personal transformation
                    </span>
                  </div>
                </div>
                
                <Button 
                  className="mt-8 w-full bg-sky hover:bg-sky/90 text-white font-dm-sans font-medium py-6 rounded-sm group-hover:translate-x-0 transition-all"
                  data-testid="explore-wellness-btn"
                >
                  Explore Wellness Track
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </div>
            </motion.div>

            {/* Clinical Track Card */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              whileHover={{ y: -4 }}
              className="group"
            >
              <div 
                className="bg-white rounded-lg border border-slate-200 p-8 md:p-10 shadow-card hover:shadow-card-hover transition-all duration-500 cursor-pointer h-full flex flex-col"
                onClick={() => navigate('/clinical')}
                data-testid="clinical-track-card"
              >
                <div className="mb-6">
                  <span className="inline-block px-3 py-1 text-xs font-dm-sans font-semibold tracking-wider uppercase bg-navy-100 text-navy-700 rounded-full">
                    Clinical Track
                  </span>
                </div>
                
                <h2 className="text-3xl font-playfair font-semibold text-navy-900 mb-4">
                  ETT Clinical Model
                </h2>
                
                <p className="text-navy-500 font-dm-sans mb-8 leading-relaxed">
                  Advanced training for licensed mental health professionals
                </p>
                
                <div className="space-y-4 flex-grow">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <Stethoscope className="w-4 h-4 text-blue-600" />
                    </div>
                    <span className="text-navy-600 font-dm-sans text-sm leading-relaxed">
                      Level 1-2: Core ETT techniques & attachment work
                    </span>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-rose-100 flex items-center justify-center flex-shrink-0">
                      <BookOpen className="w-4 h-4 text-rose-600" />
                    </div>
                    <span className="text-navy-600 font-dm-sans text-sm leading-relaxed">
                      Advanced: Somatic applications & spiritual integration
                    </span>
                  </div>
                  
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-teal-100 flex items-center justify-center flex-shrink-0">
                      <Award className="w-4 h-4 text-teal-600" />
                    </div>
                    <span className="text-navy-600 font-dm-sans text-sm leading-relaxed">
                      Certification for clinical practice
                    </span>
                  </div>
                </div>
                
                <Button 
                  className="mt-8 w-full bg-navy-900 hover:bg-navy-800 text-white font-dm-sans font-medium py-6 rounded-sm group-hover:translate-x-0 transition-all"
                  data-testid="explore-clinical-btn"
                >
                  Explore Clinical Track
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-100 py-12 px-6 bg-navy-50/50">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-navy-900 rounded-sm flex items-center justify-center">
                <span className="text-white font-playfair font-bold text-sm">T</span>
              </div>
              <span className="font-dm-sans text-sm text-navy-600">
                Trauma Transformation Institute - ETT India
              </span>
            </div>
            
            <div className="flex items-center gap-6 text-sm font-dm-sans text-navy-500">
              <Link to="/about" className="hover:text-navy-900 transition-colors">About</Link>
              <a href="mailto:contact@tti-india.com" className="hover:text-navy-900 transition-colors">Contact</a>
              <span>© 2025 TTI India</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
