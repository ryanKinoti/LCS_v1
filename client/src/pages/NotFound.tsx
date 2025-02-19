import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import logoMain from "@/assets/lcs_main_logo.png"

const NotFound = () => {
    return (
        <div className="min-h-screen bg-[#F4F6F8] flex flex-col items-center justify-center px-4">
            <div className="w-full max-w-lg text-center space-y-6">
                <Link to="/" className="inline-block">
                    <img src={logoMain || "/placeholder.svg"} alt="Laptop Care" className="h-16 mx-auto" />
                </Link>

                <div className="space-y-4">
                    <h1 className="text-6xl font-bold text-[#111517]">404</h1>
                    <h2 className="text-2xl font-bold text-[#111517]">Page Not Found</h2>
                    <p className="text-[#647987] max-w-md mx-auto">
                        The page you're looking for doesn't exist or has been moved. Please check the URL or return to our homepage.
                    </p>
                </div>

                <div className="flex justify-center gap-4">
                    <Button variant="default" className="bg-[#0066FF] hover:bg-blue-700" asChild>
                        <Link to="/">Return Home</Link>
                    </Button>
                    <Button variant="outline" className="border-[#0066FF] text-[#0066FF] hover:bg-blue-50" asChild>
                        <Link to="/contact">Contact Support</Link>
                    </Button>
                </div>
            </div>
        </div>
    )
}

export default NotFound