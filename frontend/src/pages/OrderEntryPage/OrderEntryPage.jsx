import { useState } from "react";
import { Plus, Upload, Calculator } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
// import { useToast } from "@/components/ui/use-toast"; // Removed
import { toast } from "sonner"; // Direct import for sonner
import OrderGrid from "@/components/order/OrderGrid";
import { orderService } from "@/services/orderService";
import { calculationService } from "@/services/calculationService";
import { useNavigate } from "react-router-dom";

export default function OrderEntryPage() {
    const navigate = useNavigate();
    const [items, setItems] = useState([]);
    const [pipeLength, setPipeLength] = useState(12.0);
    const [isCalculating, setIsCalculating] = useState(false);

    const handleAddItem = (newItem) => {
        setItems((prev) => [...prev, { ...newItem, id: Date.now() }]); // simple client-side ID for now
    };

    const handleRemoveItem = (index) => {
        setItems((prev) => prev.filter((_, i) => i !== index));
    };

    const handleCalculate = async () => {
        if (items.length === 0) {
            toast.error("Please add at least one pipe to the order");
            return;
        }

        try {
            setIsCalculating(true);

            // 1. Create the order in DB first (Draft)
            const orderPayload = {
                pipe_length_m: parseFloat(pipeLength),
                items: items.map(item => ({
                    pipe_id: parseInt(item.pipeId),
                    quantity: parseInt(item.quantity)
                }))
            };

            const createdOrder = await orderService.createOrder(orderPayload);
            const orderId = createdOrder.order.id;
            toast.success(`Order #${createdOrder.order.order_number} created`);

            // 2. Perform calculation
            const requestPoints = items.map(item => ({
                pipe_id: parseInt(item.pipeId),
                quantity: parseInt(item.quantity)
            }));

            const response = await calculationService.optimize({
                items: requestPoints,
                pipe_length_m: parseFloat(pipeLength),
                enable_nesting: true,
                max_nesting_levels: 4
            });

            // 3. Update status to calculated
            await orderService.updateStatus(orderId, "calculated");

            // 4. Navigate to results with order context
            navigate(`/results?orderId=${orderId}`, {
                state: {
                    result: response,
                    orderId: orderId
                }
            });

        } catch (error) {
            console.error(error);
            let errMsg = error.message;
            if (error.response?.data?.detail) {
                const detail = error.response.data.detail;
                if (Array.isArray(detail)) {
                    // Pydantic validation error array
                    errMsg = detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('\n');
                } else if (typeof detail === 'object') {
                    errMsg = JSON.stringify(detail);
                } else {
                    errMsg = detail;
                }
            }
            toast.error("Process failed: " + errMsg);
        } finally {
            setIsCalculating(false);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const result = await orderService.importCsv(file, pipeLength);
            if (result.order && result.order.items) {
                // Transform backend items to frontend format
                const importedItems = result.order.items.map(i => ({
                    id: i.id,
                    pipeId: i.pipe_id,
                    code: i.pipe_details?.code || `Pipe ${i.pipe_id}`, // Fallback if details missing
                    quantity: i.quantity,
                    dn: i.pipe_details?.dn_mm,
                    pn: i.pipe_details?.pn_class
                }));
                setItems(prev => [...prev, ...importedItems]);
                toast.success(`Imported ${importedItems.length} items`);
            }
        } catch (err) {
            toast.error("Import failed: " + err.message);
        }
    };

    return (
        <div className="space-y-6 container mx-auto max-w-6xl">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">New Loading Order</h1>
                    <p className="text-muted-foreground">Define your pipe inventory to optimize loading.</p>
                </div>
                <div className="flex gap-2">
                    <div className="relative">
                        <input
                            type="file"
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            accept=".csv"
                            onChange={handleFileUpload}
                        />
                        <Button variant="outline">
                            <Upload className="mr-2 h-4 w-4" />
                            Import CSV
                        </Button>
                    </div>
                    <Button onClick={handleCalculate} disabled={isCalculating}>
                        <Calculator className="mr-2 h-4 w-4" />
                        {isCalculating ? "Optimizing..." : "Calculate Load"}
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Helper/Inputs Panel */}
                <Card className="md:col-span-1 h-fit">
                    <CardHeader>
                        <CardTitle>Settings</CardTitle>
                        <CardDescription>Global parameters for this order.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="length">Pipe Length (m)</Label>
                            <Input
                                id="length"
                                type="number"
                                value={pipeLength}
                                onChange={(e) => setPipeLength(e.target.value)}
                                min={6} max={18} step={0.5}
                            />
                        </div>
                        <Separator />
                        <div className="bg-muted p-4 rounded-md text-sm text-muted-foreground">
                            <p>Supported formats for CSV:</p>
                            <ul className="list-disc pl-4 mt-2 space-y-1">
                                <li>DN, PN, Quantity</li>
                                <li>Example: 200, PN6, 10</li>
                            </ul>
                        </div>
                    </CardContent>
                </Card>

                {/* Main Grid */}
                <Card className="md:col-span-2">
                    <CardHeader>
                        <CardTitle>Order Items</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <OrderGrid items={items} onRemove={handleRemoveItem} onAdd={handleAddItem} />
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
