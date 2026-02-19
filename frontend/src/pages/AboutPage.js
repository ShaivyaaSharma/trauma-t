import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Award, Users, BookOpen, Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';

const AboutPage = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-nav border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link 
                to="/" 
                className="flex items-center gap-2 text-navy-500 hover:text-navy-900 transition-colors"
                data-testid="back-home-link"
              >
                <ArrowLeft className="w-4 h-4" />
                <span className="font-dm-sans text-sm">Back</span>
              </Link>
              <div className="h-6 w-px bg-slate-200"></div>
              <Link to="/" className="flex items-center gap-3">
                <div className="w-8 h-8 bg-navy-900 rounded-sm flex items-center justify-center">
                  <span className="text-white font-playfair font-bold text-sm">T</span>
                </div>
                <span className="font-playfair font-semibold text-navy-900">TTI</span>
              </Link>
            </div>
            
            <div className="flex items-center gap-4">
              {user ? (
                <Link to="/dashboard">
                  <Button variant="outline" className="font-dm-sans" data-testid="dashboard-btn">
                    Dashboard
                  </Button>
                </Link>
              ) : (
                <Link to="/login">
                  <Button variant="outline" className="font-dm-sans" data-testid="login-btn">
                    Sign In
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-28 pb-16 px-6 bg-gradient-to-b from-navy-50 to-white">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-4xl md:text-5xl font-playfair font-bold text-navy-900 mb-6">
              About Trauma Transformation Institute
            </h1>
            <p className="text-lg font-dm-sans text-navy-500 leading-relaxed">
              Pioneering Emotional Transformation Therapy education in India, empowering wellness professionals and mental health practitioners to transform lives.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Mission */}
      <section className="px-6 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <h2 className="text-3xl font-playfair font-bold text-navy-900 mb-6">
                Our Mission
              </h2>
              <p className="font-dm-sans text-navy-600 leading-relaxed mb-4">
                The Trauma Transformation Institute (TTI) India is dedicated to bringing world-class Emotional Transformation Therapy (ETT) training to South Asia. We believe in the power of evidence-based therapeutic approaches to heal emotional wounds and transform lives.
              </p>
              <p className="font-dm-sans text-navy-600 leading-relaxed">
                Our programs combine cutting-edge neuroscience with compassionate therapeutic practice, creating a unique approach to emotional healing that respects both scientific rigor and human experience.
              </p>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="grid grid-cols-2 gap-4"
            >
              <Card className="border-slate-200 shadow-card">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 rounded-full bg-sky/10 flex items-center justify-center mx-auto mb-4">
                    <Users className="w-6 h-6 text-sky" />
                  </div>
                  <p className="text-3xl font-playfair font-bold text-navy-900 mb-1">500+</p>
                  <p className="text-sm font-dm-sans text-navy-500">Trained Practitioners</p>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200 shadow-card">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
                    <Award className="w-6 h-6 text-emerald-600" />
                  </div>
                  <p className="text-3xl font-playfair font-bold text-navy-900 mb-1">12+</p>
                  <p className="text-sm font-dm-sans text-navy-500">Years Experience</p>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200 shadow-card">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mx-auto mb-4">
                    <BookOpen className="w-6 h-6 text-purple-600" />
                  </div>
                  <p className="text-3xl font-playfair font-bold text-navy-900 mb-1">8</p>
                  <p className="text-sm font-dm-sans text-navy-500">Training Programs</p>
                </CardContent>
              </Card>
              
              <Card className="border-slate-200 shadow-card">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center mx-auto mb-4">
                    <Heart className="w-6 h-6 text-amber-600" />
                  </div>
                  <p className="text-3xl font-playfair font-bold text-navy-900 mb-1">10K+</p>
                  <p className="text-sm font-dm-sans text-navy-500">Lives Transformed</p>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="px-6 py-16 bg-navy-50/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-playfair font-bold text-navy-900 mb-12 text-center">
            Our Core Values
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: "Evidence-Based Practice",
                description: "All our training programs are grounded in neuroscience research and proven therapeutic methodologies."
              },
              {
                title: "Ethical Excellence",
                description: "We maintain the highest ethical standards with mandatory annual ethics training for all certified practitioners."
              },
              {
                title: "Compassionate Care",
                description: "We believe healing happens in relationship, and train practitioners to embody presence and empathy."
              }
            ].map((value, index) => (
              <motion.div
                key={value.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.2 + index * 0.1 }}
              >
                <Card className="h-full border-slate-200 shadow-card hover:shadow-card-hover transition-all">
                  <CardContent className="p-8">
                    <h3 className="text-xl font-playfair font-semibold text-navy-900 mb-4">
                      {value.title}
                    </h3>
                    <p className="font-dm-sans text-navy-500 leading-relaxed">
                      {value.description}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-playfair font-bold text-navy-900 mb-4">
            Ready to Begin Your Journey?
          </h2>
          <p className="font-dm-sans text-navy-500 mb-8">
            Explore our training programs and take the first step towards becoming an ETT practitioner.
          </p>
          <div className="flex gap-4 justify-center">
            <Link to="/wellness">
              <Button className="bg-sky hover:bg-sky/90 font-dm-sans px-8 py-6" data-testid="wellness-cta">
                Wellness Track
              </Button>
            </Link>
            <Link to="/clinical">
              <Button className="bg-navy-900 hover:bg-navy-800 font-dm-sans px-8 py-6" data-testid="clinical-cta">
                Clinical Track
              </Button>
            </Link>
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
              <a href="mailto:contact@tti-india.com" className="hover:text-navy-900 transition-colors">
                contact@tti-india.com
              </a>
              <span>© 2025 TTI India</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AboutPage;
