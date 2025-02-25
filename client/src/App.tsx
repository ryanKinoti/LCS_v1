import {BrowserRouter as Router, Routes, Route} from "react-router-dom";
import {AppProviders} from "./providers/AppProviders";
import {ProtectedRoute} from "@/contexts/ProtectedRoute";
import {UserRoleTypes} from "@/lib/types/constants/declarations";

import HomePage from "@/pages/HomePage";
import NotFound from "@/pages/NotFound";
import LoginPage from "@/pages/auth/Login";
import Registration from "@/pages/auth/Registration";
import AdminDashboard from "@/pages/dashboard/AdminDashboard";

function App() {

    return (
        <AppProviders>
            <Router>
                <Routes>
                    {/*Public Routes*/}
                    <Route path="/" element={<HomePage/>}/>
                    <Route path="/login" element={<LoginPage/>}/>
                    <Route path="/register" element={<Registration/>}/>

                    <Route path="/admin/*" element={
                        <ProtectedRoute allowedRoles={[UserRoleTypes.ADMIN]}>
                            <AdminDashboard/>
                        </ProtectedRoute>
                    }/>

                    <Route path="*" element={<NotFound/>}/>
                </Routes>
            </Router>
        </AppProviders>
    )
}

export default App
