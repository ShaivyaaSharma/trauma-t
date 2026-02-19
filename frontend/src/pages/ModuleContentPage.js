import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { toast } from 'sonner';
import { 
  ArrowLeft, 
  BookOpen, 
  CheckCircle2, 
  Target, 
  Clock,
  Award,
  RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import QuizComponent from '@/components/QuizComponent';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const ModuleContentPage = () => {
  const { courseId, moduleId } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [module, setModule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('content');

  useEffect(() => {
    if (token && courseId && moduleId) {
      fetchModule();
    }
  }, [token, courseId, moduleId]);

  const fetchModule = async () => {
    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.get(`${API_URL}/api/courses/${courseId}/modules/${moduleId}`, { headers });
      setModule(res.data);
    } catch (error) {
      console.error('Error fetching module:', error);
      if (error.response?.status === 403) {
        toast.error(error.response.data.detail || 'Module is locked');
        navigate(`/courses/${courseId}/learn`);
      } else {
        toast.error('Failed to load module content');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleQuizComplete = () => {
    fetchModule();
    setActiveTab('content');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!module) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-gray-600">Module not found</p>
          <Button onClick={() => navigate(`/courses/${courseId}/learn`)} className="mt-4">
            Back to Course
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => navigate(`/courses/${courseId}/learn`)}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Course
          </Button>
          
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Badge variant="outline">Week {module.week}</Badge>
                <Badge variant="outline">Module {module.module_number}</Badge>
                {module.progress?.is_completed && (
                  <Badge className="bg-green-600">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    Completed
                  </Badge>
                )}
              </div>
              <h1 className="text-3xl font-bold text-gray-900">{module.title}</h1>
              <p className="text-gray-600 mt-2">{module.description}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-6 mt-4 text-sm text-gray-600">
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-2" />
              {module.estimated_time}
            </div>
            {module.progress?.quiz_attempts > 0 && (
              <div className="flex items-center">
                <RefreshCw className="h-4 w-4 mr-2" />
                {module.progress.quiz_attempts} attempt{module.progress.quiz_attempts !== 1 ? 's' : ''}
              </div>
            )}
            {module.progress?.best_score > 0 && (
              <div className="flex items-center">
                <Award className="h-4 w-4 mr-2" />
                Best Score: {(module.progress.best_score * 100).toFixed(0)}%
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="content">
              <BookOpen className="h-4 w-4 mr-2" />
              Module Content
            </TabsTrigger>
            <TabsTrigger value="assessment">
              <Target className="h-4 w-4 mr-2" />
              Assessment
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="content" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Learning Objectives</CardTitle>
                <CardDescription>
                  By the end of this module, you will be able to:
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {module.learning_objectives?.map((objective, index) => (
                    <li key={index} className="flex items-start">
                      <CheckCircle2 className="h-5 w-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{objective}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
            
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Topics Covered</CardTitle>
                <CardDescription>
                  Key concepts and themes in this module
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {module.topics_covered?.map((topic, index) => (
                    <li key={index} className="flex items-start">
                      <div className="h-2 w-2 bg-primary rounded-full mr-3 mt-2 flex-shrink-0"></div>
                      <span className="text-gray-700">{topic}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
            
            <div className="mt-6 p-6 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Ready to Test Your Knowledge?
              </h3>
              <p className="text-gray-700 mb-4">
                Once you've reviewed the content, take the assessment to demonstrate your understanding. 
                You need to score at least {(module.assessment?.passing_score * 100)}% to pass and unlock the next module.
              </p>
              <Button onClick={() => setActiveTab('assessment')}>
                Start Assessment
              </Button>
            </div>
          </TabsContent>
          
          <TabsContent value="assessment" className="mt-6">
            <QuizComponent 
              courseId={courseId} 
              moduleId={moduleId}
              onComplete={handleQuizComplete}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ModuleContentPage;