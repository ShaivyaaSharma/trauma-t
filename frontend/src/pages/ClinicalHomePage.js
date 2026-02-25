import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Calendar, MapPin, Clock, Users, Lock, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL || ''}/api`;

const ClinicalHomePage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await axios.get(`${API}/courses?track=clinical`);
        const sortedCourses = response.data.sort((a, b) => {
          if (a.is_coming_soon === b.is_coming_soon) return 0;
          return a.is_coming_soon ? 1 : -1;
        });
        setCourses(sortedCourses);
      } catch (error) {
        console.error('Error fetching courses:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchCourses();
  }, []);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price);
  };

  return (
    <div className="min-h-screen bg-white">

      {/* Hero */}
      <section className="pt-28 pb-12 px-6 bg-gradient-to-b from-navy-50 to-white">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Badge className="mb-4 bg-navy-100 text-navy-700 hover:bg-navy-200 font-dm-sans">
              Clinical Track
            </Badge>
            <h1 className="text-4xl md:text-5xl font-playfair font-bold text-navy-900 mb-4">
              ETT Clinical Programs
            </h1>
            <p className="text-lg font-dm-sans text-navy-500 max-w-2xl">
              Advanced training for licensed mental health professionals. Includes DSM-5 integration, trauma protocols, and clinical certification.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Courses Grid */}
      <section className="px-6 pb-24">
        <div className="max-w-6xl mx-auto">
          {loading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {courses.map((course, index) => (
                <motion.div
                  key={course.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                >
                  <Card
                    className={`h-full border-slate-200 shadow-card hover:shadow-card-hover transition-all duration-500 cursor-pointer group ${course.is_coming_soon ? 'opacity-75' : ''}`}
                    onClick={() => !course.is_coming_soon && navigate(`/courses/${course.id}`)}
                    data-testid={`course-card-${course.id}`}
                  >
                    <CardContent className="p-6 flex flex-col h-full">
                      <div className="flex items-start justify-between mb-4">
                        <Badge
                          variant="outline"
                          className="font-dm-sans text-xs capitalize border-navy-300 text-navy-600"
                        >
                          {course.level}
                        </Badge>
                        {course.is_coming_soon && (
                          <Badge className="bg-slate-100 text-slate-600 font-dm-sans">
                            <Lock className="w-3 h-3 mr-1" />
                            Coming Soon
                          </Badge>
                        )}
                      </div>

                      <h3 className="text-xl font-playfair font-semibold text-navy-900 mb-2 group-hover:text-navy-700 transition-colors">
                        {course.title}
                      </h3>

                      <p className="text-sm font-dm-sans text-navy-500 mb-4 flex-grow">
                        {course.description}
                      </p>

                      <div className="space-y-2 text-sm font-dm-sans text-navy-400 mb-4">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4" />
                          <span>{course.schedule}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4" />
                          <span>{course.location}</span>
                        </div>
                      </div>

                      <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                        <div>
                          <span className="text-2xl font-playfair font-bold text-navy-900">
                            {formatPrice(course.price)}
                          </span>
                          {course.equipment_fee > 0 && (
                            <span className="block text-xs font-dm-sans text-navy-400">
                              + {formatPrice(course.equipment_fee)} equipment
                            </span>
                          )}
                        </div>
                        {!course.is_coming_soon && (
                          <Button
                            size="sm"
                            className="bg-navy-900 hover:bg-navy-800 font-dm-sans"
                            data-testid={`view-course-${course.id}`}
                          >
                            View
                            <ArrowRight className="w-3 h-3 ml-1" />
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </section>


    </div>
  );
};

export default ClinicalHomePage;
