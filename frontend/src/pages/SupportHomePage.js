import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Calendar, MapPin, Lock, ArrowRight, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SupportHomePage = () => {
    const navigate = useNavigate();
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCourses = async () => {
            try {
                const response = await axios.get(`${API}/courses?track=support`);
                setCourses(response.data);
            } catch (error) {
                console.error('Error fetching support courses:', error);
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
            <section className="pt-28 pb-12 px-6 bg-gradient-to-b from-amber-50 to-white">
                <div className="max-w-6xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <Badge className="mb-4 bg-amber-100 text-amber-700 hover:bg-amber-200 font-dm-sans border-none">
                            Support Track
                        </Badge>
                        <h1 className="text-4xl md:text-5xl font-playfair font-bold text-navy-900 mb-4">
                            Trauma Support Programs
                        </h1>
                        <p className="text-lg font-dm-sans text-navy-500 max-w-2xl">
                            Empowering community leaders, teachers, and caregivers with trauma awareness and essential support tools.
                        </p>
                    </motion.div>

                    <div className="mt-12">
                        {loading ? (
                            <div className="flex justify-center py-12">
                                <Loader2 className="w-8 h-8 text-amber-500 animate-spin" />
                            </div>
                        ) : courses.length === 0 ? (
                            <div className="text-center py-12">
                                <p className="text-navy-500">No support courses available yet.</p>
                            </div>
                        ) : (
                            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                                {courses.map((course) => (
                                    <motion.div
                                        key={course.id}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                    >
                                        <Card
                                            className={`h-full border-slate-200 shadow-card hover:shadow-card-hover transition-all duration-500 cursor-pointer group ${course.is_coming_soon ? 'opacity-75' : ''}`}
                                            onClick={() => !course.is_coming_soon && navigate(`/courses/${course.id}`)}
                                        >
                                            <CardContent className="p-6 flex flex-col h-full">
                                                <div className="flex items-start justify-between mb-4">
                                                    <Badge variant="outline" className="font-dm-sans text-xs capitalize border-amber-200 text-amber-700">
                                                        {course.level}
                                                    </Badge>
                                                    {course.is_coming_soon && (
                                                        <Badge className="bg-slate-100 text-slate-600 font-dm-sans">
                                                            <Lock className="w-3 h-3 mr-1" />
                                                            Coming Soon
                                                        </Badge>
                                                    )}
                                                </div>

                                                <h3 className="text-xl font-playfair font-semibold text-navy-900 mb-2 group-hover:text-amber-600 transition-colors">
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
                                                    </div>
                                                    {!course.is_coming_soon && (
                                                        <Button size="sm" className="bg-amber-500 hover:bg-amber-600 text-white font-dm-sans">
                                                            View <ArrowRight className="w-3 h-3 ml-1" />
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
                </div>
            </section>
        </div>
    );
};

export default SupportHomePage;
