import { Outlet, Link, useLocation } from "react-router-dom";
import {
    LayoutDashboard,
    PackagePlus,
    Truck,
    Settings,
    Menu
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Toaster } from "@/components/ui/sonner";
import { cn } from "@/lib/utils";

const sidebarItems = [
    { icon: LayoutDashboard, label: "Dashboard", href: "/" },
    { icon: PackagePlus, label: "New Order", href: "/orders/new" },
    { icon: Truck, label: "Truck Configs", href: "/trucks" },
    { icon: Settings, label: "Settings", href: "/settings" },
];

export default function Layout() {
    const location = useLocation();

    return (
        <div className="min-h-screen bg-background font-sans antialiased">
            {/* Mobile Header */}
            <div className="flex items-center p-4 border-b md:hidden">
                <Sheet>
                    <SheetTrigger asChild>
                        <Button variant="ghost" size="icon">
                            <Menu className="h-6 w-6" />
                        </Button>
                    </SheetTrigger>
                    <SheetContent side="left" className="w-64 p-0">
                        <SidebarContent location={location} />
                    </SheetContent>
                </Sheet>
                <span className="font-bold text-lg ml-4">TLC4Pipe</span>
            </div>

            <div className="flex h-screen overflow-hidden">
                {/* Desktop Sidebar */}
                <aside className="hidden md:flex w-64 flex-col border-r bg-card text-card-foreground">
                    <SidebarContent location={location} />
                </aside>

                {/* Main Content */}
                <main className="flex-1 overflow-y-auto p-4 md:p-8 bg-muted/20">
                    <Outlet />
                </main>
            </div>
            <Toaster />
        </div>
    );
}

function SidebarContent({ location }) {
    return (
        <div className="flex flex-col h-full">
            <div className="p-6 border-b">
                <h1 className="text-2xl font-bold tracking-tight text-primary">TLC4Pipe</h1>
                <p className="text-sm text-muted-foreground">Load Calculator</p>
            </div>
            <nav className="flex-1 p-4 space-y-2">
                {sidebarItems.map((item) => {
                    const isActive = location.pathname === item.href;
                    return (
                        <Link key={item.href} to={item.href}>
                            <Button
                                variant={isActive ? "secondary" : "ghost"}
                                className={cn("w-full justify-start", isActive && "font-semibold")}
                            >
                                <item.icon className="mr-2 h-4 w-4" />
                                {item.label}
                            </Button>
                        </Link>
                    );
                })}
            </nav>
            <div className="p-4 border-t text-xs text-center text-muted-foreground">
                v1.0.0
            </div>
        </div>
    );
}
