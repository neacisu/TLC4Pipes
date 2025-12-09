import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "@/components/common/Layout";
import OrderEntryPage from "@/pages/OrderEntryPage/OrderEntryPage";
import ResultsDashboard from "@/pages/ResultsDashboard/ResultsDashboard";
import TruckConfigsPage from "@/pages/TruckConfigsPage/TruckConfigsPage";
import SettingsPage from "@/pages/SettingsPage/SettingsPage";
import DashboardPage from "@/pages/DashboardPage/DashboardPage";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route index element={<DashboardPage />} />
                    <Route path="orders/new" element={<OrderEntryPage />} />
                    <Route path="orders/:orderId" element={<OrderEntryPage />} />
                    <Route path="orders/:orderId/edit" element={<OrderEntryPage />} />
                    <Route path="results" element={<ResultsDashboard />} />
                    <Route path="trucks" element={<TruckConfigsPage />} />
                    <Route path="settings" element={<SettingsPage />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App;
