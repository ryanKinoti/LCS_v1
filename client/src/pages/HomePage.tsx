import React from "react"
import logoMain from '@/assets/lcs_main_logo.png'
import Navigation from '@/components/ui/navigation';
import {Button} from "@/components/ui/button"
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card"
import {Laptop, Wrench, Clock, Search, Truck, Copy, CreditCard, Smartphone, Tablet} from "lucide-react"

const HomePage: React.FC = () => {
    return (
        <div className="min-h-screen bg-white">
            {/* Header */}
            <Navigation logoSrc={logoMain} />

            <main>
                {/* Hero Section */}
                <section className="px-40 py-5">
                    <div className="flex flex-col max-w-[960px] mx-auto">
                        <div
                            className="min-h-[480px] rounded-xl bg-cover bg-center p-10 flex flex-col justify-end gap-6"
                            style={{
                                backgroundImage: `
                  linear-gradient(
                    to bottom,
                    rgba(0, 102, 255, 0.1),
                    rgba(0, 64, 133, 0.85)
                  ),
                  url("/src/assets/device_repair.jpg")
                `,
                                backgroundPosition: 'center',
                                backgroundSize: 'cover'
                            }}>
                            <div className="flex flex-col gap-2">
                                <h1 className="text-5xl font-black text-white tracking-tight">
                                    Fast, reliable tech repair
                                </h1>
                                <p className="text-base text-white">
                                    We fix all devices, including laptops, phones, and tablets. Most repairs done in
                                    under an hour.
                                </p>
                            </div>
                            <div className="flex w-full max-w-[480px]">
                                <div className="flex w-full items-center rounded-xl bg-white">
                                    <div className="pl-4">
                                        <Search className="text-[#647987]"/>
                                    </div>
                                    <input
                                        placeholder="What do you need help with?"
                                        className="flex-1 border-none px-4 py-3 focus:ring-0"
                                    />
                                    <div className="pr-2">
                                        <Button>Get a Quote</Button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Services Grid */}
                <section id="services" className="py-20 px-4">
                    <div className="container mx-auto">
                        <h2 className="text-4xl font-bold mb-12 text-[#111517]">We fix all devices</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {services.map((service, index) => (
                                <ServiceCard key={index} {...service} />
                            ))}
                        </div>
                    </div>
                </section>

                {/* Why Choose Us */}
                <section id="why-us" className="bg-[#F4F6F8] py-20">
                    <div className="container mx-auto px-4">
                        <h2 className="text-3xl font-bold text-center mb-12">How it works</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                            {features.map((feature, index) => (
                                <FeatureCard key={index} {...feature} />
                            ))}
                        </div>
                    </div>
                </section>

                {/* Contact Section */}
                <section id="contact" className="py-20">
                    <div className="container mx-auto px-4 text-center">
                        <h2 className="text-3xl font-bold mb-8">Ready to get your device fixed?</h2>
                        <p className="text-xl mb-8">Most repairs completed same day!</p>
                        <Button size="lg" variant="default">Book a Repair</Button>
                    </div>
                </section>
            </main>

            <footer className="bg-[#111517] text-white py-8">
                <div className="container mx-auto px-4 text-center">
                    <p>&copy; {new Date().getFullYear()} Laptop Care. All rights reserved.</p>
                </div>
            </footer>
        </div>
    )
}

const ServiceCard: React.FC<{
    icon: React.ReactNode
    title: string
    description: string
}> = ({icon, title, description}) => (
    <Card className="flex flex-col gap-3">
        <CardHeader>
            <div className="aspect-video rounded-xl bg-[#F4F6F8] flex items-center justify-center">
                {icon}
            </div>
        </CardHeader>
        <CardContent>
            <CardTitle className="text-base font-medium mb-2">{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
        </CardContent>
    </Card>
)

const FeatureCard: React.FC<{
    icon: React.ReactNode
    title: string
    description: string
}> = ({icon, title, description}) => (
    <Card className="flex flex-col gap-3 p-4 border-[#dce1e5]">
        <div className="text-[#0066FF]">{icon}</div>
        <div>
            <CardTitle className="text-base font-bold mb-1">{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
        </div>
    </Card>
)

const services = [
    {
        icon: <Laptop className="w-12 h-12 text-[#0066FF]"/>,
        title: "Laptop Repair",
        description: "Screen repairs, hardware upgrades, and more"
    },
    {
        icon: <Smartphone className="w-12 h-12 text-[#0066FF]"/>,
        title: "Phone Repair",
        description: "Screen replacement, battery service, and water damage repair"
    },
    {
        icon: <Tablet className="w-12 h-12 text-[#0066FF]"/>,
        title: "Tablet Repair",
        description: "Screen repairs, charging issues, and battery replacement"
    },
    {
        icon: <Clock className="w-12 h-12 text-[#0066FF]"/>,
        title: "Quick Service",
        description: "Most repairs completed same day"
    }
]

const features = [
    {
        icon: <CreditCard className="w-6 h-6"/>,
        title: "Get a quote",
        description: "Tell us what's wrong with your device"
    },
    {
        icon: <Truck className="w-6 h-6"/>,
        title: "Drop off or mail in",
        description: "Choose your preferred drop-off method"
    },
    {
        icon: <Wrench className="w-6 h-6"/>,
        title: "We fix your device",
        description: "Our technicians will repair your device"
    },
    {
        icon: <Copy className="w-6 h-6"/>,
        title: "Quality check",
        description: "We ensure everything works perfectly"
    }
]

export default HomePage