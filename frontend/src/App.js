import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider, useAuth } from "@/context/AuthContext";

// Pages
import LandingPage from "@/pages/LandingPage";
import WellnessHomePage from "@/pages/WellnessHomePage";
import ClinicalHomePage from "@/pages/ClinicalHomePage";
import CourseDetailsPage from "@/pages/CourseDetailsPage";
import LoginPage from "@/pages/LoginPage";
import SignupPage from "@/pages/SignupPage";
import DashboardPage from "@/pages/DashboardPage";
import AboutPage from "@/pages/AboutPage";
import PaymentSuccessPage from "@/pages/PaymentSuccessPage";
import CourseLearningPage from "@/pages/CourseLearningPage";
import ModuleContentPage from "@/pages/ModuleContentPage";

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/wellness" element={<WellnessHomePage />} />
          <Route path="/clinical" element={<ClinicalHomePage />} />
          <Route path="/courses/:courseId" element={<CourseDetailsPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/payment-success" 
            element={
              <ProtectedRoute>
                <PaymentSuccessPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/courses/:courseId/learn" 
            element={
              <ProtectedRoute>
                <CourseLearningPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/courses/:courseId/modules/:moduleId" 
            element={
              <ProtectedRoute>
                <ModuleContentPage />
              </ProtectedRoute>
            } 
          />
        </Routes>
        <Toaster position="top-right" />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
