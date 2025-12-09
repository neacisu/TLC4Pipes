import { useState } from "react";
import { useLocation, Navigate, Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Truck, Package, Weight, AlertTriangle, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { toast } from "sonner";
import TruckView3D, { getNestingColor } from "@/components/visualization/TruckView3D.jsx";
import { orderService } from "@/services/orderService";

export default function ResultsDashboard() {
    const location = useLocation();
    const navigate = useNavigate();
    const result = location.state?.result;
    const orderId = location.state?.orderId;
    const orderNumber = location.state?.orderNumber;
    const [isValidating, setIsValidating] = useState(false);
    const [isValidated, setIsValidated] = useState(false);

    if (!result) {
        return <Navigate to="/orders/new" replace />;
    }

    const handleValidate = async () => {
        if (!orderId) {
            toast.error("Order ID missing - cannot validate");
            return;
        }

        try {
            setIsValidating(true);
            await orderService.updateStatus(orderId, "calculated");
            setIsValidated(true);
            toast.success(`Order ${orderNumber || orderId} validated successfully!`);
        } catch (error) {
            console.error("Validation failed:", error);
            toast.error("Failed to validate order: " + (error.response?.data?.detail || error.message));
        } finally {
            setIsValidating(false);
        }
    };

    const handleBackToDashboard = () => {
        navigate("/");
    };

    const { summary = {}, nesting_stats = {}, weight_limits = {}, trucks = [], warnings = [] } = result;
    
    // Normalize field names for compatibility
    const totalItems = summary.total_items ?? summary.total_pipes ?? 0;
    const trucksCount = summary.trucks_count ?? summary.trucks_needed ?? trucks.length;
    const nestedPipes = nesting_stats.nested_pipes ?? nesting_stats.bundles_with_nesting ?? 0;
    const nestingEfficiency = nesting_stats.nesting_efficiency_percent ?? nesting_stats.estimated_space_reduction_pct ?? 0;
    
    // Calculate remaining capacity in trucks for recommendations
    const truckCapacities = trucks.map((truck, idx) => {
        const currentPayload = truck.current_payload_kg ?? truck.total_weight_kg ?? 0;
        const maxPayload = truck.max_payload_kg ?? 24000;
        const remaining = maxPayload - currentPayload;
        return { truckNumber: idx + 1, remaining, currentPayload, maxPayload };
    });
    
    // Find trucks with significant remaining capacity (>500kg)
    const trucksWithSpace = truckCapacities.filter(t => t.remaining > 500);
    
    // Generate packing list summary per truck (grouped by pipe code) with nesting level info
    const generatePackingList = (truck) => {
        const pipeGroups = {};
        if (!truck.bundles) return [];
        
        truck.bundles.forEach(bundle => {
            // Count outer pipe (level 0)
            const outerCode = bundle.outer_pipe?.code || 'Unknown';
            const outerDn = bundle.outer_pipe?.dn_mm || bundle.outer_pipe?.outer_diameter_mm;
            const key = outerCode;
            if (!pipeGroups[key]) {
                pipeGroups[key] = { code: outerCode, dn: outerDn, count: 0, weight: 0, nestingLevel: 0 };
            }
            pipeGroups[key].count += 1;
            pipeGroups[key].weight += (bundle.outer_pipe?.weight_per_meter || 0) * (result.pipe_length_m || 12);
            
            // Count nested pipes recursively with level tracking
            const countNested = (nestedList, level = 1) => {
                if (!nestedList) return;
                nestedList.forEach(nested => {
                    const nestedCode = nested.outer_pipe?.code || 'Unknown';
                    const nestedDn = nested.outer_pipe?.dn_mm || nested.outer_pipe?.outer_diameter_mm;
                    const nestedKey = nestedCode;
                    if (!pipeGroups[nestedKey]) {
                        pipeGroups[nestedKey] = { code: nestedCode, dn: nestedDn, count: 0, weight: 0, nestingLevel: level };
                    }
                    pipeGroups[nestedKey].count += 1;
                    pipeGroups[nestedKey].weight += (nested.outer_pipe?.weight_per_meter || 0) * (result.pipe_length_m || 12);
                    // Recurse with incremented level
                    if (nested.nested_pipes) {
                        countNested(nested.nested_pipes, level + 1);
                    }
                });
            };
            countNested(bundle.nested_pipes, 1);
        });
        
        // Convert to array sorted by DN descending
        return Object.values(pipeGroups).sort((a, b) => (b.dn || 0) - (a.dn || 0));
    };

    // Generate nesting configurations for the loading team
    const generateNestingConfigurations = (truck) => {
        const nestingGroups = {};
        if (!truck.bundles) return [];
        
        truck.bundles.forEach(bundle => {
            // Build the nesting chain for this bundle
            const chain = [];
            
            // Add outer pipe
            const outerDn = bundle.outer_pipe?.dn_mm || bundle.outer_pipe?.outer_diameter_mm;
            if (outerDn) chain.push(outerDn);
            
            // Recursively collect nested DNs
            const collectChain = (nestedList) => {
                if (!nestedList || nestedList.length === 0) return;
                nestedList.forEach(nested => {
                    const nestedDn = nested.outer_pipe?.dn_mm || nested.outer_pipe?.outer_diameter_mm;
                    if (nestedDn) chain.push(nestedDn);
                    if (nested.nested_pipes) {
                        collectChain(nested.nested_pipes);
                    }
                });
            };
            collectChain(bundle.nested_pipes);
            
            // Create a key from the chain (e.g., "280→225→180")
            const chainKey = chain.join(' → ');
            if (!nestingGroups[chainKey]) {
                nestingGroups[chainKey] = { 
                    chain: chain, 
                    chainString: chainKey, 
                    count: 0,
                    levels: chain.length 
                };
            }
            nestingGroups[chainKey].count += 1;
        });
        
        // Convert to array sorted by number of levels descending, then by count
        return Object.values(nestingGroups).sort((a, b) => {
            if (b.levels !== a.levels) return b.levels - a.levels;
            return b.count - a.count;
        });
    };

    return (
        <div className="space-y-6 container mx-auto max-w-7xl">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <Link to={orderId ? `/orders/${orderId}/edit` : "/orders/new"}>
                        <Button variant="outline" size="icon">
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                    </Link>
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Loading Plan</h1>
                        <p className="text-muted-foreground">
                            {orderNumber && `Order #${orderNumber} - `}
                            Optimized distribution across {trucks.length} truck(s).
                        </p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={() => window.print()}>Export PDF</Button>
                    {isValidated ? (
                        <Button variant="default" disabled className="bg-green-600">
                            <CheckCircle className="mr-2 h-4 w-4" /> Validated
                        </Button>
                    ) : (
                        <Button 
                            variant="default" 
                            onClick={handleValidate} 
                            disabled={isValidating}
                            className="bg-green-600 hover:bg-green-700"
                        >
                            <CheckCircle className="mr-2 h-4 w-4" />
                            {isValidating ? "Validating..." : "Validate & Save"}
                        </Button>
                    )}
                    {isValidated && (
                        <Button variant="secondary" onClick={handleBackToDashboard}>
                            Back to Dashboard
                        </Button>
                    )}
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatsCard
                    title="Total Items"
                    value={totalItems}
                    icon={Package}
                    subtext={`${nestedPipes} nested inside others`}
                />
                <StatsCard
                    title="Total Weight"
                    value={`${((summary.total_weight_kg ?? 0) / 1000).toFixed(2)} t`}
                    icon={Weight}
                    subtext={`Vs Max ${trucks.length * 24}t`}
                />
                <StatsCard
                    title="Trucks Used"
                    value={trucksCount}
                    icon={Truck}
                    subtext="optimized"
                />
                <StatsCard
                    title="Efficiency"
                    value={`${nestingEfficiency}%`}
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
            
            {/* Remaining Capacity Recommendation */}
            {trucksWithSpace.length > 0 && (
                <Alert variant="default" className="border-blue-500 bg-blue-50 dark:bg-blue-950">
                    <Package className="h-4 w-4 text-blue-600" />
                    <AlertTitle className="text-blue-800 dark:text-blue-200">Optimizare Transport</AlertTitle>
                    <AlertDescription className="text-blue-700 dark:text-blue-300">
                        {trucksWithSpace.map((t, i) => (
                            <p key={i}>
                                <strong>Camion #{t.truckNumber}</strong>: Mai este loc pentru <strong>{t.remaining.toLocaleString()} kg</strong>.
                                {' '}Recomandăm adăugarea de țevi suplimentare pentru a optimiza costurile de transport.
                            </p>
                        ))}
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
                                                <span className="font-bold">
                                                    {(truck.current_payload_kg ?? truck.total_weight_kg ?? 0).toLocaleString()} kg / {(truck.max_payload_kg ?? 24000).toLocaleString()} kg
                                                </span>
                                            </div>
                                            {/* Packing List - grouped by pipe type */}
                                            <div className="border rounded p-2 h-[300px] overflow-y-auto bg-muted/20 text-sm">
                                                {(() => {
                                                    const packingList = generatePackingList(truck);
                                                    if (packingList.length === 0) {
                                                        return <p className="text-muted-foreground italic">No items loaded</p>;
                                                    }
                                                    return (
                                                        <>
                                                            <div className="font-semibold mb-2 text-xs uppercase text-muted-foreground">Packing List</div>
                                                            <table className="w-full">
                                                                <thead>
                                                                    <tr className="border-b text-xs text-muted-foreground">
                                                                        <th className="text-left py-1">Cod Țeavă</th>
                                                                        <th className="text-center py-1">DN</th>
                                                                        <th className="text-right py-1">Buc.</th>
                                                                        <th className="text-right py-1">Greutate</th>
                                                                    </tr>
                                                                </thead>
                                                                <tbody>
                                                                    {packingList.map((item, pIdx) => (
                                                                        <tr key={pIdx} className="border-b last:border-b-0">
                                                                            <td className="py-1 font-medium flex items-center gap-2">
                                                                                <span 
                                                                                    className="inline-block w-3 h-3 rounded-full flex-shrink-0"
                                                                                    style={{ backgroundColor: getNestingColor(item.nestingLevel) }}
                                                                                    title={`Nesting Level ${item.nestingLevel}`}
                                                                                />
                                                                                {item.code}
                                                                            </td>
                                                                            <td className="py-1 text-center">{item.dn} mm</td>
                                                                            <td className="py-1 text-right">{item.count}</td>
                                                                            <td className="py-1 text-right">{item.weight.toFixed(0)} kg</td>
                                                                        </tr>
                                                                    ))}
                                                                </tbody>
                                                                <tfoot>
                                                                    <tr className="border-t font-semibold">
                                                                        <td colSpan="2" className="py-1">Total</td>
                                                                        <td className="py-1 text-right">{packingList.reduce((sum, i) => sum + i.count, 0)}</td>
                                                                        <td className="py-1 text-right">{packingList.reduce((sum, i) => sum + i.weight, 0).toFixed(0)} kg</td>
                                                                    </tr>
                                                                </tfoot>
                                                            </table>
                                                        </>
                                                    );
                                                })()}
                                            </div>
                                            
                                            {/* Nesting Configurations - for loading team */}
                                            <div className="border rounded p-2 max-h-[200px] overflow-y-auto bg-muted/20 text-sm mt-3">
                                                {(() => {
                                                    const nestingConfigs = generateNestingConfigurations(truck);
                                                    if (nestingConfigs.length === 0) {
                                                        return <p className="text-muted-foreground italic">No nesting configurations</p>;
                                                    }
                                                    return (
                                                        <>
                                                            <div className="font-semibold mb-2 text-xs uppercase text-muted-foreground">
                                                                🔧 Instrucțiuni Telescopare
                                                            </div>
                                                            <div className="space-y-2">
                                                                {nestingConfigs.map((config, nIdx) => (
                                                                    <div key={nIdx} className="flex items-center justify-between p-2 bg-background rounded border">
                                                                        <div className="flex items-center gap-2 flex-wrap">
                                                                            <span className="font-bold text-xs text-muted-foreground">
                                                                                #{nIdx + 1}
                                                                            </span>
                                                                            {config.chain.map((dn, dnIdx) => (
                                                                                <span key={dnIdx} className="flex items-center gap-1">
                                                                                    <span 
                                                                                        className="inline-block w-3 h-3 rounded-full"
                                                                                        style={{ backgroundColor: getNestingColor(dnIdx) }}
                                                                                    />
                                                                                    <span className="font-medium">DN{dn}</span>
                                                                                    {dnIdx < config.chain.length - 1 && (
                                                                                        <span className="text-muted-foreground mx-1">→</span>
                                                                                    )}
                                                                                </span>
                                                                            ))}
                                                                        </div>
                                                                        <span className="font-bold text-primary whitespace-nowrap ml-2">
                                                                            {config.count} buc
                                                                        </span>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                            <div className="mt-2 text-xs text-muted-foreground italic">
                                                                Introduceți țevile interioare în țeava exterioară în ordinea indicată de săgeți.
                                                            </div>
                                                        </>
                                                    );
                                                })()}
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
