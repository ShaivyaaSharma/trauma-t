import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Award, Users, BookOpen, Heart, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';

const certifications = [
  { short: "CCTSI", full: "Certified Clinical Trauma Specialist – Individual" },
  { short: "CCTSF", full: "Certified Clinical Trauma Specialist – Family" },
  { short: "CCTSA", full: "Certified Clinical Trauma Specialist – Addiction" },
  { short: "CTSS", full: "Certified Trauma Support Specialist" },
  { short: "ACCTS", full: "Advanced Certified Clinical Trauma Specialist" },
  { short: "CRP", full: "Certified Resilience Professional" },
  { short: "CCTS-P", full: "Certified Clinical Trauma Specialist – Prenatal" }
];

const benefits = [
  { title: "Professional Recognition", desc: "Use the certification designation on your credentials." },
  { title: "Expertise", desc: "Demonstrate your ambitious dedication to excellence in trauma service." },
  { title: "Community", desc: "Join a world-wide network of caring peers for support." },
  { title: "Knowledge", desc: "Stay informed of current developments in trauma care." },
  { title: "Support", desc: "Access peer coaching through Arizona Trauma Institute." }
];

const AboutPage = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-white">

      {/* Hero */}
      <section className="pt-32 pb-16 px-6 bg-gradient-to-b from-teal-50 to-white">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-playfair font-bold text-navy-900 mb-6 leading-tight">
              Empowering Transformations
            </h1>
            <p className="text-lg md:text-xl font-dm-sans text-navy-600 leading-relaxed max-w-3xl mx-auto">
              Trauma Institute International is the premier organization for certification in trauma treatment and transformative care. We provide certifications in accord with the standards accepted by the international trauma treating community. Our goal is to equip professionals with the essential information and skills to help trauma survivors recover fully.
            </p>
          </motion.div>
        </div>
      </section>

      {/* About Us & Mission */}
      <section className="px-6 py-16 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl font-playfair font-bold text-navy-900 mb-6 relative">
                <span className="relative z-10">About Us</span>
                <span className="absolute bottom-1 left-0 w-16 h-3 bg-teal-100 -z-0"></span>
              </h2>
              <p className="font-dm-sans text-navy-600 leading-relaxed mb-8 text-lg">
                Trauma Institute International is a leading provider of trauma education and certification. We are dedicated to helping professionals and organizations improve their capacity to support individuals affected by trauma.
              </p>

              <h2 className="text-3xl font-playfair font-bold text-navy-900 mb-6 relative">
                <span className="relative z-10">Our Mission</span>
                <span className="absolute bottom-1 left-0 w-24 h-3 bg-blue-100 -z-0"></span>
              </h2>
              <p className="font-dm-sans text-navy-600 leading-relaxed text-lg">
                To provide the highest quality trauma education and certification.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
              className="bg-navy-50 rounded-2xl p-8 lg:p-12 border border-navy-100"
            >
              <h3 className="text-2xl font-playfair font-bold text-navy-900 mb-6">Benefits of Becoming Certified</h3>
              <ul className="space-y-6">
                {benefits.map((benefit, idx) => (
                  <li key={idx} className="flex items-start gap-4">
                    <div className="w-8 h-8 rounded-full bg-teal-100 flex items-center justify-center flex-shrink-0 mt-1">
                      <CheckCircle2 className="w-5 h-5 text-teal-600" />
                    </div>
                    <div>
                      <h4 className="font-playfair font-semibold text-navy-900 text-lg">{benefit.title}</h4>
                      <p className="font-dm-sans text-navy-600">{benefit.desc}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Certifications Overview */}
      <section className="px-6 py-20 bg-slate-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-playfair font-bold text-navy-900 mb-4 tracking-tight">
              Our Certifications
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-teal-400 to-blue-500 mx-auto rounded-full"></div>
            <p className="mt-6 text-navy-600 font-dm-sans max-w-2xl mx-auto text-lg">
              Comprehensive certification pathways designed for different specialties in trauma care and support.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {certifications.map((cert, index) => (
              <motion.div
                key={cert.short}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.05 }}
                viewport={{ once: true }}
              >
                <Card className="h-full border-slate-200 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300 bg-white">
                  <CardContent className="p-6 flex flex-col items-center text-center h-full">
                    <div className="w-20 h-20 shrink-0 rounded-full bg-blue-50 flex items-center justify-center mb-4 border border-blue-100">
                      <span className="font-playfair font-bold text-blue-700 text-lg whitespace-nowrap tracking-tight">{cert.short}</span>
                    </div>
                    <p className="font-dm-sans font-medium text-navy-800 leading-snug">
                      {cert.full}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Target Tracks / CTA */}
      <section className="px-6 py-24 bg-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-playfair font-bold text-navy-900 mb-6">
            Ready to Begin Your Journey?
          </h2>
          <p className="font-dm-sans text-navy-600 mb-10 text-lg md:text-xl leading-relaxed">
            Choose the path that best fits your goals. Our <span className="text-teal-600 font-semibold">Wellness Track</span> is perfect for personal growth and holistic seekers, while our <span className="text-blue-700 font-semibold">Clinical Track</span> provides advanced training for licensed mental health professionals. We have the right certification for your journey.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Link to="/wellness">
              <Button className="w-full sm:w-auto bg-gradient-to-r from-teal-500 to-blue-500 hover:from-teal-600 hover:to-blue-600 font-dm-sans px-10 py-7 text-lg font-semibold text-white shadow-lg rounded-xl transition-transform hover:-translate-y-1">
                Explore Wellness Track
              </Button>
            </Link>
            <Link to="/clinical">
              <Button className="w-full sm:w-auto bg-navy-900 hover:bg-navy-800 font-dm-sans px-10 py-7 text-lg font-semibold text-white shadow-lg rounded-xl transition-transform hover:-translate-y-1">
                Explore Clinical Track
              </Button>
            </Link>
          </div>
        </div>
      </section>


    </div>
  );
};

export default AboutPage;
