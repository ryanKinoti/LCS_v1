import {BrowserRouter as Router, Routes, Route} from "react-router-dom";
import HomePage from "@/pages/HomePage";
import NotFound from "@/pages/NotFound";
import LoginPage from "@/pages/auth/Login";
import Registration from "@/pages/auth/Registration";
import {AuthProvider} from "@/contexts/AuthContext";
import {ProtectedRoute} from "@/components/ProtectedRoute";
import AdminDashboard from "@/pages/dashboard/AdminDashboard.tsx";

function App() {

    return (
        <AuthProvider>
            <Router>
                <Routes>
                    {/*Public Routes*/}
                    <Route path="/" element={<HomePage/>}/>
                    <Route path="/login" element={<LoginPage/>}/>
                    <Route path="/register" element={<Registration/>}/>

                    <Route path="/admin/*" element={
                        <ProtectedRoute allowedRoles={['admin']}>
                            <AdminDashboard/>
                        </ProtectedRoute>
                    }/>

                    <Route path="*" element={<NotFound/>}/>
                </Routes>
            </Router>
        </AuthProvider>
    )
}

export default App
