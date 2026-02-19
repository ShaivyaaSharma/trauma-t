import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { toast } from 'sonner';
import { 
  CheckCircle2, 
  XCircle, 
  Award, 
  AlertCircle,
  RefreshCw,
  TrendingUp
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const QuizComponent = ({ courseId, moduleId, onComplete }) => {
  const { token } = useAuth();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchQuiz();
  }, [courseId, moduleId]);

  const fetchQuiz = async () => {
    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.get(
        `${API_URL}/api/courses/${courseId}/modules/${moduleId}/quiz`,
        { headers }
      );
      setQuiz(res.data);
      setAnswers({});
      setResult(null);
    } catch (error) {
      console.error('Error fetching quiz:', error);
      toast.error('Failed to load quiz');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionIndex, optionIndex) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: optionIndex
    }));
  };

  const handleSubmit = async () => {
    // Validate all questions are answered
    if (Object.keys(answers).length !== quiz.questions.length) {
      toast.error('Please answer all questions before submitting');
      return;
    }

    try {
      setSubmitting(true);
      const headers = { Authorization: `Bearer ${token}` };
      
      // Convert answers object to array
      const answersArray = quiz.questions.map((_, index) => answers[index] ?? -1);
      
      const res = await axios.post(
        `${API_URL}/api/courses/${courseId}/modules/${moduleId}/submit-quiz`,
        { module_id: moduleId, answers: answersArray },
        { headers }
      );
      
      setResult(res.data);
      
      if (res.data.passed) {
        toast.success(`Congratulations! You passed with ${(res.data.score * 100).toFixed(0)}%`);
      } else {
        toast.error(`You scored ${(res.data.score * 100).toFixed(0)}%. You need ${(quiz.passing_score * 100)}% to pass.`);
      }
    } catch (error) {
      console.error('Error submitting quiz:', error);
      toast.error('Failed to submit quiz');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRetry = () => {
    setAnswers({});
    setResult(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!quiz) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No quiz available for this module</p>
        </CardContent>
      </Card>
    );
  }

  // Show results
  if (result) {
    return (
      <div className="space-y-6">
        {/* Results Summary */}
        <Card className={result.passed ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center space-x-2">
                  {result.passed ? (
                    <CheckCircle2 className="h-6 w-6 text-green-600" />
                  ) : (
                    <XCircle className="h-6 w-6 text-red-600" />
                  )}
                  <span>{result.passed ? 'Assessment Passed!' : 'Assessment Not Passed'}</span>
                </CardTitle>
                <CardDescription className="mt-2">
                  You scored {result.correct_answers} out of {result.total_questions} questions correctly
                </CardDescription>
              </div>
              <div className="text-right">
                <div className="text-4xl font-bold">
                  {(result.score * 100).toFixed(0)}%
                </div>
                <Badge className={result.passed ? 'bg-green-600' : 'bg-red-600'}>
                  {result.passed ? 'Passed' : 'Failed'}
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Progress value={result.score * 100} className="h-3" />
            <div className="flex justify-between text-sm text-gray-600 mt-2">
              <span>Passing Score: {(quiz.passing_score * 100)}%</span>
              <span>Your Score: {(result.score * 100).toFixed(0)}%</span>
            </div>
          </CardContent>
        </Card>

        {/* Previous Attempts Info */}
        {quiz.attempts > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                <TrendingUp className="h-5 w-5 mr-2" />
                Your Progress
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-600">Total Attempts</div>
                  <div className="text-2xl font-bold">{quiz.attempts + 1}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Best Score</div>
                  <div className="text-2xl font-bold">
                    {Math.max((quiz.best_score * 100), (result.score * 100)).toFixed(0)}%
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Detailed Review */}
        <Card>
          <CardHeader>
            <CardTitle>Detailed Review</CardTitle>
            <CardDescription>Review your answers and learn from explanations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {result.questions_review.map((review, index) => (
              <div 
                key={index} 
                className={`p-4 rounded-lg border-2 ${
                  review.is_correct ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <Badge variant="outline">Question {review.question_number}</Badge>
                      {review.is_correct ? (
                        <Badge className="bg-green-600">Correct</Badge>
                      ) : (
                        <Badge className="bg-red-600">Incorrect</Badge>
                      )}
                    </div>
                    <p className="font-semibold text-gray-900">{review.question}</p>
                  </div>
                  {review.is_correct ? (
                    <CheckCircle2 className="h-6 w-6 text-green-600 flex-shrink-0" />
                  ) : (
                    <XCircle className="h-6 w-6 text-red-600 flex-shrink-0" />
                  )}
                </div>
                
                <div className="space-y-2 mt-3">
                  <div className="flex items-start">
                    <span className="text-sm font-medium text-gray-600 mr-2">Your answer:</span>
                    <span className={`text-sm ${
                      review.is_correct ? 'text-green-700' : 'text-red-700'
                    }`}>
                      {review.user_answer}
                    </span>
                  </div>
                  
                  {!review.is_correct && (
                    <div className="flex items-start">
                      <span className="text-sm font-medium text-gray-600 mr-2">Correct answer:</span>
                      <span className="text-sm text-green-700">{review.correct_answer}</span>
                    </div>
                  )}
                  
                  {review.explanation && (
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-sm text-gray-700">
                        <span className="font-medium">Explanation:</span> {review.explanation}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-between">
          <Button variant="outline" onClick={handleRetry}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry Quiz
          </Button>
          <Button onClick={onComplete}>
            {result.passed ? 'Continue to Next Module' : 'Back to Module'}
          </Button>
        </div>
      </div>
    );
  }

  // Show quiz questions
  return (
    <div className="space-y-6">
      {/* Quiz Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Award className="h-5 w-5 mr-2" />
            {quiz.module_title} - Assessment
          </CardTitle>
          <CardDescription>
            Answer all questions to test your understanding. You need {(quiz.passing_score * 100)}% to pass.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-sm text-gray-600">Questions</div>
              <div className="text-2xl font-bold">{quiz.questions.length}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Passing Score</div>
              <div className="text-2xl font-bold">{(quiz.passing_score * 100)}%</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Attempts</div>
              <div className="text-2xl font-bold">{quiz.attempts}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Questions */}
      {quiz.questions.map((question, index) => (
        <Card key={question.id}>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <Badge variant="outline" className="mb-2">Question {index + 1}</Badge>
                <CardTitle className="text-lg">{question.question}</CardTitle>
              </div>
              {answers[index] !== undefined && (
                <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
              )}
            </div>
          </CardHeader>
          <CardContent>
            <RadioGroup
              value={answers[index]?.toString()}
              onValueChange={(value) => handleAnswerChange(index, parseInt(value))}
            >
              <div className="space-y-3">
                {question.options.map((option, optIndex) => (
                  <div key={optIndex} className="flex items-center space-x-3">
                    <RadioGroupItem value={optIndex.toString()} id={`q${index}-opt${optIndex}`} />
                    <Label 
                      htmlFor={`q${index}-opt${optIndex}`}
                      className="flex-1 cursor-pointer py-2"
                    >
                      {option}
                    </Label>
                  </div>
                ))}
              </div>
            </RadioGroup>
          </CardContent>
        </Card>
      ))}

      {/* Submit Button */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          {Object.keys(answers).length} of {quiz.questions.length} questions answered
        </div>
        <Button 
          onClick={handleSubmit} 
          disabled={submitting || Object.keys(answers).length !== quiz.questions.length}
          size="lg"
        >
          {submitting ? 'Submitting...' : 'Submit Assessment'}
        </Button>
      </div>
    </div>
  );
};

export default QuizComponent;