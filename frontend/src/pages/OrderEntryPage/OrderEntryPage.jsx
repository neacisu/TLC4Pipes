import { useEffect, useState } from "react";
import { Upload, Calculator } from "lucide-react";
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
import { useNavigate, useLocation, useParams } from "react-router-dom";

export default function OrderEntryPage() {
    const navigate = useNavigate();
    const location = useLocation();
    const { orderId } = useParams();
    const [items, setItems] = useState([]);
    const [pipeLength, setPipeLength] = useState(12.0);
    const [isCalculating, setIsCalculating] = useState(false);
    const [draftOrder, setDraftOrder] = useState(null);

    const mapOrderItems = (orderItems = [], lengthMeters) => {
        return orderItems.map((item) => {
            const qty = item.quantity;
            // Use backend values if available, else compute for backwards compat
            const orderedMeters = item.ordered_meters ?? item.orderedMeters;
            const pipeCount = item.pipe_count ?? item.pipeCount ?? qty;
            const meters = orderedMeters ?? (qty && lengthMeters ? qty * parseFloat(lengthMeters) : undefined);
            return {
                id: item.id || item.item_id || item.pipe_id,
                pipeId: item.pipe_id ?? item.pipeId,
                code: item.pipe_details?.code || item.pipe_code || item.code || `Pipe ${item.pipe_id ?? item.pipeId}`,
                quantity: qty,
                orderedMeters,
                pipeCount,
                meters,
                dn: item.pipe_details?.dn_mm ?? item.dn_mm,
                pn: item.pipe_details?.pn_class ?? item.pn_class,
            };
        }).filter(Boolean);
    };

    const initializeFromOrder = (orderData) => {
        if (!orderData) return;
        setDraftOrder(orderData);
        if (orderData.pipe_length_m) {
            setPipeLength(parseFloat(orderData.pipe_length_m));
        }
        if (Array.isArray(orderData.items)) {
            const lengthMeters = orderData.pipe_length_m || pipeLength;
            setItems(mapOrderItems(orderData.items, lengthMeters));
        }
    };

    useEffect(() => {
        let isActive = true;

        const loadOrder = async () => {
            // When navigating from elsewhere with state
            if (!orderId && location.state?.order) {
                initializeFromOrder(location.state.order);
                return;
            }

            // Existing draft/edit path
            if (orderId) {
                try {
                    const response = await orderService.getOrder(orderId);
                    const fetchedOrder = response?.order ?? response;

                    if (!fetchedOrder) {
                        toast.error("Order not found");
                        navigate("/", { replace: true });
                        return;
                    }

                    if (fetchedOrder.status && fetchedOrder.status !== "draft") {
                        toast.error(`Order cannot be edited (status: ${fetchedOrder.status})`);
                        navigate("/", { replace: true });
                        return;
                    }

                    if (isActive) {
                        initializeFromOrder(fetchedOrder);
                    }
                    return;
                } catch (error) {
                    console.error(error);
                    toast.error("Failed to load order");
                    navigate("/", { replace: true });
                    return;
                }
            }

            // New draft scenario
            try {
                const created = await orderService.createOrder({
                    pipe_length_m: parseFloat(pipeLength),
                    items: [],
                });
                if (created?.order && isActive) {
                    setDraftOrder(created.order);
                }
            } catch (error) {
                console.error(error);
                toast.error("Failed to start a new order");
            }
        };

        loadOrder();

        return () => {
            isActive = false;
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [orderId, location.state, navigate]);

    const ensureDraftOrder = async () => {
        if (draftOrder?.id) return draftOrder;
        const created = await orderService.createOrder({
            pipe_length_m: parseFloat(pipeLength),
            items: [],
        });
        setDraftOrder(created.order);
        return created.order;
    };

    const handleAddItem = async (newItem) => {
        const length = parseFloat(pipeLength);
        if (!length || length <= 0) {
            toast.error("Invalid pipe length");
            return;
        }

        const requestedMeters = parseFloat(newItem.meters);
        if (!requestedMeters || requestedMeters <= 0) {
            toast.error("Introduce o cantitate in metri");
            return;
        }

        const pipeCount = Math.ceil(requestedMeters / length);
        const adjustedMeters = pipeCount * length;

        try {
            // Ensure we have a draft order
            const order = await ensureDraftOrder();

            // Save item to DB immediately
            const response = await orderService.addItem(order.id, {
                pipe_id: parseInt(newItem.pipeId),
                quantity: pipeCount,
                total_meters: requestedMeters,
            });

            // Add to local state with the DB id
            const savedItemId = response?.item?.id || Date.now();
            setItems((prev) => [
                ...prev,
                {
                    ...newItem,
                    id: savedItemId,
                    quantity: pipeCount,
                    orderedMeters: requestedMeters,
                    pipeCount,
                    meters: adjustedMeters,
                },
            ]);

            toast.success("Item added");
        } catch (error) {
            console.error("Failed to add item:", error);
            toast.error("Failed to add item: " + (error.response?.data?.detail || error.message));
        }
    };

    const handleRemoveItem = async (index) => {
        const item = items[index];
        if (!item) return;

        // Remove from local state immediately for responsive UI
        setItems((prev) => prev.filter((_, i) => i !== index));

        // If item has a DB id, delete from backend
        if (draftOrder?.id && item.id && typeof item.id === 'number') {
            try {
                await orderService.deleteItem(draftOrder.id, item.id);
            } catch (error) {
                console.error("Failed to delete item from DB:", error);
                // Optionally restore item on error
                toast.error("Failed to delete item from server");
            }
        }
    };

    const handleCalculate = async () => {
        if (items.length === 0) {
            toast.error("Please add at least one pipe to the order");
            return;
        }

        try {
            setIsCalculating(true);

            const order = await ensureDraftOrder();
            const orderId = order.id;

            // Verify items are saved by refreshing from DB
            const freshOrder = await orderService.getOrder(orderId);
            const savedItems = freshOrder?.items || [];

            if (savedItems.length !== items.length) {
                toast.warning(`Syncing items: ${items.length} local vs ${savedItems.length} saved`);
                // Items not yet saved - this shouldn't happen now but handle gracefully
                for (const item of items) {
                    const alreadySaved = savedItems.some(
                        (s) => s.pipe_id === parseInt(item.pipeId) && s.quantity === item.quantity
                    );
                    if (!alreadySaved) {
                        await orderService.addItem(orderId, {
                            pipe_id: parseInt(item.pipeId),
                            quantity: parseInt(item.quantity),
                            total_meters: item.orderedMeters || item.meters,
                        });
                    }
                }
            }

            toast.success(`Order #${order.order_number} - calculating with ${savedItems.length || items.length} items`);

            // 2. Perform calculation using saved items
            const itemsForCalc = savedItems.length > 0 ? savedItems : items;
            const requestPoints = itemsForCalc.map(item => ({
                pipe_id: parseInt(item.pipe_id ?? item.pipeId),
                quantity: parseInt(item.quantity)
            }));

            const response = await calculationService.optimize({
                items: requestPoints,
                pipe_length_m: parseFloat(pipeLength),
                enable_nesting: true,
                max_nesting_levels: 10
            });

            // Status stays as 'draft' until user validates in results page
            // await orderService.updateStatus(orderId, "calculated");

            // 4. Navigate to results with order context
            navigate(`/results?orderId=${orderId}`, {
                state: {
                    result: response,
                    orderId: orderId,
                    orderNumber: order.order_number
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
                const length = parseFloat(result.order.pipe_length_m || pipeLength);
                const importedItems = result.order.items.map(i => ({
                    id: i.id,
                    pipeId: i.pipe_id,
                    code: i.pipe_details?.code || `Pipe ${i.pipe_id}`, // Fallback if details missing
                    quantity: i.quantity,
                    meters: i.quantity && length ? i.quantity * length : undefined,
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
