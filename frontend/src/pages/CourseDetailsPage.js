import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Calendar, MapPin, Users, Check, CreditCard, ChevronDown, ChevronUp, BookOpen, Clock, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL || ''}/api`;

const CourseDetailsPage = () => {
  const { courseId } = useParams();
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [expandedModules, setExpandedModules] = useState({});
  const [isEnrolled, setIsEnrolled] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const requests = [
          axios.get(`${API}/courses/${courseId}`),
          axios.get(`${API}/courses/${courseId}/curriculum`),
        ];
        // Only fetch enrollments if the user is logged in
        if (token) {
          requests.push(
            axios.get(`${API}/enrollments/my`, {
              headers: { Authorization: `Bearer ${token}` }
            })
          );
        }

        const [courseRes, modulesRes, enrollmentsRes] = await Promise.all(requests);
        setCourse(courseRes.data);
        setModules(modulesRes.data.sort((a, b) => a.module_number - b.module_number));

        if (enrollmentsRes) {
          const enrolled = enrollmentsRes.data.some(
            (e) => e.enrollment?.course_id === courseId || e.course_id === courseId
          );
          setIsEnrolled(enrolled);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        toast.error('Course not found');
        navigate('/');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [courseId, navigate, token]);

  const toggleModule = (id) => {
    setExpandedModules(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price);
  };

  const handleEnroll = async () => {
    if (!user) {
      toast.info('Please sign in to enroll');
      navigate('/login', { state: { from: `/courses/${courseId}` } });
      return;
    }

    try {
      setEnrolling(true);
      const origin = window.location.origin; // e.g. http://localhost:3000
      const res = await axios.post(
        `${API}/enrollments/checkout`,
        { course_id: courseId, origin_url: origin },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Redirect to Stripe Checkout hosted page
      window.location.href = res.data.checkout_url;
    } catch (err) {
      const msg = err.response?.data?.detail || 'Could not initiate checkout. Please try again.';
      toast.error(msg);
      setEnrolling(false);
    }
  };



  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!course) {
    return null;
  }

  const totalPrice = course.price + (course.equipment_fee || 0);
  const isWellness = course.track === 'wellness' || course.track === 'both';

  return (
    <div className="min-h-screen bg-white">
      {/* Back Header */}
      <div className="fixed top-0 left-0 right-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-100 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Button variant="ghost" className="gap-2" onClick={() => navigate(-1)}>
            <ArrowLeft className="w-4 h-4" />
            Back to Programs
          </Button>
          <div className="hidden md:flex items-center gap-4">
            <span className="text-sm font-dm-sans text-navy-500">{course.title}</span>
            <Separator orientation="vertical" className="h-4" />
            <span className="text-sm font-dm-sans font-bold text-navy-900">{formatPrice(course.price)}</span>
          </div>
        </div>
      </div>

      {/* Hero Content */}
      <div className="pt-28 pb-20 px-6 bg-gradient-to-b from-slate-50 to-white">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-3 gap-12">
            {/* Main Content */}
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Badge className={`mb-4 ${isWellness ? 'bg-teal-100 text-teal-700' : 'bg-blue-100 text-blue-700'} border-none uppercase tracking-wider text-[10px]`}>
                  {course.track} Path - {course.level}
                </Badge>

                <h1 className="text-4xl md:text-5xl font-playfair font-bold text-navy-900 mb-6">
                  {course.title}
                </h1>

                <p className="text-lg font-dm-sans text-navy-600 mb-10 leading-relaxed">
                  {course.detailed_description || course.description}
                </p>

                <div className="grid sm:grid-cols-3 gap-6 mb-12">
                  <div className="flex flex-col gap-1">
                    <span className="text-xs font-dm-sans text-navy-400 uppercase tracking-widest">Schedule</span>
                    <div className="flex items-center gap-2 text-navy-900 font-medium font-dm-sans">
                      <Calendar className="w-4 h-4 text-navy-400" />
                      {course.schedule}
                    </div>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-xs font-dm-sans text-navy-400 uppercase tracking-widest">Location</span>
                    <div className="flex items-center gap-2 text-navy-900 font-medium font-dm-sans">
                      <MapPin className="w-4 h-4 text-navy-400" />
                      {course.location}
                    </div>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-xs font-dm-sans text-navy-400 uppercase tracking-widest">Instructor</span>
                    <div className="flex items-center gap-2 text-navy-900 font-medium font-dm-sans">
                      <Users className="w-4 h-4 text-navy-400" />
                      {course.instructor}
                    </div>
                  </div>
                </div>

                <div className="space-y-12">
                  {/* Features / Objectives */}
                  <section>
                    <h2 className="text-2xl font-playfair font-bold text-navy-900 mb-6 underline decoration-teal-200 underline-offset-8">
                      Program Curriculum Overview
                    </h2>
                    <div className="grid sm:grid-cols-2 gap-x-8 gap-y-4">
                      {course.features?.map((feature, idx) => (
                        <div key={idx} className="flex items-start gap-4">
                          <Check className="w-5 h-5 text-teal-500 mt-0.5 flex-shrink-0" />
                          <span className="text-navy-700 font-dm-sans">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </section>

                  {/* Modules Accordion */}
                  <section>
                    <h2 className="text-2xl font-playfair font-bold text-navy-900 mb-6 underline decoration-blue-200 underline-offset-8">
                      Module Breakdown
                    </h2>
                    <div className="space-y-4">
                      {modules.map((mod) => (
                        <Card key={mod.id} className="border-slate-100 overflow-hidden shadow-sm">
                          <button
                            onClick={() => toggleModule(mod.id)}
                            className="w-full text-left p-5 flex items-center justify-between hover:bg-slate-50 transition-colors"
                          >
                            <div className="flex items-center gap-4">
                              <span className="w-8 h-8 rounded-full bg-navy-900 text-white flex items-center justify-center text-xs font-bold">
                                {mod.module_number}
                              </span>
                              <div>
                                <h3 className="font-playfair font-bold text-navy-900">{mod.title}</h3>
                                <div className="flex items-center gap-3 text-xs text-navy-400 mt-1 font-dm-sans">
                                  <span className="flex items-center gap-1">
                                    <Clock className="w-3 h-3" /> {mod.estimated_time || '4 hours'}
                                  </span>
                                  <span>•</span>
                                  <span>{mod.topics_covered?.length || 0} topics included</span>
                                </div>
                              </div>
                            </div>
                            {expandedModules[mod.id] ? <ChevronUp className="w-5 h-5 text-navy-400" /> : <ChevronDown className="w-5 h-5 text-navy-400" />}
                          </button>

                          {expandedModules[mod.id] && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: "auto", opacity: 1 }}
                              className="p-5 pt-0 border-t border-slate-50"
                            >
                              <div className="pt-4 space-y-4">
                                <p className="text-sm text-navy-600 font-dm-sans leading-relaxed italic">
                                  {mod.description}
                                </p>

                                <div className="grid md:grid-cols-2 gap-6">
                                  <div>
                                    <h4 className="text-xs font-bold uppercase tracking-widest text-navy-400 mb-3">Key Topics</h4>
                                    <ul className="space-y-2">
                                      {mod.topics_covered?.map((topic, i) => (
                                        <li key={i} className="text-sm text-navy-700 flex items-center gap-2">
                                          <div className="w-1.5 h-1.5 rounded-full bg-blue-300" />
                                          {topic}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                  <div>
                                    <h4 className="text-xs font-bold uppercase tracking-widest text-navy-400 mb-3">Activities</h4>
                                    <ul className="space-y-2">
                                      {mod.student_activities?.map((activity, i) => (
                                        <li key={i} className="text-sm text-navy-700 flex items-center gap-2">
                                          <BookOpen className="w-3.5 h-3.5 text-teal-500" />
                                          {activity}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </Card>
                      ))}
                    </div>
                  </section>
                </div>
              </motion.div>
            </div>

            {/* Sidebar - Enrollment Card */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Card className="sticky top-28 border-slate-200 shadow-xl overflow-hidden group">
                <div className={`h-2 ${isWellness ? 'bg-teal-500' : 'bg-blue-600'}`} />
                <CardContent className="p-8">
                  <div className="mb-8">
                    <p className="text-xs font-bold uppercase tracking-widest text-navy-400 mb-2">Program Investment</p>
                    <div className="flex items-baseline gap-2">
                      <span className="text-4xl font-playfair font-bold text-navy-900">{formatPrice(course.price)}</span>
                      {course.equipment_fee > 0 && <span className="text-xs text-navy-400 font-dm-sans">+ fees</span>}
                    </div>
                  </div>

                  <div className="space-y-4 mb-8 text-sm font-dm-sans text-navy-600">
                    <div className="flex justify-between items-center">
                      <span>Certification Track</span>
                      <span className="text-navy-900 font-medium capitalize">{course.level}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Duration</span>
                      <span className="text-navy-900 font-medium">{course.duration}</span>
                    </div>
                    {course.equipment_fee > 0 && (
                      <div className="flex justify-between items-center">
                        <span>Equipment Fee</span>
                        <span className="text-navy-900 font-medium">{formatPrice(course.equipment_fee)}</span>
                      </div>
                    )}
                    <Separator />
                    <div className="flex justify-between items-center text-lg font-bold text-navy-900">
                      <span>Total Due</span>
                      <span>{formatPrice(totalPrice)}</span>
                    </div>
                  </div>

                  {isEnrolled ? (
                    <div className="space-y-3">
                      {/* Already enrolled banner */}
                      <div className="flex items-center gap-3 bg-emerald-50 border border-emerald-200 rounded-xl px-5 py-4">
                        <CheckCircle2 className="w-6 h-6 text-emerald-600 flex-shrink-0" />
                        <div>
                          <p className="font-dm-sans font-bold text-emerald-800 text-sm">Already Enrolled</p>
                          <p className="text-xs text-emerald-600 font-dm-sans">You have access to this course</p>
                        </div>
                      </div>
                      {/* Go to learning */}
                      <Button
                        className="w-full py-7 font-dm-sans font-bold text-lg rounded-xl bg-navy-900 hover:bg-navy-800 text-white shadow-lg"
                        onClick={() => navigate(`/courses/${courseId}/learn`)}
                      >
                        <BookOpen className="w-5 h-5 mr-3" />
                        Continue Learning
                      </Button>
                      <Button
                        variant="outline"
                        className="w-full font-dm-sans"
                        onClick={() => navigate('/dashboard')}
                      >
                        Go to Dashboard
                      </Button>
                    </div>
                  ) : (
                    <Button
                      className={`w-full py-7 font-dm-sans font-bold text-lg rounded-xl transition-all ${isWellness
                        ? 'bg-teal-500 hover:bg-teal-600 hover:shadow-teal-100 shadow-lg'
                        : 'bg-blue-600 hover:bg-blue-700 hover:shadow-blue-100 shadow-lg'
                        } text-white`}
                      onClick={handleEnroll}
                      disabled={enrolling || course.is_coming_soon}
                    >
                      {enrolling ? (
                        <div className="flex items-center gap-2">
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                          Initializing...
                        </div>
                      ) : course.is_coming_soon ? (
                        'Registration Closed'
                      ) : (
                        <>
                          <CreditCard className="w-5 h-5 mr-3" />
                          Enroll Now
                        </>
                      )}
                    </Button>
                  )}

                  <p className="text-center text-[10px] text-navy-400 uppercase tracking-widest mt-6">
                    Secure Enrollment via Stripe Terminal
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetailsPage;
