import { useLocation, Navigate, Link } from "react-router-dom";
import { ArrowLeft, Truck, Package, Weight, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import TruckView3D from "@/components/visualization/TruckView3D.jsx";

export default function ResultsDashboard() {
    const location = useLocation();
    const result = location.state?.result;

    if (!result) {
        return <Navigate to="/orders/new" replace />;
    }

    const { summary, nesting_stats, weight_limits, trucks, warnings } = result;

    return (
        <div className="space-y-6 container mx-auto max-w-7xl">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <Link to="/orders/new">
                        <Button variant="outline" size="icon">
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                    </Link>
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Loading Plan</h1>
                        <p className="text-muted-foreground">Optimized distribution across {trucks.length} truck(s).</p>
                    </div>
                </div>
                <Button onClick={() => window.print()}>Export PDF</Button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatsCard
                    title="Total Items"
                    value={summary.total_items}
                    icon={Package}
                    subtext={`${nesting_stats.nested_pipes} nested inside others`}
                />
                <StatsCard
                    title="Total Weight"
                    value={`${(summary.total_weight_kg / 1000).toFixed(2)} t`}
                    icon={Weight}
                    subtext={`Vs Max ${trucks.length * 24}t`}
                />
                <StatsCard
                    title="Trucks Used"
                    value={summary.trucks_count}
                    icon={Truck}
                    subtext="optimized"
                />
                <StatsCard
                    title="Efficiency"
                    value={`${nesting_stats.nesting_efficiency_percent}%`}
                    icon={CalculatorIcon}
                    subtext="volume reduction"
                />
            </div>

            {/* Warnings */}
            {(warnings.length > 0 || weight_limits.is_overweight) && (
                <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertTitle>Attention Required</AlertTitle>
                    <AlertDescription>
                        {weight_limits.is_overweight && <p>Total weight exceeds legal limits per truck.</p>}
                        {warnings.map((w, i) => <p key={i}>{w}</p>)}
                    </AlertDescription>
                </Alert>
            )}

            {/* Main Content: Tabs for each truck */}
            <Tabs defaultValue="truck-0" className="w-full">
                <TabsList>
                    {trucks.map((truck, idx) => (
                        <TabsTrigger key={idx} value={`truck-${idx}`}>
                            Truck #{idx + 1}
                        </TabsTrigger>
                    ))}
                </TabsList>

                {trucks.map((truck, idx) => (
                    <TabsContent key={idx} value={`truck-${idx}`} className="space-y-4">
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            {/* 3D Visualization */}
                            <div className="lg:col-span-2">
                                <TruckView3D loadingPlan={truck} />
                            </div>

                            {/* Truck Manifest */}
                            <div>
                                <Card className="h-full">
                                    <CardHeader>
                                        <CardTitle>Manifest</CardTitle>
                                        <CardDescription>Items loaded in Truck #{idx + 1}</CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-4">
                                            <div className="flex justify-between text-sm">
                                                <span>Payload:</span>
                                                <span className="font-bold">{truck.current_payload_kg} kg / 24,000 kg</span>
                                            </div>
                                            {/* Simple list for now, ideally detailed list of bundles */}
                                            <div className="border rounded p-2 h-[300px] overflow-y-auto bg-muted/20 text-sm">
                                                {/* Manifest items would be mapped here */}
                                                <p className="text-muted-foreground italic">Bundle list...</p>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                        </div>
                    </TabsContent>
                ))}
            </Tabs>
        </div>
    );
}

function StatsCard({ title, value, icon: Icon, subtext }) {
    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{title}</CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{value}</div>
                <p className="text-xs text-muted-foreground">{subtext}</p>
            </CardContent>
        </Card>
    );
}

function CalculatorIcon(props) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <rect width="16" height="20" x="4" y="2" rx="2" />
            <line x1="8" x2="16" y1="6" y2="6" />
            <line x1="16" x2="16" y1="14" y2="18" />
            <path d="M16 10h.01" />
            <path d="M12 10h.01" />
            <path d="M8 10h.01" />
            <path d="M12 14h.01" />
            <path d="M8 14h.01" />
            <path d="M12 18h.01" />
            <path d="M8 18h.01" />
        </svg>
    )
}
