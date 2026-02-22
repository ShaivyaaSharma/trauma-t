import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { toast } from 'sonner';
import { 
  BookOpen, 
  Lock, 
  CheckCircle2, 
  Clock, 
  Award, 
  ArrowLeft, 
  Play,
  Target
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const CourseLearningPage = () => {
  const { courseId } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [modules, setModules] = useState([]);
  const [progress, setProgress] = useState(null);
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token || !courseId) return;
    let cancelled = false;
    const fetchData = async () => {
      try {
        setLoading(true);
        const headers = { Authorization: `Bearer ${token}` };
        
        const courseRes = await axios.get(`${API_URL}/api/courses/${courseId}`, { headers });
        if (!cancelled) setCourse(courseRes.data);
        
        const modulesRes = await axios.get(`${API_URL}/api/courses/${courseId}/modules`, { headers });
        if (!cancelled) setModules(modulesRes.data);
        
        const progressRes = await axios.get(`${API_URL}/api/courses/${courseId}/progress`, { headers });
        if (!cancelled) setProgress(progressRes.data);
      } catch (error) {
        if (!cancelled) {
          console.error('Error fetching data:', error);
          if (error.response?.status === 403) {
            toast.error('You need to enroll in this course first');
            navigate(`/courses/${courseId}`);
          } else {
            toast.error('Failed to load course content');
          }
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchData();
    return () => { cancelled = true; };
  }, [token, courseId, navigate]);

  const getModuleStatus = (module) => {
    const prog = module.progress || {};
    if (prog.is_completed) return 'completed';
    if (prog.is_unlocked) return 'unlocked';
    return 'locked';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case 'unlocked':
        return <Play className="h-5 w-5 text-blue-600" />;
      case 'locked':
        return <Lock className="h-5 w-5 text-gray-400" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 border-green-200';
      case 'unlocked':
        return 'bg-blue-50 border-blue-200';
      case 'locked':
        return 'bg-gray-50 border-gray-200';
      default:
        return 'bg-white';
    }
  };

  const groupModulesByWeek = (modules) => {
    const grouped = {};
    modules.forEach(module => {
      if (!grouped[module.week]) {
        grouped[module.week] = [];
      }
      grouped[module.week].push(module);
    });
    return grouped;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const weekGroups = groupModulesByWeek(modules);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link to="/dashboard">
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
          
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{course?.title}</h1>
              <p className="text-gray-600 mt-2">{course?.description}</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-600">Your Progress</div>
              <div className="text-3xl font-bold text-primary">
                {progress?.overall_progress?.toFixed(0)}%
              </div>
              <div className="text-sm text-gray-600 mt-1">
                {progress?.completed_modules} of {progress?.total_modules} modules
              </div>
            </div>
          </div>
          
          {/* Overall Progress Bar */}
          <div className="mt-6">
            <Progress value={progress?.overall_progress || 0} className="h-3" />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Current Module</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Module {progress?.current_module}</div>
              <p className="text-xs text-muted-foreground mt-1">
                Keep learning to unlock more
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Duration</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">~33 Hours</div>
              <p className="text-xs text-muted-foreground mt-1">
                Estimated completion time
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Certificate</CardTitle>
              <Award className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {progress?.completed_modules === progress?.total_modules ? 'Ready!' : 'In Progress'}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {progress?.completed_modules === progress?.total_modules 
                  ? 'Congratulations on completing!'
                  : 'Complete all modules to earn'}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Modules by Week */}
        {Object.keys(weekGroups).sort((a, b) => parseInt(a) - parseInt(b)).map(week => (
          <div key={week} className="mb-10">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <BookOpen className="h-6 w-6 mr-2 text-primary" />
              Week {week}
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {weekGroups[week].map(module => {
                const status = getModuleStatus(module);
                const isClickable = status !== 'locked';
                
                return (
                  <Card 
                    key={module.id} 
                    className={`transition-all duration-200 ${getStatusColor(status)} ${
                      isClickable ? 'hover:shadow-lg cursor-pointer' : 'cursor-not-allowed opacity-75'
                    }`}
                    onClick={() => isClickable && navigate(`/courses/${courseId}/modules/${module.id}`)}
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <Badge variant="outline">Module {module.module_number}</Badge>
                            {status === 'completed' && (
                              <Badge className="bg-green-600">Completed</Badge>
                            )}
                            {status === 'unlocked' && (
                              <Badge className="bg-blue-600">In Progress</Badge>
                            )}
                          </div>
                          <CardTitle className="text-xl">{module.title}</CardTitle>
                        </div>
                        {getStatusIcon(status)}
                      </div>
                      <CardDescription className="mt-2">
                        {module.description}
                      </CardDescription>
                    </CardHeader>
                    
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center text-sm text-gray-600">
                          <Clock className="h-4 w-4 mr-2" />
                          {module.estimated_time}
                        </div>
                        
                        {module.progress?.quiz_attempts > 0 && (
                          <div className="pt-3 border-t">
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-gray-600">Best Score</span>
                              <span className="font-semibold">
                                {(module.progress.best_score * 100).toFixed(0)}%
                              </span>
                            </div>
                            <Progress value={module.progress.best_score * 100} className="h-2" />
                            <div className="text-xs text-gray-500 mt-1">
                              {module.progress.quiz_attempts} attempt{module.progress.quiz_attempts !== 1 ? 's' : ''}
                            </div>
                          </div>
                        )}
                        
                        {status === 'locked' && (
                          <div className="pt-3 border-t">
                            <p className="text-sm text-gray-600 flex items-center">
                              <Lock className="h-4 w-4 mr-2" />
                              Complete previous module to unlock
                            </p>
                          </div>
                        )}
                        
                        {isClickable && (
                          <Button className="w-full mt-4" variant={status === 'completed' ? 'outline' : 'default'}>
                            {status === 'completed' ? 'Review Module' : 'Start Module'}
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CourseLearningPage;